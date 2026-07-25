# backend/services/__init__.py
# Lazy import — don't pull google/groq at import time; callers import explicitly.
__all__ = ['llm_service']