# backend/routes/roadmap.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Any
from dotenv import load_dotenv

from core.exceptions import AIServiceError
from models.analysis import RoadmapResponse
from services.llm_service import llm_service

load_dotenv()

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class RoadmapRequest(BaseModel):
    target_role: str
    match_score: int
    readiness_level: str
    roadmap_inputs: Dict[str, Any]
    matched_skills: List[Any] = []
    missing_required: List[Any] = []
    total_days: int = 90          # ← NEW: user-supplied day count


def _extract_name(gap: Any) -> str:
    """Safely pull a skill name from a SkillGap dict, plain dict, or string."""
    if isinstance(gap, dict):
        return gap.get("name") or gap.get("skill_name") or str(gap)
    return str(gap)


def _build_fallback_from_inputs(
    roadmap_inputs: Dict[str, Any],
    target_role: str,
    match_score: int,
    total_days: int = 90,
) -> RoadmapResponse:
    """
    Build a RoadmapResponse directly from the pre-computed learning_roadmap_inputs
    that the ML pipeline already produced in AnalysisResult.
    Used when Gemini is unavailable.
    """
    phases_raw = roadmap_inputs.get("phases", [])
    total_weeks = roadmap_inputs.get("total_estimated_weeks", total_days // 7)

    phases = []
    for ph in phases_raw:
        skills = ph.get("skills", [])
        resources_raw = ph.get("resources", [])

        resources = []
        for r in resources_raw:
            if isinstance(r, str) and "|" in r:
                name, url = r.split("|", 1)
                resources.append({"name": name.strip(), "url": url.strip(), "free": True})
            elif isinstance(r, dict):
                resources.append(r)
            else:
                resources.append({"name": str(r), "url": "", "free": True})

        duration_weeks = ph.get("duration_weeks", 4)
        start = ph.get("start_week", 1)
        end = ph.get("end_week", start + duration_weeks - 1)

        phases.append({
            "phase": ph.get("phase", len(phases) + 1),
            "label": ph.get("label", f"Phase {len(phases) + 1}"),
            "duration_weeks": duration_weeks,
            "duration": f"Weeks {start}–{end}",
            "goal": f"Master {', '.join(skills[:2])} and related fundamentals" if skills else "Build core skills",
            "skills": skills,
            "topics": [],
            "weeks": [],
            "resources": resources,
        })

    summary = (
        f"A {total_days}-day personalised roadmap to become a {target_role}. "
        f"Starting from a {match_score}% match, each phase closes specific skill gaps "
        "identified from your resume."
    )

    return RoadmapResponse(
        phases=phases,
        total_weeks=int(total_weeks) if total_weeks else total_days // 7,
        total_days=total_days,
        summary=summary,
    )


@router.post("/roadmap", response_model=RoadmapResponse)
async def generate_roadmap(request: RoadmapRequest):
    """
    Generate a detailed learning roadmap for the requested number of days.
    Uses Gemini for rich topic-by-topic teacher format; falls back to the
    ML-computed phase structure when Gemini is unavailable.
    """
    # ── 1. Basic validation ──────────────────────────────────────────────────
    if not request.target_role.strip():
        raise AIServiceError("target_role cannot be empty.")

    total_days = max(7, request.total_days)  # minimum 7 days

    # ── 2. Serialize missing_required to plain strings ────────────────────────
    missing_names = [_extract_name(g) for g in request.missing_required]

    # ── 3. Extract matched_skills as plain strings ────────────────────────────
    matched = [str(s) for s in request.matched_skills]

    # ── 4. Try Gemini first ───────────────────────────────────────────────────
    if GEMINI_API_KEY:
        try:
            missing_dicts = [{"name": n} for n in missing_names]

            result = llm_service.generate_roadmap_with_gemini(
                target_role=request.target_role,
                match_score=request.match_score,
                missing_required=missing_dicts,
                available_hours_per_week=10,
                matched_skills=matched,
                total_days=total_days,        # ← passed through
            )

            phases = result.get("phases", [])
            total_weeks = result.get("total_weeks", total_days // 7)
            summary = result.get("summary", "")

            if phases:
                normalised = []
                for ph in phases:
                    skills = ph.get("skills", [])
                    dur = int(ph.get("duration_weeks", total_days // (7 * 3)))
                    phase_num = ph.get("phase", len(normalised) + 1)
                    start = (phase_num - 1) * dur + 1
                    end = phase_num * dur

                    normalised.append({
                        "phase": phase_num,
                        "label": ph.get("label", f"Phase {phase_num}"),
                        "duration_weeks": dur,
                        "duration": ph.get("day_range") or ph.get("duration", f"Weeks {start}–{end}"),
                        "goal": ph.get("goal", ""),
                        "skills": skills,
                        "topics": ph.get("topics", []),      # ← NEW: teacher topics
                        "weeks": ph.get("weeks", []),
                        "resources": ph.get("resources", []),
                        "milestones": ph.get("milestones", []),
                        "milestone": (
                            ph["weeks"][0].get("milestone", "") if ph.get("weeks") else ""
                        ),
                    })

                return RoadmapResponse(
                    phases=normalised,
                    total_weeks=int(total_weeks),
                    total_days=total_days,
                    summary=summary,
                )

        except Exception as e:
            print(f"⚠️  Gemini roadmap failed, using ML fallback: {e}")

    # ── 5. Fallback ───────────────────────────────────────────────────────────
    print("ℹ️  Using ML-computed roadmap fallback")
    return _build_fallback_from_inputs(
        roadmap_inputs=request.roadmap_inputs,
        target_role=request.target_role,
        match_score=request.match_score,
        total_days=total_days,
    )