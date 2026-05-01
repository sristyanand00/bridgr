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
from services.llm_service import llm_service

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
    Returns full career gap analysis with Gemini-powered feasibility score.
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
        
        # NEW: Add Gemini feasibility score
        feasibility = llm_service.generate_feasibility_score_with_gemini(
            target_role=target_role,
            match_score=result_dict.get("match_score", 0),
            user_skills=result_dict.get("matched_skills", []),
            missing_required=result_dict.get("missing_required", []),
            current_role=result_dict.get("extracted_skills", [{}])[0].get("original", "Not specified") if result_dict.get("extracted_skills") else "Not specified"
        )
        
        # Add feasibility to result
        result_dict["feasibility"] = feasibility
        
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