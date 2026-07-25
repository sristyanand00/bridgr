"""
Score all 5 variants for each candidate and save to results.json.

Usage:
    python run_study.py --variants variants/ --output results.json --role "Software Engineer"

The script calls the local scoring API (core_ml.scoring) directly — no HTTP,
so it works without a running server.

results.json format:
    [
        {
            "candidate_id": "c01",
            "variant": "terse",
            "target_role": "Senior Software Engineer",
            "screen_score": 72.0,
            "interview_score": 64.5,
            "job_score": 64.5,
        },
        ...
    ]
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import List

# Allow running from the evals directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from core_ml.scoring import score, ScoreInput, UserSkill, Requirement

VARIANT_NAMES = ("terse", "verbose", "metric_heavy", "jargon_heavy", "non_native")

# Simple keyword-based skill detection for the study
# (avoids requiring the full ML stack for a variance measurement)
COMMON_SKILLS = [
    "python", "java", "javascript", "sql", "docker", "kubernetes", "aws",
    "react", "node.js", "git", "machine learning", "tensorflow", "fastapi",
    "postgresql", "redis", "kafka", "spark", "ci/cd", "linux", "typescript",
]


def _detect_skills_simple(bullets: List[str]) -> List[UserSkill]:
    """
    Keyword-based skill detection for variance study only.
    Not the production extractor — this isolates the scoring variance
    from extraction variance (that's a separate measurement).
    """
    text = " ".join(bullets).lower()
    skills = []
    for skill in COMMON_SKILLS:
        if skill in text:
            # Evidence level based on context clues
            level = 2  # default: exposed
            if any(verb in text for verb in ("led", "architected", "owned", "managed")):
                level = 4
            elif any(verb in text for verb in ("built", "deployed", "implemented", "developed")):
                level = 3
            skills.append(UserSkill(skill=skill, level=level, months_since_used=6))
    return skills


def _build_requirements(target_role: str) -> List[Requirement]:
    """Minimal fixed requirements so variance comes from skills, not requirements."""
    # Fixed requirements ensure score variance is purely from presentation
    return [
        Requirement(skill="python",         required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
        Requirement(skill="sql",            required_level=2, criticality=0.8, frequency=0.9, is_blocker=False),
        Requirement(skill="git",            required_level=2, criticality=0.7, frequency=0.8, is_blocker=False),
        Requirement(skill="docker",         required_level=2, criticality=0.7, frequency=0.7, is_blocker=False),
        Requirement(skill="machine learning",required_level=3, criticality=0.9, frequency=0.8, is_blocker=False),
        Requirement(skill="kubernetes",     required_level=2, criticality=0.6, frequency=0.6, is_blocker=False),
        Requirement(skill="aws",            required_level=2, criticality=0.6, frequency=0.6, is_blocker=False),
        Requirement(skill="ci/cd",          required_level=2, criticality=0.5, frequency=0.5, is_blocker=False),
    ]


def score_variant(variant_data: dict, today: str) -> dict:
    user_skills  = _detect_skills_simple(variant_data["resume_bullets"])
    requirements = _build_requirements(variant_data["target_role"])

    inp    = ScoreInput(user_skills=user_skills, requirements=requirements, today=today)
    result = score(inp)

    return {
        "candidate_id":   variant_data["candidate_id"],
        "variant":        variant_data["variant"],
        "target_role":    variant_data["target_role"],
        "screen_score":   result.screen_score,
        "interview_score": result.interview_score,
        "job_score":      result.job_score,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score all presentation variants")
    parser.add_argument("--variants", required=True, help="Directory of variant JSONs")
    parser.add_argument("--output",   default="results.json", help="Output file")
    args = parser.parse_args()

    variants_dir = Path(args.variants)
    today        = date.today().isoformat()
    results      = []

    candidate_dirs = sorted(variants_dir.iterdir())
    for cand_dir in candidate_dirs:
        if not cand_dir.is_dir():
            continue
        for variant_name in VARIANT_NAMES:
            variant_file = cand_dir / f"{variant_name}.json"
            if not variant_file.exists():
                print(f"  Warning: missing {variant_file}")
                continue
            with open(variant_file) as f:
                variant_data = json.load(f)
            result = score_variant(variant_data, today)
            results.append(result)
            print(f"  {variant_data['candidate_id']} / {variant_name}: "
                  f"interview={result['interview_score']:.1f}")

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{len(results)} scores saved to {args.output}")


if __name__ == "__main__":
    main()
