"""Core data schemas for the Bridgr ML system."""

from __future__ import annotations
import logging
from pydantic import BaseModel, field_validator
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


class ExtractedSkill(BaseModel):
    original:   str
    normalized: str
    confidence: float
    source:     str = "resume"
    context:    str = ""

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class SkillGap(BaseModel):
    name:               str
    priority:           str
    priority_score:     float = 0.5
    market_demand:      float = 0.05
    reason:             str   = ""
    estimated_weeks:    int   = 4
    has_foundation:     bool  = False
    learning_resources: List[str] = []

    @property
    def demand_percentage(self) -> int:
        return int(self.market_demand * 100)


class TransferableSkill(BaseModel):
    user_skill:        str
    maps_to_job_skill: str
    transfer_score:    float
    explanation:       str


class AnalysisResult(BaseModel):
    analysis_id:      str
    generated_at:     str
    target_role:      str

    match_score:      int
    readiness_level:  str
    confidence_score: float

    extracted_skills:    List[ExtractedSkill]
    matched_skills:      List[str]
    missing_required:    List[SkillGap]
    missing_preferred:   List[SkillGap]
    transferable_skills: List[TransferableSkill]
    priority_skills:     List[str]
    market_demand_skills: List[str]

    learning_roadmap_inputs: Dict[str, Any]
    mock_interview_inputs:   Dict[str, Any]
    career_chat_context:     Dict[str, Any]

    salary_band_estimate: Dict[str, Any]
    feasibility: Optional[Dict[str, Any]] = None
    explanations:         List[str]


class ChatRequest(BaseModel):
    message:     str
    analysis_id: Optional[str]           = None
    context:     Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply:       str
    suggestions: List[str] = []


class AnalyzeRequest(BaseModel):
    target_role: str


class RoadmapResponse(BaseModel):
    phases:      List[Dict[str, Any]]
    total_weeks: int
    summary:     str
