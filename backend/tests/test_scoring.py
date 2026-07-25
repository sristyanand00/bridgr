"""
Tests for the pure scoring engine.

The scoring engine must be deterministic - same input produces identical output.
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Now we can import directly - __init__.py won't pull in spacy
from core_ml.scoring import score, ScoreInput, UserSkill, Requirement

import pytest


def load_fixture(name: str) -> dict:
    """Load a golden fixture JSON file."""
    fixture_path = Path(__file__).parent / "fixtures" / f"{name}.json"
    with open(fixture_path) as f:
        return json.load(f)


def test_golden_perfect():
    """Test perfect match case."""
    fixture = load_fixture("golden_perfect")
    
    inp = ScoreInput(
        user_skills=[UserSkill(**s) for s in fixture["input"]["user_skills"]],
        requirements=[Requirement(**r) for r in fixture["input"]["requirements"]],
        today=fixture["input"]["today"]
    )
    
    result = score(inp)
    
    assert result.screen_score == fixture["expected"]["screen_score"]
    assert result.interview_score == fixture["expected"]["interview_score"]
    assert result.verdict == fixture["expected"]["verdict"]
    assert not result.has_blocker


def test_golden_mixed():
    """Test mixed levels with recency decay."""
    fixture = load_fixture("golden_mixed")
    
    inp = ScoreInput(
        user_skills=[UserSkill(**s) for s in fixture["input"]["user_skills"]],
        requirements=[Requirement(**r) for r in fixture["input"]["requirements"]],
        today=fixture["input"]["today"]
    )
    
    result = score(inp)
    
    # Allow small floating point tolerance
    assert abs(result.screen_score - fixture["expected"]["screen_score"]) < 0.5
    assert abs(result.interview_score - fixture["expected"]["interview_score"]) < 1.0
    assert result.verdict == fixture["expected"]["verdict"]


def test_golden_blocked():
    """Test hard blocker scenario."""
    fixture = load_fixture("golden_blocked")
    
    inp = ScoreInput(
        user_skills=[UserSkill(**s) for s in fixture["input"]["user_skills"]],
        requirements=[Requirement(**r) for r in fixture["input"]["requirements"]],
        today=fixture["input"]["today"]
    )
    
    result = score(inp)
    
    assert result.screen_score == fixture["expected"]["screen_score"]
    assert result.interview_score == fixture["expected"]["interview_score"]
    assert result.verdict == fixture["expected"]["verdict"]
    assert result.has_blocker


def test_deterministic():
    """Same input produces identical output - critical purity test."""
    inp = ScoreInput(
        user_skills=[
            UserSkill(skill="python", level=3, months_since_used=10),
            UserSkill(skill="sql", level=2, months_since_used=15),
        ],
        requirements=[
            Requirement(skill="python", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
            Requirement(skill="sql", required_level=3, criticality=0.8, frequency=0.9, is_blocker=False),
        ],
        today="2026-07-25"
    )
    
    # Run 10 times
    results = [score(inp) for _ in range(10)]
    
    # All results should be byte-identical
    first = results[0]
    for r in results[1:]:
        assert r.screen_score == first.screen_score
        assert r.interview_score == first.interview_score
        assert r.job_score == first.job_score
        assert r.verdict == first.verdict
        assert r.scoring_version == first.scoring_version


def test_no_requirements():
    """Edge case: empty requirements."""
    inp = ScoreInput(
        user_skills=[UserSkill(skill="python", level=4, months_since_used=0)],
        requirements=[],
        today="2026-07-25"
    )
    
    result = score(inp)
    assert result.screen_score == 0.0
    assert result.interview_score == 0.0


def test_no_user_skills():
    """Edge case: no skills."""
    inp = ScoreInput(
        user_skills=[],
        requirements=[
            Requirement(skill="python", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
        ],
        today="2026-07-25"
    )
    
    result = score(inp)
    assert result.screen_score == 0.0
    assert result.interview_score == 0.0
    assert result.verdict == "early"


def test_recency_multipliers():
    """Test recency decay is applied correctly."""
    inp = ScoreInput(
        user_skills=[
            UserSkill(skill="recent", level=3, months_since_used=10),  # 1.0
            UserSkill(skill="aging", level=3, months_since_used=30),   # 0.9
            UserSkill(skill="old", level=3, months_since_used=50),     # 0.75
            UserSkill(skill="ancient", level=3, months_since_used=70), # 0.6
        ],
        requirements=[
            Requirement(skill="recent", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
            Requirement(skill="aging", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
            Requirement(skill="old", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
            Requirement(skill="ancient", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
        ],
        today="2026-07-25"
    )
    
    result = score(inp)
    
    # Find components
    comps = {c.skill: c for c in result.components}
    
    assert comps["recent"].recency_mult == 1.0
    assert comps["aging"].recency_mult == 0.9
    assert comps["old"].recency_mult == 0.75
    assert comps["ancient"].recency_mult == 0.6


def test_partial_level_coverage():
    """Test that partial levels give partial coverage."""
    inp = ScoreInput(
        user_skills=[
            UserSkill(skill="python", level=2, months_since_used=0),  # 2/3 = 0.67
        ],
        requirements=[
            Requirement(skill="python", required_level=3, criticality=1.0, frequency=1.0, is_blocker=False),
        ],
        today="2026-07-25"
    )
    
    result = score(inp)
    
    # Interview coverage should be 2/3 = 0.67
    comp = result.components[0]
    expected_coverage = 2.0 / 3.0
    assert abs(comp.interview_coverage - expected_coverage) < 0.01
