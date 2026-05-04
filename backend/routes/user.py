from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from services.auth_service import get_current_user
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter()

class QuizUpdate(BaseModel):
    quiz_data: Any

@router.post("/user/sync")
def sync_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Called on login to ensure the user exists in PostgreSQL.
    Returns the user's saved data (like quiz results).
    """
    uid = current_user.get("uid")
    db_user = db.query(User).filter(User.id == uid).first()
    
    if not db_user:
        db_user = User(
            id=uid,
            email=current_user.get("email"),
            name=current_user.get("name") or current_user.get("email", "").split("@")[0]
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    return {
        "uid": db_user.id,
        "email": db_user.email,
        "name": db_user.name,
        "quiz_data": db_user.quiz_data,
        "created_at": db_user.created_at
    }

@router.post("/user/quiz")
def update_quiz(
    data: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Saves the onboarding quiz results.
    """
    uid = current_user.get("uid")
    db_user = db.query(User).filter(User.id == uid).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.quiz_data = data.quiz_data
    db.commit()
    
    return {"status": "success", "quiz_data": db_user.quiz_data}

@router.get("/user/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the user's past analyses and roadmaps.
    """
    uid = current_user.get("uid")
    
    from db.models import Analysis, Roadmap
    
    analyses = db.query(Analysis).filter(Analysis.user_id == uid).order_by(Analysis.created_at.desc()).all()
    roadmaps = db.query(Roadmap).filter(Roadmap.user_id == uid).order_by(Roadmap.created_at.desc()).all()
    
    return {
        "analyses": [
            {
                "id": a.id,
                "target_role": a.target_role,
                "match_score": a.match_score,
                "created_at": a.created_at,
                "feasibility": a.feasibility_score
            } for a in analyses
        ],
        "roadmaps": [
            {
                "id": r.id,
                "analysis_id": r.analysis_id,
                "target_role": r.target_role,
                "total_days": r.total_days,
                "created_at": r.created_at,
                "summary": r.summary
            } for r in roadmaps
        ]
    }

