# Model Card — Bridgr Readiness Scorer

## Model details

- **Name:** Bridgr Readiness Scorer
- **Version:** SCORING_VERSION = v1.0
- **Type:** Rule-based scoring engine + NLP skill extractor
- **Last updated:** 2026-07

## Intended use

This system is designed to help **an individual understand their own readiness
for a role they are considering applying for.** It provides three scores (Screen,
Interview, Job) with evidence citations so the person can see exactly what is
and isn't demonstrated in their resume.

### In-scope use

- A person uploads their own resume to understand their own gaps.
- A career coach uses the output as a starting point for a conversation.
- A researcher studies the relationship between resume presentation and
  automated readiness assessment.

### Out-of-scope use

**This system must not be used to screen or rank candidates.** It is designed
to advise a person about themselves, not to make hiring decisions or rank
applicants against each other. Specific out-of-scope uses include:

- Automated candidate filtering or shortlisting
- Ranking candidates in a hiring pipeline
- Replacing human judgment in any employment decision
- Inferring protected characteristics from resume text
- Any use where the person has not consented to their resume being processed

## Evaluation

See `evals/` for the full evaluation harness.

| Metric                     | Value      | Notes                                    |
|----------------------------|------------|------------------------------------------|
| Skill extraction F1        | TBD        | Run `evals/run_all.py` after labelling   |
| Human ceiling (α)          | TBD        | Krippendorff's alpha, pairwise study     |
| Presentation variance      | TBD        | Within-candidate score range             |
| Non-native phrasing penalty| TBD        | Fairness metric from presentation study  |

## Limitations

1. **Evidence level is approximate.** Tenure estimates use regex heuristics on
   date strings. Unusual formats may produce incorrect tenure, which affects
   the evidence level (2 vs. 3).

2. **Skill taxonomy is closed.** Skills not in the taxonomy are dropped, not
   accepted. This reduces false positives but may miss emerging skills.

3. **No protected characteristic modeling.** The system does not model, detect,
   or adjust for protected characteristics. The presentation variance study
   measures the non-native phrasing penalty as a proxy for one fairness concern,
   but this is not a comprehensive fairness evaluation.

4. **Scoring formula thresholds are assumed.** See `ASSUMPTIONS.md`. Most
   thresholds (recency decay windows, evidence level boundaries) are based on
   judgment, not measured data. The evaluation harness is designed to measure
   these empirically — until that data exists, treat all numbers with skepticism.

5. **LLM fallback for unknown roles.** When a role is not in O*NET, the system
   calls Gemini or Groq to generate a skill profile. LLM outputs are not
   validated against a ground truth and may be inaccurate for niche roles.

6. **Presentation bias in variants.** The presentation variance study uses
   rule-based variant generation. The transformation rules encode the author's
   stylistic priors and may not represent real-world presentation diversity.

## Training data

The scoring engine is not trained — it is a deterministic rule-based system.
The NLP components (spaCy, sentence-transformers/all-MiniLM-L6-v2) use
publicly released pre-trained models. See their respective model cards for
training data details.

The skill taxonomy is derived from the O*NET 30.2 database, published by the
U.S. Department of Labor.

## Ethical considerations

- Users should be informed that scores are estimates, not ground truth.
- The non-native phrasing penalty (measured in `evals/presentation_study/`)
  is a concrete fairness concern. Until that number is measured and found
  acceptable, the system should not be used in any context where phrasing
  differences could disadvantage non-native speakers.
- The human ceiling study measures the inherent difficulty of the task. If
  human raters disagree substantially, that is evidence the task is
  fundamentally ambiguous — not that the system should try harder.
