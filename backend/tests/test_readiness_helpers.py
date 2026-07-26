"""
Unit tests for the pure helper functions inside routes/readiness.py.

These call the helpers directly without an HTTP request.  They belong in a
separate file so test_api.py can truthfully contain only TestClient tests.

Heavy optional packages (google-generativeai, groq) are mocked at the
module level so this file is safe to collect without those packages installed.
"""

import sys
from unittest.mock import MagicMock

import pytest

# ── Stub heavy optional packages before any route import ──────────────────
sys.modules.setdefault("google", MagicMock())
sys.modules.setdefault("google.generativeai", MagicMock())
sys.modules.setdefault("groq", MagicMock())

if "pydantic_settings" not in sys.modules:
    _ps_stub = MagicMock()
    _ps_stub.BaseSettings = object
    sys.modules["pydantic_settings"] = _ps_stub

from routes.readiness import (  # noqa: E402
    _validate_pdf,
    _evidence_level_and_tenure,
    _candidate_skills,
    _extract_requirements,
)
from core.exceptions import ResumeParseFailed  # noqa: E402


# ── _validate_pdf ──────────────────────────────────────────────────────────

def test_validate_pdf_accepts_valid_pdf():
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b"%PDF-1.4\nsome content"
    assert _validate_pdf(mock_file) == b"%PDF-1.4\nsome content"


def test_validate_pdf_rejects_non_pdf_extension():
    mock_file = MagicMock()
    mock_file.filename = "resume.txt"
    mock_file.file.read.return_value = b"%PDF-1.4\nsome content"
    with pytest.raises(ResumeParseFailed, match="PDF files are supported"):
        _validate_pdf(mock_file)


def test_validate_pdf_rejects_empty_file():
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b""
    with pytest.raises(ResumeParseFailed, match="empty"):
        _validate_pdf(mock_file)


def test_validate_pdf_rejects_oversized_file():
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b"x" * (10 * 1024 * 1024 + 1)
    with pytest.raises(ResumeParseFailed, match="too large"):
        _validate_pdf(mock_file)


def test_validate_pdf_rejects_bad_magic_bytes():
    mock_file = MagicMock()
    mock_file.filename = "resume.pdf"
    mock_file.file.read.return_value = b"not a pdf file at all"
    with pytest.raises(ResumeParseFailed, match="valid PDF"):
        _validate_pdf(mock_file)


# ── _evidence_level_and_tenure ────────────────────────────────────────────

def test_evidence_level_skills_section_only_returns_1():
    skill = MagicMock()
    skill.normalized = "kubernetes"
    skill.context    = ""
    skill.source     = "phrase_match"
    sections = {"skills": "Python, Kubernetes, Docker"}
    level, _ = _evidence_level_and_tenure(skill, sections)
    assert level == 1


def test_evidence_level_experience_strong_verb_returns_3():
    skill = MagicMock()
    skill.normalized = "kubernetes"
    skill.context    = "Deployed services on Kubernetes across production clusters"
    skill.source     = "phrase_match"
    sections = {"experience": "Deployed services on Kubernetes across production clusters"}
    level, _ = _evidence_level_and_tenure(skill, sections)
    assert level == 3


def test_evidence_level_scope_marker_returns_4():
    skill = MagicMock()
    skill.normalized = "kubernetes"
    skill.context    = "Managed 40-node Kubernetes cluster serving 2 million requests"
    skill.source     = "phrase_match"
    sections = {"experience": "Managed 40-node Kubernetes cluster serving 2 million requests"}
    level, _ = _evidence_level_and_tenure(skill, sections)
    assert level == 4


# ── _candidate_skills ─────────────────────────────────────────────────────

def test_candidate_skills_uses_extractor_list():
    mock_core = MagicMock()
    mock_core.skill_extractor.skill_list = ["Python", "Java", "SQL"]
    skills = _candidate_skills(mock_core)
    assert "python" in skills
    assert "java" in skills
    assert "sql" in skills


def test_candidate_skills_hardcoded_fallback():
    mock_core = MagicMock()
    mock_core.skill_extractor = None
    mock_core.dataset_loader.get_all_tech_skills.side_effect = Exception("no data")
    skills = _candidate_skills(mock_core)
    assert "python" in skills
    assert "javascript" in skills
    assert len(skills) > 10


# ── _extract_requirements ─────────────────────────────────────────────────

def test_extract_requirements_counts_correctly():
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
    counts = _extract_requirements([], ["python", "java"])
    assert counts["python"] == 0
    assert counts["java"] == 0
