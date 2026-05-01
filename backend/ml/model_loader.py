# backend/ml/model_loader.py
# Integrated with Colab-trained models from bridgr_final.py

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

load_dotenv()

# This is created ONCE when the module is imported.
# FastAPI imports this at startup and reuses the instance.
_core_instance: Union[IntelligenceCore, FallbackIntelligenceCore, None] = None


def get_core() -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    """
    Returns the Colab-trained ML model instance.
    Uses your bridgr_final.py models with proper configuration.
    """
    global _core_instance
    if _core_instance is None:
        # Update config paths for local environment
        config = {
            "ONET_EXTRACT_PATH": os.getenv("ONET_EXTRACT_PATH", "data/"),
            "ONET_ZIP_PATH": os.getenv("ONET_ZIP_PATH", ""),
            "SEMANTIC_THRESHOLD": float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "DATA_DIR": os.getenv("DATA_DIR", "data/"),
        }
        
        # Set environment variables for the Colab models
        os.environ["ONET_EXTRACT_PATH"] = config["ONET_EXTRACT_PATH"]
        os.environ["ONET_ZIP_PATH"] = config["ONET_ZIP_PATH"]
        os.environ["SEMANTIC_THRESHOLD"] = str(config["SEMANTIC_THRESHOLD"])
        os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
        os.environ["DATA_DIR"] = config["DATA_DIR"]
        
        try:
            # Use your Colab IntelligenceCore
            print("🚀 Initializing Colab-trained IntelligenceCore...")
            _core_instance = get_colab_core()
            print("✅ Using full IntelligenceCore with O*NET data")
        except Exception as e:
            print(f"⚠️  Failed to load full IntelligenceCore: {e}")
            print("🔄 Falling back to FallbackIntelligenceCore")
            # Use your Colab FallbackIntelligenceCore
            _core_instance = FallbackIntelligenceCore(config)
    
    return _core_instance


def analyze_resume(resume_path: str, target_role: str) -> Dict[str, Any]:
    """
    Analyze resume using your Colab-trained models.
    """
    core = get_core()
    
    try:
        result = core.analyze(resume_path, target_role)
        return result.model_dump()  # Convert Pydantic to dict for JSON response
    except Exception as e:
        print(f"⚠️  Analysis failed: {e}")
        return {
            "analysis_id": "error",
            "target_role": target_role,
            "match_score": 0,
            "readiness_level": "Analysis Failed",
            "extracted_skills": [],
            "matched_skills": [],
            "missing_required": [],
            "missing_preferred": [],
            "transferable_skills": [],
            "priority_skills": [],
            "market_demand_skills": [],
            "explanations": [f"Analysis failed: {str(e)}"],
            "error": str(e)
        }


def reset_models():
    """Reset the core instance - useful for testing or config changes."""
    global _core_instance
    reset_core()
    _core_instance = None
    print("🔄 Models reset - next call will reinitialize.")
