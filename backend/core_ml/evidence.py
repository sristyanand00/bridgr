"""Context-based evidence level determination.

Evidence level measures how deeply a skill was demonstrated, NOT extraction confidence.

Levels:
  0 = absent      — not found
  1 = claimed     — appears only in skills or summary section
  2 = exposed     — project bullet, OR weak verb, OR under 6 months professional
  3 = applied     — professional + strong action verb + 6+ months
  4 = owned       — level 3 conditions PLUS one of:
                     - leadership verb (led/architected/owned/designed/drove)
                     - scope marker (team size, user counts, data volume, SLA)
                     - 24+ months

Recency is stored SEPARATELY and applied as a discount at scoring time.
"""

from __future__ import annotations
import logging
import re
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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
    verb_strength: Optional[str] = None  # "weak", "strong", "leadership"
    tenure_months: int = 0
    has_scope_marker: bool = False
    context_text: str = ""  # Surrounding text for debugging


def determine_evidence_level(ctx: EvidenceContext) -> int:
    """
    Determine evidence level from context. Pure deterministic rules.
    
    Returns:
        0-4 evidence level
    """
    if not ctx.found:
        return 0  # Absent
    
    # Level 1: Claimed — only in skills or summary section
    if (ctx.in_skills_section or ctx.in_summary_section) and not ctx.in_experience_section and not ctx.in_projects_section:
        return 1
    
    # Level 2: Exposed — project, weak verb, or short tenure
    if ctx.in_projects_section:
        return 2  # Personal/academic project
    if ctx.verb_strength == "weak":
        return 2  # Assisted but didn't own
    if ctx.in_experience_section and ctx.tenure_months < 6:
        return 2  # Too short to demonstrate depth
    
    # Level 3: Applied — professional with strong verb and 6+ months
    if ctx.in_experience_section and ctx.verb_strength == "strong" and ctx.tenure_months >= 6:
        # Check for level 4 conditions
        if ctx.verb_strength == "leadership":
            return 4  # Leadership verb
        if ctx.has_scope_marker:
            return 4  # Demonstrated scale/impact
        if ctx.tenure_months > 24:  # MORE than 24 months, not 24 exactly
            return 4  # Extended tenure shows mastery
        return 3
    
    # Level 4: Owned — leadership, scope, or long tenure
    if ctx.in_experience_section:
        if ctx.verb_strength == "leadership":
            return 4
        if ctx.has_scope_marker and ctx.tenure_months >= 6:
            return 4
        if ctx.tenure_months > 24 and ctx.verb_strength in ("strong", "leadership"):  # MORE than 24
            return 4
    
    # Default: if in experience but conditions not met, treat as exposed
    if ctx.in_experience_section:
        return 2
    
    # Fallback
    return 1


def detect_verb_strength(text: str) -> str:
    """
    Detect verb strength from surrounding text.
    
    Returns:
        "weak", "strong", or "leadership"
    """
    text_lower = text.lower()
    
    # Check in order of precedence
    for verb in LEADERSHIP_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            return "leadership"
    
    for verb in WEAK_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            return "weak"
    
    for verb in STRONG_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            return "strong"
    
    # No verb detected — conservative default
    return "strong"


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


def extract_tenure_months(experience_text: str) -> int:
    """
    Extract professional tenure from experience section.
    Handles date ranges like "Jan 2021 – Mar 2023".
    
    Returns:
        Tenure in months (0 if not parsable)
    """
    # Simplified: look for common patterns
    # Real implementation would parse dates properly
    # For now, return a placeholder
    # TODO: Implement proper date parsing in Phase 5
    return 0
