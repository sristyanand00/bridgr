"""
Variance decomposition: between-candidate vs. within-candidate (presentation effect).

Usage:
    python decompose.py --results results.json

Prints:
  - Between-candidate variance  (real capability differences)
  - Within-candidate variance   (pure presentation effect)
  - Ratio: presentation effect / total variance
  - Mean score range within candidates
  - Non-native variant separately (fairness number)

Limitation: variant generation was rule-based and my stylistic priors are
baked into the transformation rules. The true presentation effect may differ
with LLM-generated variants or human rewrites.
"""

from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np

VARIANT_NAMES = ("terse", "verbose", "metric_heavy", "jargon_heavy", "non_native")


def load_results(path: Path) -> list:
    with open(path) as f:
        return json.load(f)


def decompose(results: list, score_key: str = "interview_score") -> dict:
    """
    One-way ANOVA decomposition.

    Between-candidate SS: variance due to who the candidate is.
    Within-candidate SS:  variance due to how they wrote it (presentation).
    """
    # Group by candidate
    by_candidate: Dict[str, List[float]] = defaultdict(list)
    for r in results:
        by_candidate[r["candidate_id"]].append(r[score_key])

    candidates     = sorted(by_candidate.keys())
    n_candidates   = len(candidates)
    all_scores     = [s for scores in by_candidate.values() for s in scores]
    grand_mean     = np.mean(all_scores)
    n_total        = len(all_scores)

    # Between-candidate: how much candidates differ from each other
    ss_between = sum(
        len(by_candidate[c]) * (np.mean(by_candidate[c]) - grand_mean) ** 2
        for c in candidates
    )

    # Within-candidate: how much a candidate's variants differ from their own mean
    ss_within = sum(
        (s - np.mean(by_candidate[c])) ** 2
        for c in candidates
        for s in by_candidate[c]
    )

    ss_total = ss_between + ss_within

    # Degrees of freedom
    df_between = n_candidates - 1
    df_within  = n_total - n_candidates

    ms_between = ss_between / df_between if df_between > 0 else 0
    ms_within  = ss_within  / df_within  if df_within  > 0 else 0

    # F-statistic (is between-candidate variance significant?)
    f_stat = ms_between / ms_within if ms_within > 0 else float("inf")

    # Presentation effect ratio: proportion of total variance within candidates
    presentation_ratio = ss_within / ss_total if ss_total > 0 else 0

    # Score range per candidate
    ranges = {c: max(by_candidate[c]) - min(by_candidate[c]) for c in candidates}
    mean_range = np.mean(list(ranges.values()))

    # Non-native variant scores separately
    non_native_scores = [r[score_key] for r in results if r["variant"] == "non_native"]
    other_scores      = [r[score_key] for r in results if r["variant"] != "non_native"]

    non_native_mean = np.mean(non_native_scores) if non_native_scores else None
    other_mean      = np.mean(other_scores)      if other_scores      else None
    non_native_gap  = (other_mean - non_native_mean) if (non_native_mean is not None and other_mean is not None) else None

    return {
        "n_candidates":         n_candidates,
        "n_variants":           len(set(r["variant"] for r in results)),
        "grand_mean":           float(grand_mean),
        "ss_between":           float(ss_between),
        "ss_within":            float(ss_within),
        "ss_total":             float(ss_total),
        "ms_between":           float(ms_between),
        "ms_within":            float(ms_within),
        "f_statistic":          float(f_stat),
        "presentation_ratio":   float(presentation_ratio),
        "mean_score_range":     float(mean_range),
        "per_candidate_ranges": {c: float(v) for c, v in ranges.items()},
        "non_native_mean":      float(non_native_mean) if non_native_mean is not None else None,
        "other_variants_mean":  float(other_mean)      if other_mean      is not None else None,
        "non_native_gap":       float(non_native_gap)  if non_native_gap  is not None else None,
    }


def print_report(stats: dict) -> None:
    print("\n── Variance Decomposition ──────────────────────────────────────")
    print(f"  Candidates:           {stats['n_candidates']}")
    print(f"  Variants per person:  {stats['n_variants']}")
    print(f"  Grand mean score:     {stats['grand_mean']:.2f}")
    print()
    print(f"  Between-candidate SS: {stats['ss_between']:.2f}  (real capability)")
    print(f"  Within-candidate SS:  {stats['ss_within']:.2f}   (presentation effect)")
    print(f"  Presentation ratio:   {stats['presentation_ratio']:.1%} of total variance")
    print(f"  Mean score range:     {stats['mean_score_range']:.2f} points (same person, 5 styles)")
    print()

    if stats["non_native_gap"] is not None:
        print(f"  ── Fairness: non-native phrasing ──")
        print(f"  Non-native mean score:  {stats['non_native_mean']:.2f}")
        print(f"  Other variants mean:    {stats['other_variants_mean']:.2f}")
        print(f"  Gap (penalty):          {stats['non_native_gap']:+.2f} points")
        if stats["non_native_gap"] > 3:
            print("  ⚠ Non-native phrasing causes a meaningful score penalty.")
        else:
            print("  ✓ Non-native phrasing has minimal score impact.")

    print()
    print("  Limitation: variant rules encode the author's stylistic priors.")
    print("  Results may differ with LLM-generated or human-written variants.")
    print("────────────────────────────────────────────────────────────────")


def main() -> None:
    parser = argparse.ArgumentParser(description="Variance decomposition")
    parser.add_argument("--results",   default="results.json")
    parser.add_argument("--score-key", default="interview_score",
                        choices=["screen_score", "interview_score", "job_score"])
    args = parser.parse_args()

    results = load_results(Path(args.results))
    if not results:
        print("No results found.")
        return

    stats = decompose(results, score_key=args.score_key)
    print_report(stats)


if __name__ == "__main__":
    main()
