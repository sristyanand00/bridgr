"""Pure scoring engine for readiness assessment.

CRITICAL RULES (from project.md):
1. This is a PURE function - no I/O, no network, no LLM calls, no datetime.now()
2. Same input MUST produce byte-identical output every time
3. No LLM produces numbers that feed scores
4. today is a parameter, not computed

Formulas:
  weight_i      = criticality × frequency
  screen_cov    = 1.0 if level >= 1 else 0.0
  interview_cov = min(level / required_level, 1) × recency_mult
  job_cov       = interview_cov × scope_factor
  score         = 100 × Σ(weight × cov) / Σ(weight)
  
  hard blocker  → cap screen at 40, interview and job at 55

Recency multipliers:
  ≤18 months: 1.0
  ≤36 months: 0.90
  ≤60 months: 0.75
  else:       0.60
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SCORING_VERSION = "v1.0"

# Recency decay thresholds (in months)
RECENCY_THRESHOLDS = [
    (18, 1.0),
    (36, 0.90),
    (60, 0.75),
    (float('inf'), 0.60),
]

# Hard blocker caps
SCREEN_CAP_WITH_BLOCKER = 40.0
INTERVIEW_CAP_WITH_BLOCKER = 55.0
JOB_CAP_WITH_BLOCKER = 55.0


class UserSkill(BaseModel):
    """A skill the user possesses."""
    skill: str
    level: int                      # 0-4 evidence level
    last_used: Optional[str] = None  # ISO 'YYYY-MM'; None = unknown date


class Requirement(BaseModel):
    """A job requirement."""
    skill: str
    required_level: int  # 1-4
    criticality: float  # 0.0-1.0, importance weight
    frequency: float    # 0.0-1.0, how often used
    is_blocker: bool    # Hard requirement (e.g., security clearance, visa)


class ScoreInput(BaseModel):
    """Input to the scoring function - pure data."""
    user_skills: List[UserSkill]
    requirements: List[Requirement]
    today: str  # ISO date string, e.g., "2026-07-25"


class ScoreComponent(BaseModel):
    """Breakdown for a single requirement."""
    skill: str
    required_level: int
    user_level: int
    weight: float
    recency_mult: Optional[float]   # None = skill absent (no recency to report)
    screen_coverage: float
    interview_coverage: float
    job_coverage: float
    points_earned: float
    points_possible: float
    reason: str  # Human-readable explanation, GENERATED IN CODE


class ScoreResult(BaseModel):
    """Output of the scoring function."""
    scoring_version: str
    screen_score: float
    interview_score: float
    job_score: float
    verdict: str  # "ready", "developing", "early", "blocked"
    has_blocker: bool
    components: List[ScoreComponent]
    total_weight: float
    explanation: str


def _months_between(last_used: Optional[str], today: str) -> Optional[int]:
    """
    Return months elapsed between last_used (ISO 'YYYY-MM') and today (ISO date).
    Returns None when last_used is None — caller must treat None as unknown,
    not as stale.  We never guess a date.
    """
    if last_used is None:
        return None
    try:
        ly, lm = int(last_used[:4]), int(last_used[5:7])
        td = datetime.fromisoformat(today)
        return (td.year - ly) * 12 + (td.month - lm)
    except (ValueError, IndexError):
        return None


def score(inp: ScoreInput) -> ScoreResult:
    """
    Pure scoring function. NO I/O, NO NETWORK, NO datetime.now().
    Same input produces identical output every time.
    
    Args:
        inp: ScoreInput with user skills, requirements, and today's date
        
    Returns:
        ScoreResult with three scores and detailed breakdown
    """
    # Build skill lookup
    user_skill_map: Dict[str, UserSkill] = {s.skill.lower(): s for s in inp.user_skills}
    
    # Check for hard blockers — absent OR present but below required level
    has_blocker = any(
        r.is_blocker and (
            r.skill.lower() not in user_skill_map
            or user_skill_map[r.skill.lower()].level < r.required_level
        )
        for r in inp.requirements
    )
    
    components: List[ScoreComponent] = []
    total_weight = 0.0
    screen_points = 0.0
    interview_points = 0.0
    job_points = 0.0
    
    for req in inp.requirements:
        # Weight = criticality × frequency
        weight = req.criticality * req.frequency
        total_weight += weight
        
        skill_key = req.skill.lower()
        user_skill = user_skill_map.get(skill_key)
        
        if user_skill is None:
            # Skill absent — recency_mult is None (not stale; simply not present)
            components.append(ScoreComponent(
                skill=req.skill,
                required_level=req.required_level,
                user_level=0,
                weight=weight,
                recency_mult=None,
                screen_coverage=0.0,
                interview_coverage=0.0,
                job_coverage=0.0,
                points_earned=0.0,
                points_possible=weight,
                reason=f"Not present in profile (required level {req.required_level})"
            ))
            continue

        # Compute months elapsed from last_used and today (both parameters — pure)
        months_since = _months_between(user_skill.last_used, inp.today)

        # Unknown date → no decay; we never treat unknown as stale
        recency_mult = _get_recency_mult(months_since) if months_since is not None else 1.0
        date_unknown = months_since is None
        
        # Screen coverage: 1.0 if claimed (level >= 1), else 0
        screen_cov = 1.0 if user_skill.level >= 1 else 0.0
        
        # Interview coverage: min(user_level / required_level, 1.0) × recency
        level_ratio = min(user_skill.level / req.required_level, 1.0) if req.required_level > 0 else 1.0
        interview_cov = level_ratio * recency_mult
        
        # Job coverage: same as interview for now (scope_factor = 1.0)
        # Future: could add scope adjustment based on company size, role complexity
        job_cov = interview_cov
        
        # Points earned
        screen_pts = weight * screen_cov
        interview_pts = weight * interview_cov
        job_pts = weight * job_cov
        
        screen_points += screen_pts
        interview_points += interview_pts
        job_points += job_pts
        
        # Generate reason
        reason = _generate_reason(req, user_skill, recency_mult, level_ratio, date_unknown)
        
        components.append(ScoreComponent(
            skill=req.skill,
            required_level=req.required_level,
            user_level=user_skill.level,
            weight=weight,
            recency_mult=recency_mult,
            screen_coverage=screen_cov,
            interview_coverage=interview_cov,
            job_coverage=job_cov,
            points_earned=interview_pts,
            points_possible=weight,
            reason=reason
        ))
    
    # Compute raw scores
    if total_weight == 0:
        screen_score = interview_score = job_score = 0.0
    else:
        screen_score = round(100.0 * screen_points / total_weight, 2)
        interview_score = round(100.0 * interview_points / total_weight, 2)
        job_score = round(100.0 * job_points / total_weight, 2)
    
    # Apply blocker caps
    if has_blocker:
        screen_score = min(screen_score, SCREEN_CAP_WITH_BLOCKER)
        interview_score = min(interview_score, INTERVIEW_CAP_WITH_BLOCKER)
        job_score = min(job_score, JOB_CAP_WITH_BLOCKER)
    
    # Determine verdict
    verdict = _determine_verdict(interview_score, has_blocker)
    
    # Generate explanation
    explanation = _generate_explanation(verdict, has_blocker, components, inp.requirements)
    
    return ScoreResult(
        scoring_version=SCORING_VERSION,
        screen_score=screen_score,
        interview_score=interview_score,
        job_score=job_score,
        verdict=verdict,
        has_blocker=has_blocker,
        components=components,
        total_weight=total_weight,
        explanation=explanation
    )


def _get_recency_mult(months_since: int) -> float:
    """Calculate recency multiplier based on months since last use."""
    for threshold, mult in RECENCY_THRESHOLDS:
        if months_since <= threshold:
            return mult
    # RECENCY_THRESHOLDS ends with float('inf'), so this is unreachable
    return 0.60  # pragma: no cover


def _generate_reason(
    req: Requirement,
    user_skill: UserSkill,
    recency_mult: float,
    level_ratio: float,
    date_unknown: bool = False,
) -> str:
    """Generate human-readable reason for a single requirement's score."""
    parts = []

    # Level assessment
    if user_skill.level >= req.required_level:
        parts.append(f"Meets required level {req.required_level}")
    elif user_skill.level > 0:
        parts.append(f"Level {user_skill.level}/{req.required_level} - partially meets requirement")
    else:
        parts.append("Not demonstrated")

    # Recency
    if date_unknown:
        parts.append("last-used date unknown — no decay applied")
    elif recency_mult < 1.0:
        parts.append(f"last used {user_skill.last_used} (recency: {int(recency_mult * 100)}%)")
    elif user_skill.level > 0:
        parts.append("recently used")

    return "; ".join(parts)


def _determine_verdict(interview_score: float, has_blocker: bool) -> str:
    """Map interview score to readiness verdict."""
    if has_blocker:
        return "blocked"
    if interview_score >= 80:
        return "ready"
    elif interview_score >= 50:
        return "developing"
    else:
        return "early"


def _generate_explanation(
    verdict: str,
    has_blocker: bool,
    components: List[ScoreComponent],
    requirements: List[Requirement],
) -> str:
    """Generate overall explanation."""
    if has_blocker:
        missing_blockers = [
            r.skill for r in requirements
            if r.is_blocker and any(
                c.skill.lower() == r.skill.lower() and c.user_level < r.required_level
                for c in components
            )
        ]
        blocker_list = ", ".join(missing_blockers) if missing_blockers else "unknown"
        return f"Missing hard blocker: {blocker_list}"
    
    missing = [c.skill for c in components if c.user_level == 0]
    partial = [c.skill for c in components if 0 < c.user_level < c.required_level]
    
    parts = []
    if verdict == "ready":
        parts.append("Strong match with all key requirements met")
    elif verdict == "developing":
        parts.append("Solid foundation with room for growth")
    else:
        parts.append("Early stage - significant skill gaps remain")
    
    if missing:
        parts.append(f"Missing: {', '.join(missing[:3])}")
    if partial:
        parts.append(f"Partial: {', '.join(partial[:3])}")
    
    return ". ".join(parts)
