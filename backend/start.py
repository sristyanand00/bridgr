"""
Startup shim for environments where ML packages (spacy, sentence-transformers,
torch, sklearn) are not installed — e.g. Python 3.14 where spacy/thinc don't
yet have wheels.

The API, PDF parsing, scoring engine, and all evidence logic run fine without
them.  The ML models (SkillExtractor, MatchingEngine) load lazily on the first
/api/readiness request; if the deps are absent, the server falls back to
FallbackIntelligenceCore which uses the built-in 50-occupation sample.

Usage:
    python start.py              # development (--reload)
    python start.py --no-reload  # production-style
"""
import sys
from unittest.mock import MagicMock

# ── Stub ML packages that don't build on Python 3.14 ──────────────────────
_ML_STUBS = [
    "spacy", "spacy.matcher", "spacy.util", "spacy.lang", "spacy.lang.en",
    "sentence_transformers",
    "sklearn", "sklearn.metrics", "sklearn.metrics.pairwise",
    "torch", "thinc",
    "google", "google.generativeai",
    "groq",
    "firebase_admin", "firebase_admin.credentials", "firebase_admin.auth",
]
for _mod in _ML_STUBS:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

# ── Launch uvicorn ─────────────────────────────────────────────────────────
import uvicorn  # noqa: E402

if __name__ == "__main__":
    reload = "--no-reload" not in sys.argv
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=reload,
    )
