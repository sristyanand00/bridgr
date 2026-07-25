"""
Spearman correlation: model ranking vs. human-derived Bradley-Terry ranking.

Usage:
    python compare.py

Reads bt_scores.json (from bradley_terry.py) and model_scores.json.
model_scores.json format:
    [{"candidate_id": "c01", "interview_score": 72.5}, ...]

Prints Spearman rho and p-value, and a rank comparison table.
"""

from __future__ import annotations
import json
from pathlib import Path

import numpy as np
from scipy import stats  # scipy is already in requirements via scikit-learn

BT_SCORES_FILE    = Path(__file__).parent / "bt_scores.json"
MODEL_SCORES_FILE = Path(__file__).parent / "model_scores.json"


def _load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def main() -> None:
    if not BT_SCORES_FILE.exists():
        print("bt_scores.json not found. Run bradley_terry.py first.")
        return
    if not MODEL_SCORES_FILE.exists():
        print("model_scores.json not found. Score all candidates first.")
        return

    bt     = {e["candidate_id"]: e["bt_score"]       for e in _load_json(BT_SCORES_FILE)}
    model  = {e["candidate_id"]: e["interview_score"] for e in _load_json(MODEL_SCORES_FILE)}

    common = sorted(set(bt) & set(model))
    if len(common) < 3:
        print(f"Only {len(common)} candidates in common — need ≥3 for correlation.")
        return

    bt_scores    = [bt[c]    for c in common]
    model_scores = [model[c] for c in common]

    rho, pval = stats.spearmanr(bt_scores, model_scores)

    print(f"\nSpearman correlation (model vs. human ranking)")
    print(f"  Candidates compared: {len(common)}")
    print(f"  ρ = {rho:.3f}   p = {pval:.4f}")

    if pval < 0.05:
        print("  Significant correlation (p < 0.05).")
    else:
        print("  Not statistically significant — more data needed.")

    # Rank comparison table
    bt_ranks    = {c: r + 1 for r, c in enumerate(sorted(common, key=lambda x: bt[x],    reverse=True))}
    model_ranks = {c: r + 1 for r, c in enumerate(sorted(common, key=lambda x: model[x], reverse=True))}

    print(f"\n{'Candidate':<20} {'BT Rank':>8} {'Model Rank':>11} {'Δ Rank':>8}")
    print("─" * 52)
    for c in sorted(common, key=lambda x: bt_ranks[x]):
        delta = model_ranks[c] - bt_ranks[c]
        sign  = "+" if delta > 0 else ""
        print(f"{c:<20} {bt_ranks[c]:>8} {model_ranks[c]:>11} {sign}{delta:>7}")


if __name__ == "__main__":
    main()
