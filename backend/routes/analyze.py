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
from services.auth_service import get_user_optional
from db.database import get_db
from db.models import Analysis, User
from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, Form, Depends

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024

#    helpers                                                                   

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


#    route                                                                     

@router.post("/analyze", response_model=AnalysisResult)
def analyze_resume(
    resume: UploadFile = File(..., description="PDF resume file"),
    target_role: str = Form(..., description="Target job role, e.g. 'Data Scientist'"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_optional)
):
    """
    Upload a resume PDF and target role.
    Returns full career gap analysis with Gemini-powered feasibility score.
    """
    #    1. Validate inputs before touching the file                           
    target_role = _validate_target_role(target_role)

    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise ResumeParseFailed("Only PDF files are supported. Please upload a .pdf file.")

    #    2. Read & size-check (synchronous read)
    contents = resume.file.read()
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

    #    3. Write to temp file & run ML pipeline                               
    tmp_path = None
    try:
        print(f"[RESUME] Processing resume for: {target_role}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        print("[ML] Loading ML models...")
        from ml.model_loader import get_core
        core = get_core()
        
        print("[MATCH] Running NLP extraction and gap analysis...")
        result = core.analyze(tmp_path, target_role)

        result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()

        #    4. Gemini feasibility score                                       
        print("[AI] Generating Gemini feasibility score...")
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

        #    5. Save to database if user is authenticated                      
        if current_user:
            uid = current_user.get("uid")
            print(f"[DB] Saving results to database for user: {uid}")
            
            # Ensure user exists in database
            db_user = db.query(User).filter(User.id == uid).first()
            if not db_user:
                print(f"[USER] Creating new user record for: {uid}")
                db_user = User(
                    id=uid,
                    email=current_user.get("email"),
                    name=current_user.get("name") or current_user.get("email", "").split("@")[0]
                )
                db.add(db_user)
                db.commit()
            
            # Save analysis
            db_analysis = Analysis(
                user_id=uid,
                target_role=target_role,
                match_score=result_dict.get("match_score", 0),
                feasibility_score=feasibility,
                skill_gaps=missing_required_dicts,
                matched_skills=result_dict.get("matched_skills", []),
                roadmap_inputs=result_dict.get("learning_roadmap_inputs", {})
            )
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)
            
            # Add the DB ID to the response
            result_dict["analysis_id"] = str(db_analysis.id)
            print(f"[OK] Analysis saved with ID: {db_analysis.id}")
            
        print("[DONE] Analysis request completed successfully")
        return AnalysisResult(**result_dict)

    except (ResumeParseFailed, JobRoleNotFound):
        raise  # re-raise our own typed errors unchanged

    except ValueError as e:
        raise ResumeParseFailed(str(e))

    except Exception as e:
        import traceback
        traceback.print_exc()
        err = str(e)
        if "not found" in err.lower():
            raise JobRoleNotFound(target_role)
        raise ResumeParseFailed(f"Analysis failed: {err}")

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)