# backend/ml/model_loader.py

import os
import sys
from typing import Optional, Union
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.intelligence_core import IntelligenceCore
except ImportError:
    IntelligenceCore = None
try:
    from services.fallback_intelligence_core import FallbackIntelligenceCore
except ImportError:
    FallbackIntelligenceCore = None

load_dotenv()

# This is created ONCE when the module is imported.
# FastAPI imports this at startup and reuses the instance.
_core_instance: Optional[Union[IntelligenceCore, FallbackIntelligenceCore]] = None


def get_core() -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    global _core_instance
    if _core_instance is None:
        config = {
            "ONET_EXTRACT_PATH":   os.getenv("ONET_EXTRACT_PATH", "data/"),
            "SEMANTIC_THRESHOLD":  float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY":     os.getenv("OPENAI_API_KEY", ""),
        }
        
        # Try to use the full IntelligenceCore first
        try:
            _core_instance = IntelligenceCore(config)
            print("✅ Using full IntelligenceCore with O*NET data")
        except Exception as e:
            print(f"⚠️  Failed to load full IntelligenceCore: {e}")
            print("🔄 Falling back to simplified IntelligenceCore")
            _core_instance = FallbackIntelligenceCore(config)
    
    return _core_instance