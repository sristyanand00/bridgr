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
from ml.model_loader import get_core
from routes import analyze, chat, roadmap, market_pulse, interview

# Global flag to track when ML core is ready
_core_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    global _core_ready
    # STARTUP: server starts without loading ML models
    print("🌉 Starting Bridgr server...")
    print("🚀 ML models will be loaded on-demand (lazy loading)")
    _core_ready = True  # Server is ready, ML loads when needed
    print("🌉 Bridgr is ready!")
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

# Register all routes
app.include_router(analyze.router,      prefix="/api")
app.include_router(chat.router,         prefix="/api")
app.include_router(roadmap.router,      prefix="/api")
app.include_router(market_pulse.router, prefix="/api")
app.include_router(interview.router,    prefix="/api")


@app.get("/")
def root():
    return {"message": "Bridgr API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok", "ready": _core_ready}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )