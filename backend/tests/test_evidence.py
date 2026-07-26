"""
Test evidence levelling logic.

Evidence levels should be based on CONTEXT (section, verb strength, duration, scope),
NOT on extraction confidence.

Levels:
  0 = absent
  1 = claimed (appears only in skills/summary section)
  2 = exposed (project bullet OR weak/no verb OR <6 months professional)
  3 = applied (professional + strong verb + 6+ months)
  4 = owned (level 3 + leadership verb OR scope marker OR 24+ months)
"""

import sys
from pathlib import Path

# Add backend dir to path so coverage can track the module normally
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from core_ml.evidence import determine_evidence_level, EvidenceContext  # noqa: E402

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
    """Deployed services on Kubernetes, 23 months — applied (3)."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=23,
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


# ── BUG 1: no-verb default must not reach level 3 ─────────────────────────

def test_no_verb_in_experience_returns_2():
    """Skill in experience with no recognisable verb → capped at exposed (2)."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="none",  # no verb detected
        tenure_months=18,
    )
    assert determine_evidence_level(ctx) == 2


def test_no_verb_never_reaches_3():
    """Even with long tenure, verb_strength='none' must stay at 2."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="none",
        tenure_months=36,
    )
    assert determine_evidence_level(ctx) < 3


# ── BUG 2: leadership verb still reaches level 4 ──────────────────────────

def test_leadership_via_dedicated_block_returns_4():
    """Leadership verb with 6+ months → owned (4). Verifies the path is reachable."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="leadership",
        tenure_months=12,
    )
    assert determine_evidence_level(ctx) == 4


# ── BUG 3: exactly 24 months must be level 4 ──────────────────────────────

def test_exactly_24_months_returns_4():
    """24 months is the spec threshold — must return owned (4), not applied (3)."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=24,
    )
    assert determine_evidence_level(ctx) == 4


# ── BUG 5: skills section + experience uses experience path ───────────────

def test_skills_section_plus_experience_uses_experience_path():
    """Skill in BOTH skills section and experience must follow the experience path."""
    ctx = EvidenceContext(
        skill="kubernetes",
        found=True,
        in_skills_section=True,
        in_experience_section=True,
        verb_strength="strong",
        tenure_months=12,
    )
    # Should NOT return 1 (claimed); experience path gives 3 (applied)
    assert determine_evidence_level(ctx) == 3


# ── Coverage: date parsing, detect_verb_strength, detect_scope_markers ───

from core_ml.evidence import (
    extract_tenure_and_last_used,
    extract_last_used_date,
    detect_verb_strength,
    detect_scope_markers,
    _parse_month_year,
)


def test_parse_month_year_two_digit_year():
    """'Jan 22' should expand to 2022."""
    result = _parse_month_year("Jan 22")
    assert result == (2022, 1)


def test_parse_month_year_year_only():
    """'2020' with no month should default to mid-year (month 6)."""
    result = _parse_month_year("2020")
    assert result == (2020, 6)


def test_parse_month_year_unparseable_returns_none():
    """String with no date info should return None."""
    result = _parse_month_year("foobar no date here")
    assert result is None


def test_extract_tenure_month_range_with_present():
    """'Jan 2021 - Present' should return tenure > 0 and parsed=True."""
    info = extract_tenure_and_last_used("Jan 2021 - Present", "")
    assert info.parsed is True
    assert info.tenure_months > 0
    assert info.last_used is not None


def test_extract_tenure_year_only_range():
    """'2019 - 2022' (year-only) should parse correctly."""
    info = extract_tenure_and_last_used("2019 - 2022", "")
    assert info.parsed is True
    assert info.tenure_months > 0


def test_extract_tenure_year_only_present():
    """'2020 - present' (year-only with present) should parse correctly."""
    info = extract_tenure_and_last_used("2020 - present", "")
    assert info.parsed is True
    assert info.tenure_months > 0


def test_extract_tenure_no_date_returns_default():
    """No date found → default 12 months, parsed=False."""
    info = extract_tenure_and_last_used("no dates here at all", "")
    assert info.parsed is False
    assert info.tenure_months == 12
    assert info.last_used is None


def test_extract_last_used_date_returns_none_when_no_date():
    """extract_last_used_date returns None when no date found."""
    result = extract_last_used_date("no dates", "")
    assert result is None


def test_detect_verb_strength_no_verb_returns_none():
    """Text with no recognisable verbs returns 'none'."""
    result = detect_verb_strength("Python experience in data pipelines")
    assert result == "none"


def test_detect_verb_strength_leadership():
    """Leadership verb detected correctly."""
    assert detect_verb_strength("led the migration to Kubernetes") == "leadership"


def test_detect_verb_strength_weak():
    """Weak verb detected correctly."""
    assert detect_verb_strength("assisted with deployment scripts") == "weak"


def test_detect_verb_strength_strong():
    """Strong verb detected correctly."""
    assert detect_verb_strength("built and deployed the API") == "strong"


def test_detect_scope_markers_true():
    """Pattern matching scope marker returns True."""
    assert detect_scope_markers("serving 2 million users") is True


def test_detect_scope_markers_false():
    """No scope markers returns False."""
    assert detect_scope_markers("wrote some code") is False


def test_determine_evidence_level_experience_no_path_fallback():
    """In experience but verb_strength=None and no matching path → fallback 2."""
    ctx = EvidenceContext(
        skill="python",
        found=True,
        in_experience_section=True,
        verb_strength=None,  # None (not set) differs from "none"
        tenure_months=12,
    )
    # verb_strength=None doesn't match "weak"/"none" check, falls to final fallback
    result = determine_evidence_level(ctx)
    assert result == 2


def test_determine_evidence_level_not_in_any_section_returns_1():
    """Found but not in any recognized section → fallback return 1."""
    ctx = EvidenceContext(
        skill="python",
        found=True,
        in_experience_section=False,
        in_projects_section=False,
        in_skills_section=False,
        in_summary_section=False,
    )
    assert determine_evidence_level(ctx) == 1


def test_extract_tenure_unparseable_start_date_skips():
    """Date range with unparseable start skips to next match (no crash)."""
    # "??? 2020 - Jan 2022" — "???" won't parse as a month
    info = extract_tenure_and_last_used("??? 2020 - Jan 2022 some text Jan 2021 - Mar 2023", "")
    # Should find the second valid range
    assert info.parsed is True


def test_extract_tenure_negative_months_skipped():
    """Date range where end < start (negative months) is skipped."""
    # End before start yields negative months and should be skipped
    # Fall through to the year-only regex or default
    info = extract_tenure_and_last_used("Jan 2023 - Feb 2020", "2021 - 2022")
    # Year-only range gives a valid positive result
    assert info.parsed is True
    assert info.tenure_months > 0
