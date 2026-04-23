# backend/ml/model_loader.py

import os
from dotenv import load_dotenv
from backend.services.intelligence_core import IntelligenceCore

load_dotenv()

# This is created ONCE when the module is imported.
# FastAPI imports this at startup and reuses the instance.
_core_instance: IntelligenceCore | None = None


def get_core() -> IntelligenceCore:
    global _core_instance
    if _core_instance is None:
        config = {
            "ONET_ZIP_PATH":       os.getenv("ONET_ZIP_PATH", "data/raw/db_30_2_text.zip"),
            "ONET_EXTRACT_PATH":   os.getenv("ONET_EXTRACT_PATH", "data/"),
            "SEMANTIC_THRESHOLD":  float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "ANTHROPIC_API_KEY":   os.getenv("ANTHROPIC_API_KEY", ""),
        }
        _core_instance = IntelligenceCore(config)
    return _core_instance