# backend/models/analysis.py

from pydantic import BaseModel
from typing import List, Dict, Optional


class ExtractedSkill(BaseModel):
    """One skill found in the user's resume."""
    name: str
    normalized: str        # lowercase version, used for comparisons
    confidence: float      # 0.0 to 1.0 — how sure we are
    source: str            # "phrase_match", "semantic", or "llm_fallback"
    context: str = ""      # the surrounding sentence it was found in


class SkillGap(BaseModel):
    """A skill the user is missing, with context about how important it is."""
    name: str
    priority: str          # "Critical", "High", "Medium", or "Low"
    priority_score: float  # numeric 0–1 used for sorting
    market_demand: float   # what fraction of jobs need this skill
    reason: str            # human-readable explanation for the user
    estimated_weeks: int   # how long to learn it
    has_foundation: bool   # does the user have a related skill already?


class TransferableSkill(BaseModel):
    """A skill the user has that partially satisfies a requirement they're missing."""
    user_skill: str
    maps_to_job_skill: str
    transfer_score: float  # semantic similarity 0–1
    explanation: str


class AnalysisResult(BaseModel):
    """
    The complete output of one resume analysis.
    This single object is what everything else in the app reads from:
    - The /analyze API endpoint returns this
    - The chatbot reads career_chat_context from this
    - The roadmap generator reads learning_roadmap_inputs from this
    - The interview simulator reads mock_interview_inputs from this
    """
    # Identity
    analysis_id: str
    generated_at: str
    target_role: str

    # The main scores shown on the dashboard
    match_score: int           # 0–100
    readiness_level: str       # "Ready", "Almost Ready", etc.
    confidence_score: float    # how much to trust the score

    # Skills
    extracted_skills: List[ExtractedSkill]
    matched_skills: List[str]
    missing_required: List[SkillGap]
    missing_preferred: List[SkillGap]
    transferable_skills: List[TransferableSkill]
    priority_skills: List[str]        # top 5 to learn first (shown in roadmap)
    market_demand_skills: List[str]   # trending skills in the market

    # Context that feeds downstream features
    learning_roadmap_inputs: Dict
    mock_interview_inputs: Dict
    career_chat_context: Dict

    # Salary shown on dashboard
    salary_band_estimate: Dict

    # Plain-English explanations shown to the user
    explanations: List[str]


class ChatRequest(BaseModel):
    """What the frontend sends when the user types a message."""
    message: str
    analysis_id: Optional[str] = None
    context: Optional[Dict] = None   # the career_chat_context from AnalysisResult


class ChatResponse(BaseModel):
    """What the backend sends back to the frontend chat."""
    reply: str
    suggestions: List[str] = []  # follow-up question chips


class AnalyzeRequest(BaseModel):
    """The form data for the /analyze endpoint. Resume comes as a file upload."""
    target_role: str


class RoadmapResponse(BaseModel):
    """Structured roadmap returned by /roadmap."""
    phases: List[Dict]
    total_weeks: int
    summary: str