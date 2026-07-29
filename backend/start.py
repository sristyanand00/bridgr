"""
Startup shim for environments where ML packages (spacy, sentence-transformers,
torch, sklearn) are not installed — e.g. Python 3.14 where spacy/thinc don't
yet have wheels.

The API, PDF parsing, scoring engine, and all evidence logic run fine without
them.  The ML models (SkillExtractor, MatchingEngine) load lazily on the first
/api/readiness request; if the deps are absent, the server falls back to
FallbackIntelligenceCore which uses the built-in 50-occupation sample.

IMPORTANT: the stubs below are installed ONLY when the real packages are
missing.  Stubbing them unconditionally shadows a perfectly good ML install
with MagicMocks, and because a MagicMock iterates as empty rather than raising,
SkillExtractor silently returns zero skills and every readiness score comes
back as 0%.  The `import spacy` probe is what keeps that from happening — do
not remove it.

Usage:
    python start.py              # development (--reload)
    python start.py --no-reload  # production-style
"""
import sys

# ── Stub ML packages that don't build on Python 3.14 ──────────────────────
# Probe for the real thing first.  spacy is the canonical marker: it pulls in
# thinc/numpy and is the dependency that actually lacks 3.14 wheels.
try:
    import spacy  # noqa: F401 — real packages present, nothing to stub
except ImportError:
    from unittest.mock import MagicMock

    print("⚠️  WARNING: ML packages not available - using stubs!")
    print("   Skill extraction will return NO skills and all scores will be 0%.")
    print("   Install the real deps: pip install -r requirements.txt")

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
