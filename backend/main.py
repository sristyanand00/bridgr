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
# ML imports deferred to speed up startup — loaded lazily on first request
# from ml.model_loader import get_core
from routes import analyze, chat, roadmap, market_pulse, interview, user

# Global flag to track when ML core is ready
_core_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    global _core_ready
    # STARTUP: Load ML models in background so port binds immediately
    print("Starting Bridgr server...")
    try:
        import threading
        def load_models():
            global _core_ready
            try:
                from ml.model_loader import get_core
                print("[ML] Pre-loading models (this may take 30-60s)...")
                get_core()
                _core_ready = True
                print("[OK] ML models loaded and ready!")
            except Exception as e:
                print(f"[ERROR] Failed to load ML models: {e}")
        
        thread = threading.Thread(target=load_models, daemon=True)
        thread.start()
        
    except Exception as e:
        print(f"Startup error: {e}")
    
    yield
    # SHUTDOWN
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
    allow_origins=settings.get_cors_origins(),
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
app.include_router(user.router,         prefix="/api")


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