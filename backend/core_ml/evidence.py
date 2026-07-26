"""Context-based evidence level determination.

Evidence level measures how deeply a skill was demonstrated, NOT extraction confidence.

Levels:
  0 = absent      — not found
  1 = claimed     — appears only in skills or summary section
  2 = exposed     — project bullet, OR weak/no verb, OR under 6 months professional
  3 = applied     — professional + strong action verb + 6+ months
  4 = owned       — level 3 conditions PLUS one of:
                     - leadership verb (led/architected/owned/designed/drove)
                     - scope marker (team size, user counts, data volume, SLA)
                     - 24+ months (exactly 24 qualifies)

Recency is stored SEPARATELY and applied as a discount at scoring time.
"""

from __future__ import annotations
import logging
import re
from datetime import date as _date
from typing import Optional, Tuple
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Date-range parsing — domain logic belongs here, not in the route layer
# ---------------------------------------------------------------------------

# Matches "Jan 2021 – Mar 2023", "Feb 2020 - Present", etc.
_DATE_RANGE_RE = re.compile(
    r"(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'\-\.]*\d{2,4})"
    r"\s*[\-–—to]+\s*"
    r"(present|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'\-\.]*\d{2,4})",
    re.IGNORECASE,
)
# Matches "2019 – 2022" or "2020 - present"
_YEAR_ONLY_RE = re.compile(r"\b(20\d{2})\s*[\-–—]\s*(20\d{2}|present)\b", re.IGNORECASE)

_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_month_year(s: str) -> Optional[Tuple[int, int]]:
    """Return (year, month) from a date string, or None if not parseable."""
    s = s.strip().lower().replace("'", " ")
    for abbr, num in _MONTH_MAP.items():
        if abbr in s:
            m = re.search(r"(\d{4}|\d{2})", s)
            if m:
                yr = int(m.group(1))
                if yr < 100:
                    yr += 2000
                return yr, num
    m = re.search(r"(\d{4})", s)
    if m:
        # Year only — use mid-year as conservative default
        return int(m.group(1)), 6
    return None


class TenureInfo(BaseModel):
    """Result of date-range parsing for a single experience entry."""
    tenure_months: int
    last_used: Optional[str]  # ISO 'YYYY-MM', None if unparseable
    parsed: bool              # False when we fell back to a default


def extract_tenure_and_last_used(context_text: str, experience_section: str) -> TenureInfo:
    """
    Parse date ranges from context or experience block.

    Returns TenureInfo with tenure_months, last_used (ISO 'YYYY-MM'), and
    parsed=True only when a real date range was found.  Callers should surface
    parsed=False to the user rather than silently treating a default as data.
    """
    today_yr = _date.today().year
    today_mo = _date.today().month

    for text in (context_text, experience_section):
        for match in _DATE_RANGE_RE.finditer(text):
            start = _parse_month_year(match.group(1))
            if not start:
                continue
            end_s = match.group(2)
            if "present" in end_s.lower():
                end_yr, end_mo = today_yr, today_mo
            else:
                end = _parse_month_year(end_s)
                if not end:
                    continue
                end_yr, end_mo = end
            months = (end_yr - start[0]) * 12 + (end_mo - start[1])
            if months > 0:
                last_used = f"{end_yr:04d}-{end_mo:02d}"
                return TenureInfo(tenure_months=months, last_used=last_used, parsed=True)

        for match in _YEAR_ONLY_RE.finditer(text):
            start_yr = int(match.group(1))
            end_str = match.group(2)
            if "present" in end_str.lower():
                end_yr, end_mo = today_yr, today_mo
            else:
                end_yr, end_mo = int(end_str), 6  # mid-year default
            months = (end_yr - start_yr) * 12 + (end_mo - 6)
            if months > 0:
                last_used = f"{end_yr:04d}-{end_mo:02d}"
                return TenureInfo(tenure_months=months, last_used=last_used, parsed=True)

    # No date found — default so professional hits aren't wrongly capped at level 2
    return TenureInfo(tenure_months=12, last_used=None, parsed=False)


def extract_last_used_date(context_text: str, experience_section: str) -> Optional[str]:
    """
    Return ISO 'YYYY-MM' of the most recent date range containing
    this skill's context, or None if no date is parseable.
    """
    info = extract_tenure_and_last_used(context_text, experience_section)
    return info.last_used if info.parsed else None


# Weak verbs indicate support/assistance, not ownership
WEAK_VERBS = {
    "assisted", "helped", "supported", "contributed", "participated",
    "involved", "aided", "collaborated", "worked with",
}

# Leadership verbs indicate ownership and strategic involvement
LEADERSHIP_VERBS = {
    "led", "architected", "owned", "designed", "drove", "founded",
    "established", "pioneered", "directed", "managed", "spearheaded",
}

# Strong action verbs indicate hands-on application
STRONG_VERBS = {
    "built", "developed", "implemented", "deployed", "created",
    "engineered", "programmed", "coded", "executed", "delivered",
    "shipped", "launched", "maintained", "optimized", "automated",
}

# Scope markers indicate scale/impact — pattern-based detection
SCOPE_PATTERNS = [
    r"\b\d+[\+]?\s*(users?|customers?|clients?)\b",           # 2M users
    r"\b\d+[\+]?\s*(nodes?|servers?|instances?|clusters?)\b", # 40-node cluster
    r"\b\d+[\+]?\s*(team members?|engineers?|developers?)\b", # 5-person team
    r"\b\d+[\+]?\s*TB\b",                                      # 100TB data
    r"\b\d+[\+]?\s*million\b",                                 # 10 million requests
    r"\b\d{2,3}%\s*(uptime|availability|SLA)\b",               # 99.9% uptime
    r"\b\$\d+[KMB]\b",                                         # $5M revenue
]


class EvidenceContext(BaseModel):
    """Context about where and how a skill appears in a resume."""
    skill: str
    found: bool = False
    in_skills_section: bool = False
    in_summary_section: bool = False
    in_experience_section: bool = False
    in_projects_section: bool = False
    verb_strength: Optional[str] = None  # "none", "weak", "strong", "leadership"
    tenure_months: int = 0
    has_scope_marker: bool = False
    context_text: str = ""  # Surrounding text for debugging


def determine_evidence_level(ctx: EvidenceContext) -> int:
    """
    Determine evidence level from context. Pure deterministic rules.

    Decision table (first matching row wins):
    ┌──────────────────────┬─────────────┬──────────┬──────────────┬───────┐
    │ section              │ verb        │ tenure   │ scope_marker │ level │
    ├──────────────────────┼─────────────┼──────────┼──────────────┼───────┤
    │ not found            │ any         │ any      │ any          │   0   │
    │ skills/summary only  │ any         │ any      │ any          │   1   │
    │ projects             │ any         │ any      │ any          │   2   │
    │ experience           │ weak        │ any      │ any          │   2   │
    │ experience           │ none        │ any      │ any          │   2   │
    │ experience           │ any         │ < 6 mo   │ any          │   2   │
    │ experience           │ leadership  │ >= 6 mo  │ any          │   4   │
    │ experience           │ strong      │ >= 6 mo  │ yes          │   4   │
    │ experience           │ strong      │ >= 24 mo │ any          │   4   │
    │ experience           │ strong      │ 6–23 mo  │ no           │   3   │
    │ experience           │ any         │ any      │ any          │   2   │
    └──────────────────────┴─────────────┴──────────┴──────────────┴───────┘

    Notes:
    - "skills/summary only" means the skill is in those sections AND NOT in
      experience or projects. If it also appears in experience, the experience
      row applies (experience path takes precedence — higher evidence wins).
    - verb_strength="none" means no recognisable verb was found near the skill.
      We saw it in a professional context but cannot confirm what was done, so
      we cap at level 2 (exposed). It must never reach level 3.
    - Exactly 24 months qualifies for level 4 (threshold is >= 24, not > 24).

    Returns:
        0-4 evidence level
    """
    if not ctx.found:
        return 0  # Absent

    # Level 1: Claimed — only in skills or summary, NOT in experience or projects.
    # Precedence: if a skill appears in BOTH skills section and experience, the
    # experience path applies because it carries stronger evidence.
    in_skills = ctx.in_skills_section or ctx.in_summary_section
    if in_skills and not ctx.in_experience_section and not ctx.in_projects_section:
        return 1

    # Level 2: Exposed — project context, no/weak verb, or short professional tenure
    if ctx.in_projects_section:
        return 2  # Personal/academic project — not professional evidence
    if ctx.verb_strength in ("weak", "none"):
        # "weak": assisted/helped/supported — did not own the work
        # "none": skill near job history but no recognisable action verb found;
        #         cannot confirm application, so cap at exposed
        return 2
    if ctx.in_experience_section and ctx.tenure_months < 6:
        return 2  # Too short to demonstrate depth — why 6? Probation/ramp-up period

    # Level 4: Owned — professional context with elevated signal
    if ctx.in_experience_section and ctx.tenure_months >= 6:
        if ctx.verb_strength == "leadership":
            # Led/architected/owned: strategic involvement, not just execution
            return 4
        if ctx.has_scope_marker:
            # Quantified scale proves real-world impact (team, users, data, SLA)
            return 4
        if ctx.tenure_months >= 24:
            # >= 24 months (exactly 24 qualifies): sustained exposure shows mastery
            return 4

    # Level 3: Applied — professional, strong verb, 6–23 months, no scope marker
    if ctx.in_experience_section and ctx.verb_strength == "strong" and ctx.tenure_months >= 6:
        return 3

    # Fallback: in experience but conditions not fully met → exposed
    if ctx.in_experience_section:
        return 2

    return 1


def detect_verb_strength(text: str) -> str:
    """
    Detect verb strength from surrounding text.

    Returns:
        "none", "weak", "strong", or "leadership"
    """
    text_lower = text.lower()

    # Check in order of precedence: leadership > weak > strong
    for verb in LEADERSHIP_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            return "leadership"

    for verb in WEAK_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            return "weak"

    for verb in STRONG_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            return "strong"

    # No verb found — returning "none" rather than assuming "strong".
    # A skill appearing near job history with no recognisable verb is exposed
    # (level 2) at best; promoting it to "strong" was the single biggest
    # source of inflated scores.
    return "none"


def detect_scope_markers(text: str) -> bool:
    """
    Check if text contains scale/impact markers.
    
    Returns:
        True if any scope marker pattern matches
    """
    for pattern in SCOPE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

