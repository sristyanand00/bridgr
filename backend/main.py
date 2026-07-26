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
try:
    import spacy  # noqa: F401 — already installed, nothing to stub
except ImportError:
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
# ─────────────────────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import get_settings
from core.exceptions import BridgrException, bridgr_exception_handler
from routes import readiness, user

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_exception_handler(BridgrException, bridgr_exception_handler)

app.include_router(readiness.router, prefix="/api")
app.include_router(user.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Bridgr API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "ready": _core_ready}


@app.get("/debug/cors")
def debug_cors():
    """Debug endpoint to test CORS configuration"""
    return {
        "message": "CORS test successful", 
        "allowed_origins": _allowed_origins,
        "timestamp": "2026-07-26T10:22:39Z"
    }
