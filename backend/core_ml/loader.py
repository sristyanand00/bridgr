"""Singleton loader for IntelligenceCore with fallback support."""

from __future__ import annotations
import logging
import os
from typing import Union, Optional

from .core import IntelligenceCore
from .fallback import FallbackIntelligenceCore

logger = logging.getLogger(__name__)

_core_instance: Optional[Union[IntelligenceCore, FallbackIntelligenceCore]] = None


def get_core(force_reload: bool = False) -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    """
    Get the ML core singleton. Tries IntelligenceCore (O*NET), falls back to FallbackIntelligenceCore.
    """
    global _core_instance
    if _core_instance is None or force_reload:
        config = {
            "ONET_EXTRACT_PATH":  os.getenv("ONET_EXTRACT_PATH",  "data/"),
            "ONET_ZIP_PATH":      os.getenv("ONET_ZIP_PATH",       ""),
            "SEMANTIC_THRESHOLD": float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY":     os.getenv("OPENAI_API_KEY",      ""),
            "DATA_DIR":           os.getenv("DATA_DIR",            "data/"),
        }
        try:
            logger.info("Using full IntelligenceCore (dataset loaded)")
            _core_instance = IntelligenceCore(config)
        except Exception as e:
            logger.warning(f"Full core failed ({e}).")
            logger.warning("Using FallbackIntelligenceCore (15 built-in roles, no dataset needed).")
            _core_instance = FallbackIntelligenceCore(config)
    return _core_instance


def reset_core() -> None:
    """Reset the singleton core — next get_core() will reinitialise."""
    global _core_instance
    _core_instance = None
    logger.info("Core reset — next get_core() will reinitialise.")
