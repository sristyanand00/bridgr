# backend/ml/model_loader.py

import os
import sys
from typing import Dict, Any, Union
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all classes from your Colab models
from models.bridgr_final import (
    IntelligenceCore, 
    FallbackIntelligenceCore,
    get_core as get_colab_core,
    reset_core
)

# Import LLM service
from services.llm_service import llm_service

load_dotenv()

_core_instance: Union[IntelligenceCore, FallbackIntelligenceCore, None] = None


def get_core() -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    """
    Returns the Colab-trained ML model instance.
    Uses your bridgr_final.py models with proper configuration.
    """
    global _core_instance
    if _core_instance is None:
        # Use absolute paths to prevent relative path issues
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(backend_dir, "data")
        
        config = {
            "ONET_EXTRACT_PATH": os.getenv("ONET_EXTRACT_PATH", data_dir),
            "ONET_ZIP_PATH": os.getenv("ONET_ZIP_PATH", ""),
            "SEMANTIC_THRESHOLD": float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "DATA_DIR": os.getenv("DATA_DIR", data_dir),
        }
        
        # Set environment variables for the Colab models
        os.environ["ONET_EXTRACT_PATH"] = config["ONET_EXTRACT_PATH"]
        os.environ["ONET_ZIP_PATH"] = config["ONET_ZIP_PATH"]
        os.environ["SEMANTIC_THRESHOLD"] = str(config["SEMANTIC_THRESHOLD"])
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
        os.environ["DATA_DIR"] = config["DATA_DIR"]
        
        try:
            print(" Initializing Colab-trained IntelligenceCore...")
            _core_instance = get_colab_core()
            print(" Using full IntelligenceCore with O*NET data")
        except Exception as e:
            print(f"[WARN] Failed to load full IntelligenceCore: {e}")
            print("[FB] Falling back to FallbackIntelligenceCore")
            _core_instance = FallbackIntelligenceCore(config)
    
    return _core_instance


def analyze_resume(resume_path: str, target_role: str) -> Dict[str, Any]:
    """
    Analyze resume using your Colab-trained models.
    Falls back to Gemini Flash for unknown roles (FREE).
    """
    core = get_core()
    
    try:
        result = core.analyze(resume_path, target_role)
        
        # If analysis returned empty matched_skills (unknown role), try Gemini
        result_dict = result.model_dump() if hasattr(result, 'model_dump') else result
        if not result_dict.get("matched_skills") or len(result_dict.get("matched_skills", [])) == 0:
            print(f"[WARN] Role '{target_role}' not in O*NET   fetching from Gemini Flash...")
            
            # Fetch from Gemini (FREE, 1500 calls/day)
            gemini_profile = llm_service.fetch_job_profile_from_gemini(target_role)
            
            if gemini_profile:
                # Inject Gemini skills into result by updating the dict
                result_dict["matched_skills"] = gemini_profile.get("tech_skills", [])
                result_dict["missing_required"] = []  # Clear missing skills since we're using Gemini
                result_dict["explanations"].append(f"Used Gemini Flash to fetch skills for '{target_role}'")
                print(f"[OK] Injected Gemini profile for '{target_role}'")
                return result_dict
        
        return result.model_dump() if hasattr(result, 'model_dump') else result
    
    except Exception as e:
        print(f"[WARN] Analysis failed: {e}")
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
            "error": str(e)
        }


def reset_models():
    """Reset the core instance - useful for testing or config changes."""
    global _core_instance
    reset_core()
    _core_instance = None
    print("[OK] Models reset - next call will reinitialize.")