# backend/main.py

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import get_settings
from core.exceptions import BridgrException, bridgr_exception_handler
from routes import readiness, user

# Global flag to track when ML core is ready
_core_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    global _core_ready
    # STARTUP: initialize DB tables
    from db.database import engine
    from db import models
    models.Base.metadata.create_all(bind=engine)
    print("[OK] Database tables ensured.")
    print("[START] Starting Bridgr server...")
    _core_ready = True
    print("[READY] Bridgr is ready. ML models will load on first report.")
    yield
    # SHUTDOWN: nothing to clean up
    _core_ready = False


settings = get_settings()

app = FastAPI(
    title="Bridgr API",
    description="The bridge between who you are and who you want to become",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow your React frontend to call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handler
app.add_exception_handler(BridgrException, bridgr_exception_handler)

# Register MVP routes only
app.include_router(readiness.router, prefix="/api")
app.include_router(user.router,      prefix="/api")


@app.get("/")
def root():
    return {"message": "Bridgr API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "ready": _core_ready}
