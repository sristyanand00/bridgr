"""Core ML module for Bridgr — skill extraction, matching, and gap analysis."""

from .schemas import (
    ExtractedSkill,
    SkillGap,
    TransferableSkill,
    AnalysisResult,
    ChatRequest,
    ChatResponse,
    AnalyzeRequest,
    RoadmapResponse,
)
from .dataset import OnetDatasetLoader
from .parser import ResumeParser
from .extractor import SkillExtractor
from .matching import MatchingEngine
from .gaps import GapAnalyzer, update_salary_bands
from .job_skills import DynamicJobSkills
from .core import IntelligenceCore
from .fallback import FallbackIntelligenceCore
from .loader import get_core, reset_core

__all__ = [
    # Schemas
    "ExtractedSkill",
    "SkillGap",
    "TransferableSkill",
    "AnalysisResult",
    "ChatRequest",
    "ChatResponse",
    "AnalyzeRequest",
    "RoadmapResponse",
    # Components
    "OnetDatasetLoader",
    "ResumeParser",
    "SkillExtractor",
    "MatchingEngine",
    "GapAnalyzer",
    "DynamicJobSkills",
    # Cores
    "IntelligenceCore",
    "FallbackIntelligenceCore",
    # Loader
    "get_core",
    "reset_core",
    # Utilities
    "update_salary_bands",
]
