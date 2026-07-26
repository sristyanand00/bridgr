# backend/ml/model_loader.py

import logging
import os
import sys
from typing import Any, Dict, Union

from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_ml import (
    FallbackIntelligenceCore,
    IntelligenceCore,
    get_core as get_colab_core,
    reset_core,
)

load_dotenv()

logger = logging.getLogger(__name__)

_core_instance: Union[IntelligenceCore, FallbackIntelligenceCore, None] = None


def get_core() -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    """Returns the ML core, initialising it on first call."""
    global _core_instance
    if _core_instance is None:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(backend_dir, "data")

        config = {
            "ONET_EXTRACT_PATH": os.getenv("ONET_EXTRACT_PATH", data_dir),
            "ONET_ZIP_PATH": os.getenv("ONET_ZIP_PATH", ""),
            "SEMANTIC_THRESHOLD": float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "DATA_DIR": os.getenv("DATA_DIR", data_dir),
        }

        os.environ["ONET_EXTRACT_PATH"] = config["ONET_EXTRACT_PATH"]
        os.environ["ONET_ZIP_PATH"] = config["ONET_ZIP_PATH"]
        os.environ["SEMANTIC_THRESHOLD"] = str(config["SEMANTIC_THRESHOLD"])
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
        os.environ["DATA_DIR"] = config["DATA_DIR"]

        try:
            logger.info("Initializing IntelligenceCore...")
            _core_instance = get_colab_core()
            logger.info("Using full IntelligenceCore with O*NET data")
        except Exception as e:
            logger.warning(
                "FALLBACK MODE — O*NET data not found. Scores will be less accurate. "
                "Run: python scripts/setup_data.py"
            )
            logger.debug("IntelligenceCore init error: %s", e, exc_info=True)
            _core_instance = FallbackIntelligenceCore(config)

    return _core_instance


def analyze_resume(resume_path: str, target_role: str) -> Dict[str, Any]:
    """Analyze resume using the ML core, with LLM fallback for unknown roles."""
    from services.llm_service import llm_service  # noqa: PLC0415

    core = get_core()

    try:
        result = core.analyze(resume_path, target_role)
        result_dict = result.model_dump() if hasattr(result, "model_dump") else result
        if not result_dict.get("matched_skills"):
            logger.warning("Role '%s' not in O*NET — fetching from Gemini Flash...", target_role)
            gemini_profile = llm_service.fetch_job_profile_from_gemini(target_role)
            if gemini_profile:
                result_dict["matched_skills"] = gemini_profile.get("tech_skills", [])
                result_dict["missing_required"] = []
                result_dict["explanations"].append(
                    f"Used Gemini Flash to fetch skills for '{target_role}'"
                )
                logger.info("Injected Gemini profile for '%s'", target_role)
                return result_dict

        return result.model_dump() if hasattr(result, "model_dump") else result

    except Exception as e:
        logger.error("Analysis failed: %s", e, exc_info=True)
        from datetime import datetime

        return {
            "analysis_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "target_role": target_role,
            "match_score": 0,
            "readiness_level": "Analysis Failed",
            "confidence_score": 0.0,
            "extracted_skills": [],
            "matched_skills": [],
            "missing_required": [],
            "missing_preferred": [],
            "transferable_skills": [],
            "priority_skills": [],
            "market_demand_skills": [],
            "learning_roadmap_inputs": {},
            "mock_interview_inputs": {},
            "career_chat_context": {},
            "salary_band_estimate": {},
            "explanations": [f"Analysis failed: {str(e)}"],
            "error": str(e),
        }


def reset_models():
    """Reset the core instance — useful for testing or config changes."""
    global _core_instance
    reset_core()
    _core_instance = None
    logger.info("Models reset — next call will reinitialize.")
