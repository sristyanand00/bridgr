#!/usr/bin/env python3
"""
Simple FastAPI server with only resume analysis functionality
"""
import os
import sys
import tempfile
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fallback_intelligence_core import FallbackIntelligenceCore
from models.analysis import AnalysisResult

# Global core instance
_core_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize ML core on startup"""
    global _core_instance
    print("🌉 Starting Simple Bridgr Server...")
    _core_instance = FallbackIntelligenceCore({})
    print("🌉 Simple Bridgr is ready!")
    yield
    _core_instance = None

app = FastAPI(
    title="Bridgr API (Simple)",
    description="Resume analysis API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_core():
    """Get the ML core instance"""
    if _core_instance is None:
        raise RuntimeError("ML core not initialized")
    return _core_instance

@app.get("/")
def root():
    return {"message": "Bridgr API (Simple)", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "ready": _core_instance is not None}

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_resume(
    resume: UploadFile = File(..., description="PDF resume file"),
    target_role: str = Form(..., description="Target job role, e.g. 'Data Scientists'"),
):
    """
    Upload a resume PDF and target role.
    Returns full career gap analysis.
    """
    # Validate file type
    if not resume.filename.endswith(".pdf"):
        return JSONResponse(
            status_code=422,
            content={"error": "Only PDF files are supported."}
        )

    # Read file bytes
    contents = await resume.read()
    
    # Validate file size (10MB max)
    if len(contents) > 10 * 1024 * 1024:
        return JSONResponse(
            status_code=422,
            content={"error": "File too large. Maximum size is 10MB."}
        )

    # Write to temp file (fallback core doesn't actually read it, but we keep the interface)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        core = get_core()
        result = core.analyze(tmp_path, target_role)
        return result

    except Exception as e:
        print(f"Analysis error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {str(e)}"}
        )
    finally:
        # Clean up temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
