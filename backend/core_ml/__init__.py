"""Core ML module for Bridgr — skill extraction, matching, and gap analysis."""

# Lazy imports to avoid pulling in heavy dependencies when only needing schemas
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
    # Components - lazy loaded
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


def __getattr__(name):
    """Lazy import to avoid loading heavy dependencies unless needed."""
    if name in ("ExtractedSkill", "SkillGap", "TransferableSkill", "AnalysisResult",
                "ChatRequest", "ChatResponse", "AnalyzeRequest", "RoadmapResponse"):
        from .schemas import (
            ExtractedSkill, SkillGap, TransferableSkill, AnalysisResult,
            ChatRequest, ChatResponse, AnalyzeRequest, RoadmapResponse
        )
        return locals()[name]
    elif name == "OnetDatasetLoader":
        from .dataset import OnetDatasetLoader
        return OnetDatasetLoader
    elif name == "ResumeParser":
        from .parser import ResumeParser
        return ResumeParser
    elif name == "SkillExtractor":
        from .extractor import SkillExtractor
        return SkillExtractor
    elif name == "MatchingEngine":
        from .matching import MatchingEngine
        return MatchingEngine
    elif name == "GapAnalyzer":
        from .gaps import GapAnalyzer
        return GapAnalyzer
    elif name == "update_salary_bands":
        from .gaps import update_salary_bands
        return update_salary_bands
    elif name == "DynamicJobSkills":
        from .job_skills import DynamicJobSkills
        return DynamicJobSkills
    elif name == "IntelligenceCore":
        from .core import IntelligenceCore
        return IntelligenceCore
    elif name == "FallbackIntelligenceCore":
        from .fallback import FallbackIntelligenceCore
        return FallbackIntelligenceCore
    elif name in ("get_core", "reset_core"):
        from .loader import get_core, reset_core
        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
