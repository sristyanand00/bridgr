# backend/routes/analyze.py

import os
import sys
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from ml.model_loader import get_core  # Replaced with Colab models
from core.exceptions import ResumeParseFailed, JobRoleNotFound
from models.analysis import AnalysisResult

router = APIRouter()

# Max resume size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/analyze", response_model=AnalysisResult)
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
        raise ResumeParseFailed("Only PDF files are supported.")

    # Read file bytes
    contents = await resume.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise ResumeParseFailed("File too large. Maximum size is 10MB.")

    # Write to temp file so pdfplumber can read it
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        from ml.model_loader import analyze_resume
        result_dict = analyze_resume(tmp_path, target_role)
        # Convert dict back to AnalysisResult for FastAPI response
        return AnalysisResult(**result_dict)

    except ValueError as e:
        # ValueError is raised by ResumeParser for scanned PDFs, bad files, etc.
        raise ResumeParseFailed(str(e))
    except Exception as e:
        error_str = str(e)
        if "not found" in error_str.lower():
            raise JobRoleNotFound(target_role)
        raise ResumeParseFailed(f"Analysis failed: {error_str}")
    finally:
        # Always clean up the temp file, even if analysis failed
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)