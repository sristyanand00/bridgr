# Assumptions

Every threshold in the codebase, marked MEASURED or ASSUMED, with the basis.

A threshold marked ASSUMED was set by judgment and should be replaced with a
measured value once the evaluation harness has enough labelled data.

---

## Scoring engine (`core_ml/scoring.py`)

| Threshold | Value | Status | Basis |
|-----------|-------|--------|-------|
| Recency decay ≤18 months | mult = 1.0 | ASSUMED | Skills used within 18 months are considered current; no decay applied. Loosely follows typical "recent experience" language in job postings. |
| Recency decay ≤36 months | mult = 0.90 | ASSUMED | 10% discount for skills not used in 1.5–3 years. Arbitrary; needs empirical grounding. |
| Recency decay ≤60 months | mult = 0.75 | ASSUMED | 25% discount for 3–5 year gap. Arbitrary. |
| Recency decay >60 months | mult = 0.60 | ASSUMED | 40% discount for skills >5 years stale. Arbitrary. |
| Hard blocker — screen cap | 40.0 | ASSUMED | A missing hard requirement (visa, clearance) caps screen at 40. The value 40 was chosen to signal "do not proceed" while preserving the information that the candidate has other skills. |
| Hard blocker — interview/job cap | 55.0 | ASSUMED | Same reasoning. 55 is below the "developing" threshold so blockers always produce a non-passing verdict. |
| Verdict threshold "ready" | interview ≥ 80 | ASSUMED | 80% match considered interview-ready. No empirical basis. |
| Verdict threshold "developing" | interview ≥ 50 | ASSUMED | 50–79% match. Arbitrary split. |
| Verdict threshold "early" | interview < 50 | ASSUMED | Below 50%. |

---

## Evidence levelling (`core_ml/evidence.py`)

| Threshold | Value | Status | Basis |
|-----------|-------|--------|-------|
| Minimum tenure for level 3 | 6 months | ASSUMED | Six months of professional use is a common threshold in job postings ("6 months experience"). No empirical validation. |
| Minimum tenure for level 4 (via tenure alone) | >24 months | ASSUMED | Two years is a common boundary between "familiar" and "deep expertise" in seniority frameworks. Arbitrary. |
| Scope marker patterns | see SCOPE_PATTERNS | ASSUMED | Patterns capture common scale indicators (user counts, cluster sizes, SLA %). Coverage is incomplete — e.g., financial metrics using non-standard units would be missed. |

---

## Skill extractor (`core_ml/extractor.py`)

| Threshold | Value | Status | Basis |
|-----------|-------|--------|-------|
| Semantic similarity threshold (tier 2) | 0.75 | ASSUMED | Chosen to balance precision/recall on informal testing. The sweep in `evals/sweep_threshold.py` is designed to measure the optimal value. Replace 0.75 with the measured peak once 100 labelled examples exist. |
| Tier 3 fallback threshold | 0.70 | ASSUMED | Slightly looser than tier 2 to catch skills that appear in short window contexts. Not independently validated. |
| Minimum skill count before tier 3 | 8 | ASSUMED | If fewer than 8 skills are found, tier 3 activates. Threshold raised from 5 during Phase 2; not measured. |

---

## Route (`routes/readiness.py`)

| Threshold | Value | Status | Basis |
|-----------|-------|--------|-------|
| Top N requirements | 18 | ASSUMED | Top 18 skills from job postings. Arbitrary cap to keep the output readable. |
| Required level threshold | count ≥ max(2, n_postings//2) → level 3, else level 2 | ASSUMED | Skills appearing in half or more of postings are treated as "required at depth". Heuristic. |
| Criticality | 1.0 (constant) | ASSUMED | constant placeholder — no signal available to distinguish critical from nice-to-have requirements yet. Until a real signal exists, weight == frequency. |
| Max file size | 10 MB | ASSUMED | Resumes are rarely >1 MB; 10 MB is a safety ceiling for adversarial inputs. |
| Default tenure (no date found) | 12 months | ASSUMED | When no date range is parseable in the context, 12 months is assumed so professional experience isn't unfairly capped at level 2. Conservative but not validated. |

---

## Updating thresholds

To replace an ASSUMED threshold with a MEASURED one:

1. Label enough examples to make the measurement meaningful (≥100 for F1, ≥40
   pairs for human study).
2. Run the relevant eval script (`run_all.py`, `sweep_threshold.py`).
3. Update the threshold value in code.
4. Update this file: change ASSUMED → MEASURED and record the measurement
   basis (dataset size, metric, date).
5. Re-run the full test suite to confirm no regressions.
