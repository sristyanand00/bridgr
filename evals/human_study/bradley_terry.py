"""
Bradley-Terry model: convert pairwise wins to a continuous readiness scale.

The BT model estimates a latent "strength" for each candidate from pairwise
comparisons. This gives a continuous ranking comparable to the model's scores.

Requires: choix  (pip install choix)
  choix implements iterative BT fitting via MM algorithm.

Usage:
    python bradley_terry.py

Reads judgements.json, writes bt_scores.json, prints ranking.
"""

from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

JUDGEMENTS_FILE = Path(__file__).parent / "judgements.json"
PAIRS_FILE      = Path(__file__).parent / "pairs.json"
BT_SCORES_FILE  = Path(__file__).parent / "bt_scores.json"


def _load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def build_win_matrix(
    judgements: list, pairs: list
) -> Tuple[Dict[str, int], np.ndarray]:
    """
    Build win counts for Bradley-Terry fitting.

    Returns:
        candidate_idx: mapping candidate_id → integer index
        comparisons:   list of (winner_idx, loser_idx) tuples (ties split 0.5)
    """
    # Map pair_id → pair
    pair_map = {p["id"]: p for p in pairs}

    # Collect candidate ids
    candidates = set()
    for pair in pairs:
        candidates.add(pair["a"]["candidate_id"])
        candidates.add(pair["b"]["candidate_id"])
    candidates = sorted(candidates)
    cand_idx   = {c: i for i, c in enumerate(candidates)}

    # Build pairwise data for choix: list of (winner, loser)
    # Ties count as 0.5 win each way
    data: List[Tuple[int, int]] = []
    for j in judgements:
        pair = pair_map.get(j["pair_id"])
        if pair is None:
            continue
        a_id = pair["a"]["candidate_id"]
        b_id = pair["b"]["candidate_id"]
        winner = j["winner"]
        if winner == "A":
            data.append((cand_idx[a_id], cand_idx[b_id]))
        elif winner == "B":
            data.append((cand_idx[b_id], cand_idx[a_id]))
        elif winner == "tie":
            # Add both directions with 0.5 weight (approximation)
            data.append((cand_idx[a_id], cand_idx[b_id]))
            data.append((cand_idx[b_id], cand_idx[a_id]))

    return cand_idx, data


def fit_bradley_terry(cand_idx: Dict[str, int], data: list) -> np.ndarray:
    """
    Fit Bradley-Terry model using choix.

    Returns scores array indexed by cand_idx.
    """
    try:
        import choix
    except ImportError:
        raise ImportError(
            "choix is required: pip install choix\n"
            "choix implements the Bradley-Terry model via MM algorithm."
        )

    n_items = len(cand_idx)
    if n_items < 2 or not data:
        return np.zeros(n_items)

    # choix expects list of (winner_idx, loser_idx)
    params = choix.ilsr_pairwise(n_items, data, alpha=0.01)
    return params


def main() -> None:
    if not JUDGEMENTS_FILE.exists():
        print("No judgements.json found. Run rate.py first.")
        return
    if not PAIRS_FILE.exists():
        print("No pairs.json found. Run generate_pairs.py first.")
        return

    judgements = _load_json(JUDGEMENTS_FILE)
    pairs      = _load_json(PAIRS_FILE)

    cand_idx, data = build_win_matrix(judgements, pairs)

    if not data:
        print("No valid comparisons found.")
        return

    try:
        scores = fit_bradley_terry(cand_idx, data)
    except ImportError as e:
        print(e)
        return

    # Build output
    idx_cand   = {v: k for k, v in cand_idx.items()}
    bt_results = [
        {"candidate_id": idx_cand[i], "bt_score": float(scores[i])}
        for i in range(len(scores))
    ]
    bt_results.sort(key=lambda x: x["bt_score"], reverse=True)

    _save_json(BT_SCORES_FILE, bt_results)

    print("\nBradley-Terry ranking (higher = more ready):")
    print(f"{'Rank':<6} {'Candidate':<20} {'BT Score':>10}")
    print("─" * 40)
    for rank, entry in enumerate(bt_results, 1):
        print(f"{rank:<6} {entry['candidate_id']:<20} {entry['bt_score']:>10.4f}")

    print(f"\nScores saved to {BT_SCORES_FILE}")


if __name__ == "__main__":
    main()
