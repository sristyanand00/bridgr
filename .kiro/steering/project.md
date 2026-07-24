# Bridgr — Project Rules

## What this is
A role-readiness scoring system. A user uploads a resume and real job postings; the system extracts demonstrated skills with evidence levels and produces three separate scores — Screen, Interview, Job — where every point traces to a specific requirement and a cited line of the resume.

## The commitment
This product's premise is that it tells the truth when other tools don't. If a choice makes output more flattering but less accurate, choose accuracy.

## Hard rules — violating any of these is a bug
1. The scoring engine is a PURE function. No I/O, no network, no LLM calls,
   no datetime.now() — today is a parameter. Same input, same output, always.
2. No LLM produces a number that feeds a score. Models may read numbers and
   write sentences. They never do arithmetic.
3. Skills resolve against a closed taxonomy. Any model output not in the
   taxonomy is dropped, not accepted.
4. Evidence level comes from CONTEXT — section, verb strength, duration,
   scope markers — never from extraction confidence.
5. Every score record stores SCORING_VERSION.
6. User corrections outrank the parser permanently and are never overwritten.
7. Never delete files outside the explicit scope of the current task.

## Scope discipline
Do exactly what the current task asks. Do not add features, refactor adjacent code, or "improve" things not mentioned. If you think something else needs fixing, say so and wait — do not act.

## Stack
Python 3.11, FastAPI, pydantic, spaCy, sentence-transformers, scikit-learn, pandas, pytest. React frontend. Do NOT add new dependencies without asking.

## Style
- Type hints everywhere. `logging`, never `print()`.
- Functions under 50 lines. Modules under 400 lines.
- Every non-obvious decision gets a one-line comment explaining WHY.

## After every task
End your response with a plain-language summary of what you changed and why, written so a non-expert could follow it. Then list anything you noticed that is broken but out of scope.
