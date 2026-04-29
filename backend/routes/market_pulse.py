# backend/routes/market_pulse.py

import os
import sys
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.model_loader import get_core

router = APIRouter()


class MarketPulseResponse(BaseModel):
    role: str
    top_demanded_skills: List[dict]
    salary_band: dict
    total_jobs_in_dataset: int
    insight: str


@router.get("/market-pulse", response_model=MarketPulseResponse)
async def market_pulse(role: str = Query(..., description="Target role, e.g. 'Data Scientists'")):
    """
    Returns market demand data for a job role based on O*NET dataset.
    Shows which skills are most demanded across all jobs in the field.
    """
    core = get_core()
    df = core.dataset_loader.load()
    demand = core.dataset_loader.skill_market_demand

    # Filter to this role's skills
    profile = core.dataset_loader.get_job_profile(role)
    if profile is None:
        return MarketPulseResponse(
            role=role,
            top_demanded_skills=[],
            salary_band={"min": 0, "max": 0, "median": 0, "currency": "INR"},
            total_jobs_in_dataset=len(df),
            insight="Role not found. Try 'Data Scientists' or 'Software Developers'."
        )

    role_skills = profile["tech_skills"]

    # Get demand scores for this role's skills, sorted
    skill_demand = sorted(
        [{"skill": s, "demand_pct": round(demand.get(s, 0) * 100, 1)}
         for s in role_skills if s],
        key=lambda x: x["demand_pct"], reverse=True
    )[:10]

    salary = core.gap_analyzer.get_salary_band(role)

    return MarketPulseResponse(
        role=role,
        top_demanded_skills=skill_demand,
        salary_band=salary,
        total_jobs_in_dataset=len(df),
        insight=f"Based on {len(df)} O*NET job profiles. "
                f"Top skill: {skill_demand[0]['skill'] if skill_demand else 'N/A'} "
                f"appears in {skill_demand[0]['demand_pct'] if skill_demand else 0}% of jobs."
    )