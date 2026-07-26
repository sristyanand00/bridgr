"""Singleton loader for IntelligenceCore with fallback support."""

from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Union, Optional

from .core import IntelligenceCore
from .fallback import FallbackIntelligenceCore

logger = logging.getLogger(__name__)

_core_instance: Optional[Union[IntelligenceCore, FallbackIntelligenceCore]] = None

# Exposed so routes can report which dataset backed a score.
# Values: "full" | "sample" | "fallback"
DATA_MODE: str = "fallback"


def get_core(force_reload: bool = False) -> Union[IntelligenceCore, FallbackIntelligenceCore]:
    """
    Get the ML core singleton.

    Load order:
      1. ONET_EXTRACT_PATH (env) → full db_* folder or ZIP
      2. backend/data/           → db_* folder if present
      3. backend/data/sample/    → bundled 50-occupation CSV
      4. FallbackIntelligenceCore (hardcoded 15 roles)
    """
    global _core_instance, DATA_MODE
    if _core_instance is None or force_reload:
        backend_dir = Path(__file__).parent.parent

        # Resolve candidate data directories in priority order
        env_path  = os.getenv("ONET_EXTRACT_PATH", "")
        data_dir  = str(backend_dir / "data")
        candidates = [p for p in [env_path, data_dir] if p]

        config = {
            "ONET_EXTRACT_PATH": candidates[0] if candidates else data_dir,
            "ONET_ZIP_PATH":     os.getenv("ONET_ZIP_PATH", ""),
            "SEMANTIC_THRESHOLD": float(os.getenv("SEMANTIC_THRESHOLD", "0.75")),
            "OPENAI_API_KEY":    os.getenv("OPENAI_API_KEY", ""),
            "DATA_DIR":          data_dir,
        }

        # Try to load IntelligenceCore (handles full → sample internally)
        for candidate in candidates:
            config["ONET_EXTRACT_PATH"] = candidate
            try:
                _core_instance = IntelligenceCore(config)
                # DATA_MODE is set by IntelligenceCore.__init__ via core.DATA_MODE
                from . import core as _core_mod
                DATA_MODE = _core_mod.DATA_MODE
                logger.info("IntelligenceCore ready (data_mode=%s)", DATA_MODE)
                return _core_instance
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.warning("IntelligenceCore init failed for '%s': %s", candidate, e)
                continue

        # Nothing worked — loud fallback
        logger.warning(
            "FALLBACK MODE — O*NET data not found. Scores will be less accurate. "
            "Run: python scripts/setup_data.py"
        )
        DATA_MODE = "fallback"
        _core_instance = FallbackIntelligenceCore(config)

    return _core_instance


def reset_core() -> None:
    """Reset the singleton core — next get_core() will reinitialise."""
    global _core_instance, DATA_MODE
    _core_instance = None
    DATA_MODE = "fallback"
    logger.info("Core reset — next get_core() will reinitialise.")
