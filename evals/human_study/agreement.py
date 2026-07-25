"""
Inter-rater agreement: Krippendorff's alpha across all raters.

Alpha is the CEILING for any automated system in this category.
A low alpha is a finding about the difficulty of the problem, not a failure.

Usage:
    python agreement.py

Reads judgements.json produced by rate.py.
Prints alpha and a per-pair agreement breakdown.

Krippendorff's alpha for ordinal data:
  1.0  = perfect agreement
  0.0  = chance agreement
  <0.0 = systematic disagreement (worse than chance)
  ≥0.8 = generally accepted as reliable
  ≥0.67 = tentatively reliable (Krippendorff's own threshold)
"""

from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

JUDGEMENTS_FILE = Path(__file__).parent / "judgements.json"

# Map choices to ordinal values for alpha calculation
CHOICE_VALUES = {"A": 0, "tie": 0.5, "B": 1}


def load_judgements(path: Path = JUDGEMENTS_FILE) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def build_reliability_matrix(
    judgements: list,
) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Build rater × unit matrix for Krippendorff's alpha.

    Returns:
        matrix: shape (n_raters, n_pairs), NaN where rater didn't rate pair
        raters: list of rater ids
        pairs:  list of pair ids
    """
    # Collect all raters and pairs (excluding overlaps from pair list)
    raters = sorted({j["rater"] for j in judgements})
    pairs  = sorted({j["pair_id"] for j in judgements})

    rater_idx = {r: i for i, r in enumerate(raters)}
    pair_idx  = {p: i for i, p in enumerate(pairs)}

    matrix = np.full((len(raters), len(pairs)), np.nan)

    for j in judgements:
        r = rater_idx[j["rater"]]
        p = pair_idx[j["pair_id"]]
        matrix[r, p] = CHOICE_VALUES.get(j["winner"], np.nan)

    return matrix, raters, pairs


def krippendorffs_alpha(matrix: np.ndarray) -> float:
    """
    Compute Krippendorff's alpha for interval data.

    Formula: alpha = 1 - D_o / D_e
      D_o = observed disagreement
      D_e = expected disagreement
    """
    # Flatten to paired observations (all rater pairs for each unit)
    n_units = matrix.shape[1]

    # Compute observed disagreement
    D_o = 0.0
    n_o = 0
    for unit in range(n_units):
        ratings = matrix[:, unit][~np.isnan(matrix[:, unit])]
        if len(ratings) < 2:
            continue
        for i in range(len(ratings)):
            for j in range(i + 1, len(ratings)):
                D_o += (ratings[i] - ratings[j]) ** 2
                n_o += 1

    if n_o == 0:
        return float("nan")
    D_o /= n_o

    # Compute expected disagreement from marginal distribution
    all_ratings = matrix[~np.isnan(matrix)]
    n_total = len(all_ratings)
    if n_total < 2:
        return float("nan")

    D_e = 0.0
    n_e = 0
    for i in range(n_total):
        for j in range(i + 1, n_total):
            D_e += (all_ratings[i] - all_ratings[j]) ** 2
            n_e += 1
    D_e /= n_e

    if D_e == 0:
        return 1.0  # All raters agreed perfectly

    return 1.0 - D_o / D_e


def pairwise_agreement(judgements: list) -> Dict[str, float]:
    """Per-pair percentage agreement (for overlap pairs)."""
    pair_votes: Dict[str, List[str]] = defaultdict(list)
    for j in judgements:
        pair_votes[j["pair_id"]].append(j["winner"])

    agreement = {}
    for pair_id, votes in pair_votes.items():
        if len(votes) < 2:
            continue
        most_common = max(set(votes), key=votes.count)
        agreement[pair_id] = votes.count(most_common) / len(votes)
    return agreement


def main() -> None:
    judgements = load_judgements()
    if not judgements:
        print("No judgements found. Run rate.py first.")
        return

    raters = sorted({j["rater"] for j in judgements})
    pairs  = sorted({j["pair_id"] for j in judgements})
    print(f"\nRaters: {len(raters)}  —  {', '.join(raters)}")
    print(f"Pairs rated: {len(pairs)}")
    print(f"Total judgements: {len(judgements)}")

    matrix, rater_list, pair_list = build_reliability_matrix(judgements)

    # Only compute alpha if ≥2 raters
    if len(rater_list) < 2:
        print("\nNeed at least 2 raters for Krippendorff's alpha.")
        print("Intra-rater agreement (overlap pairs):")
    else:
        alpha = krippendorffs_alpha(matrix)
        print(f"\nKrippendorff's alpha: {alpha:.3f}")
        if alpha >= 0.8:
            print("Interpretation: Strong agreement — reliable ceiling estimate.")
        elif alpha >= 0.667:
            print("Interpretation: Tentative agreement — usable but note uncertainty.")
        else:
            print("Interpretation: Low agreement — this task is genuinely ambiguous for humans.")
            print("  This is a ceiling finding: automated scores can't do better than humans here.")

    # Per-pair breakdown
    pa = pairwise_agreement(judgements)
    if pa:
        print(f"\nPer-pair agreement (mean): {np.mean(list(pa.values())):.2%}")
        low = [(p, v) for p, v in pa.items() if v < 0.6]
        if low:
            print(f"  Hard pairs (agreement <60%): {[p for p, _ in low]}")

    # Coverage: which pairs have ≥2 ratings
    rated_twice = sum(1 for p in pair_list if np.sum(~np.isnan(matrix[:, pair_list.index(p)])) >= 2)
    print(f"\nPairs with ≥2 ratings: {rated_twice}/{len(pair_list)}")


if __name__ == "__main__":
    main()
