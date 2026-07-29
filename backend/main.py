# backend/main.py

import logging
import os
import sys
from contextlib import asynccontextmanager

# ── Stub ML packages unavailable on Python 3.14 ───────────────────────────────
# spacy, thinc, sentence-transformers, and torch do not yet have wheels for
# Python 3.14.  Stubbing them here (before any import that transitively needs
# them) lets the API server start and serve all routes.  The ML models load
# lazily on the first /api/readiness request via FallbackIntelligenceCore,
# which uses the built-in 50-occupation sample and requires none of these.

# WARNING: This stub should only trigger on Python 3.14+ where packages aren't available
# If you're seeing this on Python 3.11/3.12, there's likely a dependency installation issue
_ml_packages_stubbed = False
try:
    import spacy  # noqa: F401 — already installed, nothing to stub
except ImportError:
    _ml_packages_stubbed = True
    print("⚠️  WARNING: ML packages not available - using stubs!")
    print("   This should only happen on Python 3.14+ or if dependencies failed to install")
    print("   Resume analysis will use fallback logic with reduced accuracy")
    
    from unittest.mock import MagicMock
    for _m in [
        "spacy", "spacy.matcher", "spacy.util", "spacy.lang", "spacy.lang.en",
        "sentence_transformers",
        "sklearn", "sklearn.metrics", "sklearn.metrics.pairwise",
        "torch", "thinc",
        "google", "google.generativeai",
        "groq",
        "firebase_admin", "firebase_admin.credentials", "firebase_admin.auth",
    ]:
        if _m not in sys.modules:
            sys.modules[_m] = MagicMock()
    
    # Log this prominently in the server logs
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)
    logger.warning("ML dependencies stubbed - analysis accuracy will be reduced!")
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import get_settings
from core.exceptions import BridgrException, bridgr_exception_handler
from core.limiter import limiter
from core.logging_config import RequestIDMiddleware
from routes import readiness, user

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s [%(request_id)s]: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Global flag to track when ML core is ready
_core_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    global _core_ready
    from db.database import engine
    from db import models

    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")
    logger.info("Starting Bridgr server...")
    _core_ready = True
    logger.info("Bridgr is ready. ML models will load on first report.")
    yield
    _core_ready = False


settings = get_settings()

# CORS — explicit allowlist; "*" + credentials is forbidden by the CORS spec.
# Set ALLOWED_ORIGINS in .env as a comma-separated list for production.
_allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app = FastAPI(
    title="Bridgr API",
    description="The bridge between who you are and who you want to become",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── Request ID tracing ────────────────────────────────────────────────────────
app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    # Regex handles dynamic preview subdomains (Vercel, Netlify, Render).
    # CORSMiddleware ignores None, so clearing the setting disables regex matching.
    allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ── Security headers middleware ───────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds baseline security response headers to every response.

    X-Content-Type-Options: prevents MIME sniffing attacks.
    X-Frame-Options: prevents clickjacking via iframes.
    Referrer-Policy: limits referrer leakage to same-origin cross-origin requests.
    """
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.add_exception_handler(BridgrException, bridgr_exception_handler)

app.include_router(readiness.router, prefix="/api")
app.include_router(user.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Bridgr API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "ready": _core_ready}


# Debug CORS endpoint — only registered when DEBUG=true.
# render.yaml sets DEBUG=false for both services, so this route
# does not exist in production.
if settings.DEBUG:
    from datetime import datetime as _datetime

    @app.get("/debug/cors")
    def debug_cors():
        """Debug endpoint to verify CORS configuration."""
        return {
            "message": "CORS test successful",
            "allowed_origins": _allowed_origins,
            "allowed_origin_regex": settings.ALLOWED_ORIGIN_REGEX or None,
            "timestamp": _datetime.utcnow().isoformat(),
        }
