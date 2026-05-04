# backend/routes/analyze.py

import os
import sys
import re
import tempfile
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exceptions import ResumeParseFailed, JobRoleNotFound
from models.analysis import AnalysisResult
from services.llm_service import llm_service

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024

# ── helpers ──────────────────────────────────────────────────────────────────

_GARBAGE_ROLE_RE = re.compile(r"^[^a-zA-Z]{0,3}$|^\d+$|^(.)\1{4,}$")  # "123", "aaaa", "   "

def _validate_target_role(role: str) -> str:
    """
    Raise ResumeParseFailed if the role string is clearly garbage.
    Returns the stripped role on success.
    """
    role = role.strip()
    if not role:
        raise ResumeParseFailed("Target role cannot be empty.")
    if len(role) < 3:
        raise ResumeParseFailed(
            f"Target role '{role}' is too short. "
            "Please enter a real job title (e.g. 'Data Scientist')."
        )
    if len(role) > 120:
        raise ResumeParseFailed("Target role is too long (max 120 characters).")
    if _GARBAGE_ROLE_RE.search(role):
        raise ResumeParseFailed(
            f"'{role}' doesn't look like a job title. "
            "Please enter something like 'Software Engineer' or 'Product Manager'."
        )
    # Reject purely numeric or symbol-only strings
    if not any(c.isalpha() for c in role):
        raise ResumeParseFailed(
            "Target role must contain at least some letters. "
            "Example: 'Data Analyst', 'DevOps Engineer'."
        )
    return role


def _serialize_skill_gaps(gaps) -> list:
    """
    Convert a list of SkillGap Pydantic objects (or plain dicts/strings)
    into plain dicts so they can safely be passed to the LLM service
    and serialised to JSON.
    """
    result = []
    for g in gaps:
        if hasattr(g, "model_dump"):          # Pydantic v2
            result.append(g.model_dump())
        elif hasattr(g, "dict"):              # Pydantic v1
            result.append(g.dict())
        elif isinstance(g, dict):
            result.append(g)
        else:
            result.append({"name": str(g)})
    return result


# ── route ────────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_resume(
    resume: UploadFile = File(..., description="PDF resume file"),
    target_role: str = Form(..., description="Target job role, e.g. 'Data Scientist'"),
):
    """
    Upload a resume PDF and target role.
    Returns full career gap analysis with Gemini-powered feasibility score.
    """
    # ── 1. Validate inputs before touching the file ──────────────────────────
    target_role = _validate_target_role(target_role)

    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise ResumeParseFailed("Only PDF files are supported. Please upload a .pdf file.")

    # ── 2. Read & size-check ─────────────────────────────────────────────────
    contents = await resume.read()
    if len(contents) == 0:
        raise ResumeParseFailed("The uploaded file is empty.")
    if len(contents) > MAX_FILE_SIZE:
        raise ResumeParseFailed("File too large. Maximum size is 10MB.")

    # Basic PDF magic-byte check (catches renamed non-PDFs)
    if not contents.startswith(b"%PDF"):
        raise ResumeParseFailed(
            "The file doesn't appear to be a valid PDF. "
            "Please export your resume as a PDF from Word or Google Docs."
        )

    # ── 3. Write to temp file & run ML pipeline ──────────────────────────────
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        # FIX: import get_core and call .analyze() — there is no standalone
        # analyze_resume function; the entry-point is IntelligenceCore.analyze()
        from ml.model_loader import get_core
        core = get_core()
        result = core.analyze(tmp_path, target_role)

        # result is already an AnalysisResult Pydantic model.
        # Convert to dict so we can augment it with the feasibility score.
        result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()

        # ── 4. Gemini feasibility score ──────────────────────────────────────
        # FIX: serialize SkillGap objects → plain dicts before passing to LLM
        missing_required_dicts = _serialize_skill_gaps(result_dict.get("missing_required", []))

        feasibility = llm_service.generate_feasibility_score_with_gemini(
            target_role=target_role,
            match_score=result_dict.get("match_score", 0),
            user_skills=result_dict.get("matched_skills", []),
            missing_required=missing_required_dicts,
            current_role=(
                result_dict.get("extracted_skills", [{}])[0].get("original", "Not specified")
                if result_dict.get("extracted_skills") else "Not specified"
            ),
        )

        result_dict["feasibility"] = feasibility
        return AnalysisResult(**result_dict)

    except (ResumeParseFailed, JobRoleNotFound):
        raise  # re-raise our own typed errors unchanged

    except ValueError as e:
        raise ResumeParseFailed(str(e))

    except Exception as e:
        err = str(e)
        if "not found" in err.lower():
            raise JobRoleNotFound(target_role)
        raise ResumeParseFailed(f"Analysis failed: {err}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)