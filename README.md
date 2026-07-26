# Bridgr

Role-readiness scoring system. Upload your resume and real job postings — get three honest scores (Screen, Interview, Job) where every point traces to a specific requirement and a cited line of your resume.

---

## Results

> Run `python evals/run_all.py` to reproduce all numbers below.

### Skill extraction (F1 on 100 labelled examples)

| Approach         |    P |    R |   F1 | ±95% CI |
|------------------|-----:|-----:|-----:|---------|
| regex_baseline   |      |      |      | pending — label 100 examples first |
| bm25_baseline    |      |      |      | pending |
| embedding_only   |      |      |      | pending |
| full_cascade     |      |      |      | pending |

### Human ceiling (Krippendorff's alpha)

| Study                 | α    | Interpretation |
|-----------------------|------|----------------|
| Pairwise readiness    |      | pending — recruit 2+ raters |

Alpha is the ceiling for any automated system in this category.
A low value is a finding about the problem, not a failure.

### Presentation variance

| Metric                         | Value   |
|--------------------------------|---------|
| Between-candidate variance     | pending |
| Within-candidate (phrasing)    | pending |
| Presentation effect ratio      | pending |
| Non-native phrasing penalty    | pending |

> Run `python evals/presentation_study/run_study.py` and `decompose.py` to fill these in.

### Engineering

| Metric           | Value |
|------------------|-------|
| Test count       | 82 passing, 1 skipped |
| Coverage (core_ml) | run `pytest --cov=core_ml` |
| CI               | [![Tests](https://github.com/zaryab-tech/bridgr/actions/workflows/test.yml/badge.svg)](https://github.com/zaryab-tech/bridgr/actions/workflows/test.yml) |

---

## Why the scoring engine is deterministic

The scoring engine (`core_ml/scoring.py`) is a pure function: given the same
input it produces byte-identical output every time. No LLM call, no
`datetime.now()`, no network. `today` is a parameter.

This matters because it means presentation variance is measurable and
attributable. When the score changes, it's because the resume changed — not
because a model had a different day.

---

## Architecture

```
frontend/          React app (upload UI, score display)
backend/
  routes/          FastAPI endpoints (validate → parse → extract → score)
  core_ml/         Pure ML/scoring modules (no I/O)
    parser.py      PDF text extraction and section detection
    extractor.py   Skill extraction (phrase → semantic → MiniLM)
    evidence.py    Context-based evidence levelling (0–4)
    scoring.py     Pure scoring engine (SCORING_VERSION = v1.0)
    loader.py      Singleton core initialisation
  ml/              Model loader (wires core_ml to the route)
  services/        LLM service (lazy-loaded, never touches scores)
evals/             Evaluation harness (label, run, sweep, human study)
scripts/           Data setup
```

---

## What doesn't work yet

- Evidence levelling uses date heuristics, not a proper date parser — tenure
  estimates may be off by a few months for unusual formats.
- The `_evidence_level` default of 12 months professional tenure means a skill
  in the experience section always reaches at least level 3 if the verb is
  strong, even if the actual tenure was 2 months.
- O*NET sample covers 50 occupations; rare roles fall through to the LLM
  fallback, which is slower and requires an API key.
- `google-generativeai` and `groq` are in requirements but only loaded lazily
  (inside `analyze_resume`). Tests mock them; production needs real keys.
- The human study requires manual recruitment — it cannot be automated.
- Presentation variant generation uses rule-based transformations. The
  stylistic priors are the author's. LLM-generated variants would be a better
  (but costlier) study design.

---

## Setup

### Prerequisites

- Python 3.11
- Node 20
- Firebase project (for auth)
- Optional: Gemini and/or Groq API keys (for unknown-role fallback)

### 1. Clone and configure

```bash
git clone <repo-url>
cd bridgr
cp backend/.env.example backend/.env
# Fill in FIREBASE_*, GEMINI_API_KEY (optional), GROQ_API_KEY (optional)
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The app starts immediately using the 50-occupation sample.
For all 1,000+ occupations:

```bash
python scripts/setup_data.py
# Then set ONET_EXTRACT_PATH in backend/.env
```

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

### 4. Docker (both services at once)

```bash
docker-compose up --build
```

### 5. Run tests

```bash
cd backend
pytest tests/ -v --cov=core_ml
```

---

## API

`POST /api/readiness` — resume readiness scoring
`GET  /health`        — health check
`GET  /`              — API status

---

## Contributing

1. Fork and create a branch
2. `pytest tests/` must pass before submitting
3. No new dependencies without discussion
4. Read `.kiro/steering/project.md` — the hard rules apply to all contributions

## License

MIT
