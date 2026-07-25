"""
Human pairwise rating CLI.

Shows two (resume, role) pairs side by side, asks the rater which candidate
is more ready, and saves the judgement to judgements.json.

Pairwise comparison is used instead of 0-100 ratings because people compare
far more reliably than they rate on an absolute scale.

Usage:
    python rate.py --rater alice --pairs pairs.json
    python rate.py --rater alice --pairs pairs.json --resume  # resume session

pairs.json format:
    [{"id": "p001", "a": {...candidate...}, "b": {...candidate...}}, ...]

Each candidate:
    {"resume_bullets": [...], "target_role": "...", "candidate_id": "..."}
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import textwrap
from datetime import date
from pathlib import Path
from typing import Any

JUDGEMENTS_FILE = Path(__file__).parent / "judgements.json"
PAIRS_FILE      = Path(__file__).parent / "pairs.json"


def _load_json(path: Path) -> Any:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _save_json(path: Path, data: Any) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _already_rated(judgements: list, rater: str, pair_id: str) -> bool:
    return any(j["rater"] == rater and j["pair_id"] == pair_id for j in judgements)


def _display_candidate(label: str, candidate: dict, width: int = 55) -> list[str]:
    """Return display lines for one candidate."""
    lines = [f"  ── Candidate {label} ──────────────────────────"]
    lines.append(f"  Role: {candidate.get('target_role', 'N/A')}")
    lines.append("")
    for bullet in candidate.get("resume_bullets", [])[:8]:
        wrapped = textwrap.wrap(bullet, width=width - 4)
        lines.append(f"    • {wrapped[0]}")
        for continuation in wrapped[1:]:
            lines.append(f"      {continuation}")
    return lines


def _show_pair(pair: dict) -> None:
    """Print both candidates side by side."""
    left  = _display_candidate("A", pair["a"])
    right = _display_candidate("B", pair["b"])

    max_lines = max(len(left), len(right))
    left  += [""] * (max_lines - len(left))
    right += [""] * (max_lines - len(right))

    col_w = 58
    print()
    print(f"  Pair {pair['id']}")
    print("  " + "─" * (col_w * 2 + 4))
    for l, r in zip(left, right):
        print(f"  {l:<{col_w}}  {r}")
    print("  " + "─" * (col_w * 2 + 4))


def _prompt_choice() -> str:
    """Return 'A', 'B', 'tie', or 'skip'."""
    while True:
        raw = input("\n  Which candidate is MORE ready? [A / B / tie / skip]: ").strip().upper()
        if raw in ("A", "B", "TIE", "SKIP"):
            return raw.lower() if raw in ("TIE", "SKIP") else raw
        print("  Please enter A, B, tie, or skip.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pairwise readiness rating CLI")
    parser.add_argument("--rater",  required=True, help="Your name/identifier")
    parser.add_argument("--pairs",  default=str(PAIRS_FILE), help="Path to pairs JSON")
    parser.add_argument("--resume", action="store_true", help="Skip already-rated pairs")
    args = parser.parse_args()

    pairs_path  = Path(args.pairs)
    if not pairs_path.exists():
        print(f"Pairs file not found: {pairs_path}")
        print("Generate it with: python generate_pairs.py")
        sys.exit(1)

    pairs       = _load_json(pairs_path)
    judgements  = _load_json(JUDGEMENTS_FILE)

    to_rate = [
        p for p in pairs
        if not (args.resume and _already_rated(judgements, args.rater, p["id"]))
    ]

    print(f"\n  Bridgr — Human Readiness Study")
    print(f"  Rater: {args.rater}   Pairs remaining: {len(to_rate)}/{len(pairs)}")
    print("  Instructions: Choose which candidate is more ready for their target role.")
    print("  'tie' = genuinely equal.  'skip' = too hard to judge, skip this pair.")
    print()

    rated = 0
    for pair in to_rate:
        _show_pair(pair)
        choice = _prompt_choice()

        if choice != "skip":
            judgements.append({
                "rater":    args.rater,
                "pair_id":  pair["id"],
                "winner":   choice,       # "A", "B", or "tie"
                "date":     date.today().isoformat(),
            })
            _save_json(JUDGEMENTS_FILE, judgements)
            rated += 1
            print(f"  ✓ Saved  ({rated} rated this session)")
        else:
            print("  Skipped.")

        print()
        cont = input("  Continue? [Enter / q to quit]: ").strip().lower()
        if cont == "q":
            break

    print(f"\n  Session complete. {rated} pairs rated.")
    print(f"  Judgements saved to {JUDGEMENTS_FILE}")


if __name__ == "__main__":
    main()
