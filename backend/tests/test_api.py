"""
API endpoint tests using FastAPI TestClient.

Heavy ML/LLM dependencies (google-generativeai, groq) are mocked at the
module level before any route import so tests run without those packages.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# ── Mock heavy optional packages before any route import ──────────────────
# This prevents ModuleNotFoundError for google.generativeai and groq,
# which are not installed in the CI/test environment.
_mock_genai = MagicMock()
_mock_groq_module = MagicMock()
sys.modules.setdefault("google", MagicMock())
sys.modules.setdefault("google.generativeai", _mock_genai)
sys.modules.setdefault("groq", _mock_groq_module)


# ── Imports that depend on the mocks being in place ───────────────────────
from routes.readiness import (  # noqa: E402
    _validate_pdf,
    _evidence_level,
    _verdict,
    _candidate_skills,
    _extract_requirements,
)
from core.exceptions import ResumeParseFailed  # noqa: E402


# ── _validate_pdf ──────────────────────────────────────────────────────────

def test_validate_pdf_accepts_valid_pdf():
    """Happy path — valid PDF magic bytes accepted."""
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b"%PDF-1.4\nsome content"

    result = _validate_pdf(mock_file)
    assert result == b"%PDF-1.4\nsome content"


def test_validate_pdf_rejects_non_pdf_extension():
    """Non-.pdf extension must raise ResumeParseFailed."""
    mock_file = MagicMock()
    mock_file.filename = "resume.txt"
    mock_file.file.read.return_value = b"%PDF-1.4\nsome content"

    with pytest.raises(ResumeParseFailed, match="PDF files are supported"):
        _validate_pdf(mock_file)


def test_validate_pdf_rejects_empty_file():
    """Empty upload must raise ResumeParseFailed."""
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b""

    with pytest.raises(ResumeParseFailed, match="empty"):
        _validate_pdf(mock_file)


def test_validate_pdf_rejects_oversized_file():
    """File over 10 MB must raise ResumeParseFailed."""
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b"x" * (10 * 1024 * 1024 + 1)

    with pytest.raises(ResumeParseFailed, match="too large"):
        _validate_pdf(mock_file)


def test_validate_pdf_rejects_bad_magic_bytes():
    """A .pdf file without %PDF header must raise ResumeParseFailed."""
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b"not a pdf file at all"

    with pytest.raises(ResumeParseFailed, match="valid PDF"):
        _validate_pdf(mock_file)


# ── _evidence_level ────────────────────────────────────────────────────────

def test_evidence_level_skills_section_only_returns_1():
    """Skill in skills section only → claimed (1)."""
    skill = MagicMock()
    skill.normalized = "kubernetes"
    skill.context    = ""
    skill.source     = "phrase_match"
    sections = {"skills": "Python, Kubernetes, Docker"}
    assert _evidence_level(skill, sections) == 1


def test_evidence_level_experience_strong_verb_returns_3():
    """Skill in experience with strong verb and default 12mo tenure → applied (3)."""
    skill = MagicMock()
    skill.normalized = "kubernetes"
    skill.context    = "Deployed services on Kubernetes across production clusters"
    skill.source     = "phrase_match"
    sections = {"experience": "Deployed services on Kubernetes across production clusters"}
    assert _evidence_level(skill, sections) == 3


def test_evidence_level_scope_marker_returns_4():
    """Skill with scope marker in experience → owned (4)."""
    skill = MagicMock()
    skill.normalized = "kubernetes"
    skill.context    = "Managed 40-node Kubernetes cluster serving 2 million requests"
    skill.source     = "phrase_match"
    sections = {"experience": "Managed 40-node Kubernetes cluster serving 2 million requests"}
    assert _evidence_level(skill, sections) == 4


# ── _verdict ──────────────────────────────────────────────────────────────

def test_verdict_high_scores_returns_ready():
    assert "Ready to apply" in _verdict(80, 85, 90)


def test_verdict_medium_scores_returns_selective():
    assert "Apply selectively" in _verdict(60, 65, 70)


def test_verdict_low_scores_returns_sprints():
    assert "Two to three" in _verdict(40, 45, 50)


def test_verdict_very_low_returns_not_realistic():
    assert "Not a realistic" in _verdict(20, 25, 30)


# ── _candidate_skills ─────────────────────────────────────────────────────

def test_candidate_skills_uses_extractor_list():
    """Uses core.skill_extractor.skill_list when available."""
    mock_core = MagicMock()
    mock_core.skill_extractor.skill_list = ["Python", "Java", "SQL"]
    skills = _candidate_skills(mock_core)
    assert "python" in skills
    assert "java" in skills
    assert "sql" in skills


def test_candidate_skills_hardcoded_fallback():
    """Returns hardcoded list when no extractor is available."""
    mock_core = MagicMock()
    mock_core.skill_extractor = None
    mock_core.dataset_loader.get_all_tech_skills.side_effect = Exception("no data")
    skills = _candidate_skills(mock_core)
    assert "python" in skills
    assert "javascript" in skills
    assert len(skills) > 10


# ── _extract_requirements ─────────────────────────────────────────────────

def test_extract_requirements_counts_correctly():
    """Skills are counted once per posting, not per mention."""
    jds = [
        "We need a Python developer with SQL experience",
        "Looking for someone with Python and Docker knowledge",
        "JavaScript developer needed",
    ]
    skills = ["python", "sql", "docker", "javascript", "react"]
    counts = _extract_requirements(jds, skills)

    assert counts["python"] == 2
    assert counts["sql"] == 1
    assert counts["docker"] == 1
    assert counts["javascript"] == 1
    assert counts["react"] == 0


def test_extract_requirements_empty_descriptions():
    """Empty job descriptions list returns all-zero counts."""
    counts = _extract_requirements([], ["python", "java"])
    assert counts["python"] == 0
    assert counts["java"] == 0
