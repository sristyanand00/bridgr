"""
Box plot: one box per candidate, 5 points each (one per presentation variant).

The height of each box is the presentation effect on identical underlying experience.

Usage:
    python plot.py --results results.json --output presentation_effect.png

Requires: matplotlib (add to requirements if needed: pip install matplotlib)
"""

from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

VARIANT_ORDER  = ("terse", "verbose", "metric_heavy", "jargon_heavy", "non_native")
VARIANT_COLORS = {
    "terse":        "#4C72B0",
    "verbose":      "#DD8452",
    "metric_heavy": "#55A868",
    "jargon_heavy": "#C44E52",
    "non_native":   "#8172B3",
}


def load_results(path: Path) -> list:
    with open(path) as f:
        return json.load(f)


def build_plot_data(results: list, score_key: str) -> tuple:
    """
    Returns:
        candidates:       sorted candidate ids
        scores_by_cand:   {candidate_id: [score_per_variant_in_VARIANT_ORDER]}
        variant_by_cand:  {candidate_id: [variant_names in same order]}
    """
    by_cand_variant: Dict[str, Dict[str, float]] = defaultdict(dict)
    for r in results:
        by_cand_variant[r["candidate_id"]][r["variant"]] = r[score_key]

    candidates = sorted(by_cand_variant.keys())
    scores = {
        c: [by_cand_variant[c].get(v, None) for v in VARIANT_ORDER]
        for c in candidates
    }
    return candidates, scores


def plot(results: list, score_key: str, output_path: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")   # non-interactive backend for headless runs
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib")
        return

    candidates, scores_by_cand = build_plot_data(results, score_key)
    n = len(candidates)

    fig, ax = plt.subplots(figsize=(max(10, n * 1.5), 6))

    positions = list(range(1, n + 1))
    box_data  = [[s for s in scores_by_cand[c] if s is not None] for c in candidates]

    bp = ax.boxplot(
        box_data,
        positions=positions,
        widths=0.5,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(color="#666666"),
        capprops=dict(color="#666666"),
        flierprops=dict(marker="o", color="#999999", markersize=4),
    )

    # Color boxes uniformly (presentation effect is the box height, not colour)
    for patch in bp["boxes"]:
        patch.set_facecolor("#AEC6CF")
        patch.set_alpha(0.7)

    # Scatter individual points coloured by variant
    for i, cand in enumerate(candidates):
        for v_idx, variant in enumerate(VARIANT_ORDER):
            score = scores_by_cand[cand].get(variant)
            if score is not None:
                ax.scatter(
                    i + 1 + (v_idx - 2) * 0.08,   # slight jitter
                    score,
                    color=VARIANT_COLORS[variant],
                    s=40, zorder=3, alpha=0.9,
                )

    ax.set_xticks(positions)
    ax.set_xticklabels(candidates, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel(score_key.replace("_", " ").title(), fontsize=11)
    ax.set_title(
        "Presentation Effect on Readiness Score\n"
        "(Each box = same candidate, 5 phrasings of identical experience)",
        fontsize=12,
    )
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Legend for variant colours
    legend_patches = [
        mpatches.Patch(color=VARIANT_COLORS[v], label=v.replace("_", " "))
        for v in VARIANT_ORDER
    ]
    ax.legend(handles=legend_patches, loc="upper right", fontsize=8, title="Variant")

    # Annotation: mean range
    ranges = [max(d) - min(d) for d in box_data if len(d) >= 2]
    if ranges:
        import numpy as np
        mean_range = np.mean(ranges)
        ax.annotate(
            f"Mean range: {mean_range:.1f} pts",
            xy=(0.02, 0.97), xycoords="axes fraction",
            fontsize=9, color="#333333",
            verticalalignment="top",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot presentation variance")
    parser.add_argument("--results",   default="results.json")
    parser.add_argument("--output",    default="presentation_effect.png")
    parser.add_argument("--score-key", default="interview_score",
                        choices=["screen_score", "interview_score", "job_score"])
    args = parser.parse_args()

    results = load_results(Path(args.results))
    if not results:
        print("No results found.")
        return

    plot(results, args.score_key, Path(args.output))


if __name__ == "__main__":
    main()
