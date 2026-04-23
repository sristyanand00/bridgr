# backend/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.core.exceptions import BridgrException, bridgr_exception_handler
from backend.ml.model_loader import get_core
from backend.routes import analyze, chat, roadmap, market_pulse, interview


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup and shutdown."""
    # STARTUP: load the ML engine once
    print("🌉 Starting Bridgr server...")
    get_core()   # this creates + caches the IntelligenceCore
    print("🌉 Bridgr is ready!")
    yield
    # SHUTDOWN: nothing to clean up


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
    return {"status": "ok"}