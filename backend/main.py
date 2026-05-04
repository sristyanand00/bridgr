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
from routes import analyze, chat, roadmap, market_pulse, interview, user

# Global flag to track when ML core is ready
_core_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    global _core_ready
    # STARTUP: Load ML models immediately to avoid first-request hang
    print("Starting Bridgr server...")
    print("Pre-loading ML models (this may take 30-60 seconds)...")
    try:
        # Load core in a background thread to not block the main thread
        import threading
        def load_models():
            global _core_ready
            try:
                get_core()
                _core_ready = True
                print("[OK] ML models loaded and ready!")
            except Exception as e:
                print(f"[ERROR] Failed to load ML models: {e}")
        
        thread = threading.Thread(target=load_models)
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