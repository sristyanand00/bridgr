"""
Test evidence levelling logic.

Evidence levels should be based on CONTEXT (section, verb strength, duration, scope),
NOT on extraction confidence.

Levels:
  0 = absent
  1 = claimed (appears only in skills/summary section)
  2 = exposed (project bullet OR weak verb OR <6 months professional)
  3 = applied (professional + strong verb + 6+ months)
  4 = owned (level 3 + leadership verb OR scope marker OR 24+ months)
"""

import sys
from pathlib import Path
import importlib.util

# Load evidence module directly without triggering __init__.py
backend_dir = Path(__file__).parent.parent
evidence_path = backend_dir / "core_ml" / "evidence.py"

spec = importlib.util.spec_from_file_location("evidence", evidence_path)
evidence = importlib.util.module_from_spec(spec)

# Inject typing module into evidence module's namespace before loading
from typing import Optional
evidence.Optional = Optional

spec.loader.exec_module(evidence)

# Rebuild model after loading
evidence.EvidenceContext.model_rebuild()

determine_evidence_level = evidence.determine_evidence_level
EvidenceContext = evidence.EvidenceContext

import pytest


def test_absent_returns_0():
    """Skill not found anywhere."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=False,
    )
    assert determine_evidence_level(ctx) == 0


def test_skills_section_only_returns_1():
    """Skill appears only in skills section — claimed."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_skills_section=True,
        in_experience_section=False,
        in_projects_section=False,
    )
    assert determine_evidence_level(ctx) == 1


def test_personal_project_returns_2():
    """Kubernetes in a projects-section bullet — exposed."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_skills_section=False,
        in_experience_section=False,
        in_projects_section=True,
    )
    assert determine_evidence_level(ctx) == 2


def test_weak_verb_returns_2():
    """Assisted with Kubernetes deployments, 2yr fulltime — weak verb caps at 2."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="weak",  # "assisted", "helped", "supported"
        tenure_months=24,
    )
    assert determine_evidence_level(ctx) == 2


def test_short_tenure_returns_2():
    """Strong verb but only 4 months tenure — short tenure caps at 2."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",  # "deployed", "built", "implemented"
        tenure_months=4,
    )
    assert determine_evidence_level(ctx) == 2


def test_professional_applied_returns_3():
    """Deployed services on Kubernetes, 2yr fulltime — applied."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=24,
    )
    assert determine_evidence_level(ctx) == 3


def test_leadership_verb_returns_4():
    """Led migration to Kubernetes, 2yr fulltime — owned via leadership."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="leadership",  # "led", "architected", "owned", "designed", "drove"
        tenure_months=24,
    )
    assert determine_evidence_level(ctx) == 4


def test_scale_marker_returns_4():
    """Managed 40-node Kubernetes cluster serving 2M requests — owned via scale."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=12,
        has_scope_marker=True,  # team size, user counts, data volume, SLA
    )
    assert determine_evidence_level(ctx) == 4


def test_long_tenure_returns_4():
    """Strong verb, 30 months — owned via tenure."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=30,
    )
    assert determine_evidence_level(ctx) == 4


def test_takes_max_across_mentions():
    """Same skill at level 1 and level 3 — returns 3."""
    # Kubernetes appears in skills section (level 1)
    ctx1 = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_skills_section=True,
    )
    level1 = determine_evidence_level(ctx1)
    
    # AND in experience with strong verb (level 3)
    ctx2 = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=12,
    )
    level2 = determine_evidence_level(ctx2)
    
    # Take max
    assert max(level1, level2) == 3
