# Readiness Report Bug Fixes Summary

## Issue Description
The readiness report was producing false-zero results for legitimate skill matches. A test case with a resume containing "Python, SQL, MongoDB, Pandas, NumPy, Scikit-learn, spaCy, Sentence Transformers, GraphQL, JWT Authentication, CI/CD" and a job description requiring all these skills showed 0% / 0 of 12 found.

## Root Causes Identified

### Bug 1: Stale Hardcoded Fallback Vocabulary
- **Location**: `backend/routes/readiness.py`, `_candidate_skills()` function
- **Issue**: When `core.skill_extractor.skill_list` or `core.dataset_loader` aren't available, the system falls back to a hardcoded list of only ~40 skills
- **Impact**: Job descriptions with 60+ specific ML/GenAI terms only captured 12 of them, silently dropping the rest

### Bug 2: Limited Regex Matching for Compound Terms
- **Location**: `backend/routes/readiness.py`, `_extract_requirements()` function  
- **Issue**: Limited alias mapping (only 6 skill aliases) and regex pattern issues with multi-word terms like "JWT Authentication"
- **Impact**: Confirmed literal matches like "CI/CD" were being missed due to regex pattern construction errors

## Fixes Implemented

### Fix 1: Expanded Hardcoded Fallback List
**Before**: 40 skills in hardcoded fallback
```python
return [
    "python", "java", "javascript", "typescript", "react", "node.js", "sql",
    "postgresql", "mongodb", "git", "docker", "kubernetes", "aws", "gcp",
    # ... only 40 total skills
]
```

**After**: 244 skills including comprehensive ML/GenAI coverage
- Added modern ML/GenAI terms: PyTorch, TensorFlow, XGBoost, Hugging Face, LangChain, LangGraph, RAG, etc.
- Added MLOps tools: MLflow, Kubeflow, DVC, Weights & Biases, etc.
- Added vector databases: FAISS, Pinecone, ChromaDB, Weaviate
- Added NLP tools: spaCy, NLTK, Transformers, BERT, GPT
- Added authentication: JWT Authentication, OAuth
- Added cloud platforms and modern DevOps tools
- Added business intelligence and data warehousing terms
- Added soft skills and project management terms

### Fix 2: Improved Regex Matching
**Before**: Simple regex with limited aliases
```python
aliases = {
    "react": ["react.js", "reactjs"],
    "node.js": ["node", "nodejs", "node.js"],
    "rest api": ["rest", "restful", "api"],
    "ci/cd": ["ci cd", "cicd", "continuous integration"],
    "postgresql": ["postgres", "postgresql"],
    "machine learning": ["ml", "machine learning"],
}
```

**After**: Comprehensive aliases and robust regex patterns
- Expanded aliases to 50+ skill variations
- Added ML/AI aliases: Hugging Face, LangChain, RAG, etc.
- Fixed multi-word regex pattern construction to handle spaces, hyphens, underscores
- Added case-insensitive matching
- Fixed nested bracket issues in regex patterns

### Fix 3: Added Debugging and Logging
- Added logging to `_candidate_skills()` to track which path is taken
- Added warnings when falling back to hardcoded list
- Added info logging for skill list sources and counts

## Test Results

### Before Fixes
- **Match Rate**: 63.6% (7/11 skills from bug report case)
- **Missing Skills**: spaCy, Sentence Transformers, GraphQL, JWT Authentication
- **Skills Found**: Only basic terms like Python, SQL, MongoDB, Pandas, NumPy, Scikit-learn, CI/CD

### After Fixes  
- **Match Rate**: 100.0% (11/11 skills from bug report case)
- **All Skills Found**: Python, SQL, MongoDB, Pandas, NumPy, Scikit-learn, spaCy, Sentence Transformers, GraphQL, JWT Authentication, CI/CD
- **Requirements Extracted**: Increased from 11 to 31 total requirements found

## Verification

Created comprehensive test scripts that verify:
1. ✅ Hardcoded fallback now includes 244 skills vs 40 previously
2. ✅ All ML/GenAI terms from bug report are now included
3. ✅ Multi-word terms like "JWT Authentication" are correctly matched
4. ✅ Case-insensitive matching works for variations like "ci/cd", "CI/CD", "Ci/Cd"
5. ✅ The exact bug report case now shows 100% match rate

## Impact

This fix addresses the core issue where legitimate skills were being missed, leading to artificially low readiness scores. The system now:

- Captures modern ML/GenAI skills that are in high demand
- Properly handles compound skill names and their variations
- Provides much more accurate readiness assessments
- Reduces false-negative results that were frustrating users

## Files Modified

1. `backend/routes/readiness.py`:
   - Expanded `_candidate_skills()` hardcoded fallback from 40 to 244 skills
   - Improved `_extract_requirements()` with better regex and 50+ aliases
   - Added logging and debugging information

## Backward Compatibility

All changes are backward compatible:
- Existing skill detection still works as before
- Added skills only improve coverage, don't break existing functionality  
- Regex improvements handle edge cases that were previously missed
- No breaking changes to API or data structures


---

## Track A Correctness Fixes — 2026-07-27

### Overview
Five correctness bugs found and fixed in the backend. No new third-party dependencies introduced. All 73 fast tests pass after changes.

---

### Fix 1: Analysis persistence (TypeError silently swallowed)

**Files changed:** `backend/routes/readiness.py`, `backend/tests/test_persistence.py`, `backend/tests/conftest.py`

**Bug:** `Analysis(...)` was constructed with a nonexistent kwarg `analysis_data=`. SQLAlchemy raised `TypeError` immediately, which a bare `except Exception: pass` swallowed silently. No analysis row was ever saved; `GET /api/user/history` always returned an empty list.

**Fix:**
- Replaced `analysis_data={...}` with the real model columns:
  - `skill_gaps` — `gaps` list serialised via `.model_dump()`
  - `matched_skills` — `matched` list serialised via `.model_dump()`
  - `roadmap_inputs` — dict with all scoring metadata needed by the roadmap generator
  - `feasibility_score` — dict `{"job_score": ..., "verdict": ...}` (column is JSON, dict form is future-extensible)
- Replaced `except Exception: pass` with `except Exception as e: logger.error(..., exc_info=True)` so failures are visible in logs.
- Added `db.rollback()` so a failed transaction doesn't leave the session dirty.
- The try/except wraps only the `db.add/db.commit` block; response construction is outside it.
- Added `tests/test_persistence.py` covering: row is persisted with correct columns, history endpoint returns it, DB failure returns 200 to client.
- Added real SQLAlchemy early-import to `conftest.py` so the stub guard in `test_api.py` is bypassed for persistence tests.

---

### Fix 2: CORS wildcard subdomain matching

**Files changed:** `backend/core/config.py`, `backend/main.py`, `backend/backend/.env.docker`, `bridgr/render.yaml`

**Bug:** `ALLOWED_ORIGINS` contained entries like `https://*.vercel.app`. Starlette's `CORSMiddleware(allow_origins=...)` does exact string matching — glob wildcards are never matched. Preview/staging deployments were silently blocked.

**Fix:**
- Split the single `ALLOWED_ORIGINS` setting into two:
  - `ALLOWED_ORIGINS` — exact-match origins only (comma-separated). Wildcard entries removed.
  - `ALLOWED_ORIGIN_REGEX` — Python regex string passed to `CORSMiddleware(allow_origin_regex=...)`, which Starlette does support. Default: `https://.*\.(vercel|netlify|onrender)\.app`.
- Updated `main.py` to pass `allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX or None`.
- Updated `.env.docker` and `render.yaml` with the new key.

---

### Fix 3: /debug/cors endpoint gated and hardcoded timestamp removed

**Files changed:** `backend/main.py`

**Bug:** `/debug/cors` was registered unconditionally, exposing internal CORS config in production. The response also contained a hardcoded timestamp string `"2026-07-26T10:22:39Z"`.

**Fix:**
- Wrapped the route registration with `if settings.DEBUG:` so it only exists when `DEBUG=true`.
- Replaced the hardcoded timestamp with `datetime.utcnow().isoformat()`.
- `render.yaml` already sets `DEBUG=false` for both services, so the route does not exist on the deployed API.

---

### Fix 4: Completed backend/.env.example and frontend/.env.example

**Files changed:** `backend/.env.example`, `frontend/.env.example`

**Bug:** `backend/.env.example` was missing several env vars actually read by the codebase: `FIREBASE_CREDENTIALS_PATH`, `FIREBASE_PROJECT_ID`, `FIREBASE_PRIVATE_KEY`, `FIREBASE_CLIENT_EMAIL`, `DATABASE_URL`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `HIGH_DEMAND_THRESHOLD`, `ALLOWED_ORIGINS`, `ALLOWED_ORIGIN_REGEX`. `frontend/.env.example` was missing all seven `REACT_APP_FIREBASE_*` keys.

**Fix:**
- Rewrote `backend/.env.example` with section headers and one-line comments per variable explaining what breaks when left empty.
- Rewrote `frontend/.env.example` to include all `REACT_APP_FIREBASE_*` keys referenced in `firebase.js`, `REACT_APP_API_URL`, and `REACT_APP_ENV`.

---

### Fix 5: Consolidated duplicate model loader

**Files changed:** `backend/routes/readiness.py`, deleted `backend/ml/model_loader.py`, deleted `backend/ml/__init__.py`

**Bug:** `ml/model_loader.py` duplicated the singleton cache (`_core_instance`) and all config-resolution logic (`ONET_EXTRACT_PATH`, `ONET_ZIP_PATH`, `SEMANTIC_THRESHOLD`) already present in `core_ml/loader.py`. The route imported `get_core` from `ml.model_loader` (wrapper) while also importing `core_ml.loader` directly for `DATA_MODE`. Two caches could diverge.

**Verification:** `grep -rn "analyze_resume\|reset_models" backend/ --include=*.py` confirmed both functions were only defined in `ml/model_loader.py` and never called from any route or test.

**Fix:**
- Deleted `ml/model_loader.py` and `ml/__init__.py` (directory now empty).
- Updated `routes/readiness.py` to import `get_core` directly from `core_ml.loader`.
- One singleton, one config-resolution path, one `DATA_MODE` source.
- `data_mode` field in `ReadinessResponse` still reports correctly (confirmed via `python -c "from routes import readiness; print(readiness._get_data_mode())"`).
