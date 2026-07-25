"""
Generate the 40 pairwise comparison pairs from a candidate pool.

Pairs are constructed so that:
  - Every candidate appears roughly the same number of times
  - ~25% of pairs are deliberate overlaps (same pair, different order) so
    intra-rater agreement can be computed
  - The resulting pairs.json is deterministic (seeded RNG) so all raters
    see the same pairs

Usage:
    python generate_pairs.py --candidates candidates.json --output pairs.json

candidates.json format:
    [{"candidate_id": "c01", "target_role": "...", "resume_bullets": [...]}, ...]
"""

from __future__ import annotations
import argparse
import itertools
import json
import random
from pathlib import Path
from typing import Any

PAIRS_FILE      = Path(__file__).parent / "pairs.json"
CANDIDATES_FILE = Path(__file__).parent / "candidates.json"
TARGET_PAIRS    = 40
OVERLAP_FRAC    = 0.25   # fraction of pairs that are deliberate duplicates
SEED            = 42     # fixed seed for reproducibility


def _load_json(path: Path) -> Any:
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, data: Any) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def generate_pairs(candidates: list, n_pairs: int = TARGET_PAIRS, seed: int = SEED) -> list:
    rng   = random.Random(seed)
    pool  = list(itertools.combinations(range(len(candidates)), 2))
    rng.shuffle(pool)

    selected = pool[: int(n_pairs * (1 - OVERLAP_FRAC))]

    # Add deliberate overlaps (reversed order) for agreement measurement
    n_overlap = n_pairs - len(selected)
    overlaps  = [pair for pair in selected[:n_overlap]]
    overlap_pairs = [(b, a) for a, b in overlaps]   # swap A/B

    all_pairs = selected + overlap_pairs
    rng.shuffle(all_pairs)

    pairs = []
    for idx, (i, j) in enumerate(all_pairs):
        pairs.append({
            "id": f"p{idx + 1:03d}",
            "a":  candidates[i],
            "b":  candidates[j],
            "is_overlap": (j, i) in [(p[0], p[1]) for p in selected[:n_overlap]],
        })

    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pairwise comparison pairs")
    parser.add_argument("--candidates", default=str(CANDIDATES_FILE))
    parser.add_argument("--output",     default=str(PAIRS_FILE))
    parser.add_argument("--n",          type=int, default=TARGET_PAIRS)
    args = parser.parse_args()

    cands_path = Path(args.candidates)
    if not cands_path.exists():
        print(f"Candidates file not found: {cands_path}")
        print("Create candidates.json with your candidate pool first.")
        return

    candidates = _load_json(cands_path)
    if len(candidates) < 2:
        print("Need at least 2 candidates to generate pairs.")
        return

    pairs = generate_pairs(candidates, n_pairs=args.n)
    _save_json(Path(args.output), pairs)

    overlap_count = sum(1 for p in pairs if p.get("is_overlap"))
    print(f"Generated {len(pairs)} pairs ({overlap_count} overlaps for agreement).")
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
