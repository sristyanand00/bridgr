import os
import re
import tempfile
import logging
from collections import Counter
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Analysis
from services.auth_service import get_user_optional
from pydantic import BaseModel

from core.exceptions import ResumeParseFailed
from core.limiter import limiter
from core_ml.evidence import (
    EvidenceContext,
    TenureInfo,
    determine_evidence_level,
    detect_verb_strength,
    detect_scope_markers,
    extract_tenure_and_last_used,
)
from core_ml.scoring import (
    Requirement,
    ScoreComponent,
    ScoreInput,
    ScoreResult,
    UserSkill,
    score,
)
from core_ml import loader as _core_loader
from core_ml.loader import get_core
from core_ml.skill_taxonomy import (
    BASE_SKILLS,
    SKILL_ALIASES,
    canonical_skill,
    merge_skills,
)

router = APIRouter()


def _get_data_mode() -> str:
    """Return the current data_mode from the loader singleton."""
    try:
        return _core_loader.DATA_MODE
    except Exception:
        return "fallback"

MAX_FILE_SIZE = 10 * 1024 * 1024


class EvidenceItem(BaseModel):
    skill: str
    level: int
    source: str
    evidence: str
    last_used: Optional[str] = None  # ISO 'YYYY-MM'; None if not parsed


class RequirementGap(BaseModel):
    skill: str
    appears_in: int
    required_level: int
    user_level: int
    evidence: str
    points_lost: int


class SprintTask(BaseModel):
    day_range: str
    title: str
    outcome: str
    lifts: List[str]


class ScoreComponentOut(BaseModel):
    """Per-requirement score breakdown — fulfils the 'every point traces to a requirement' promise."""
    skill: str
    weight: float
    user_level: int
    required_level: int
    recency_mult: Optional[float]    # None when skill is absent (not stale — simply not present)
    coverage: float          # interview_coverage
    points_lost: float       # weight - points_earned
    reason: str


class ReadinessResponse(BaseModel):
    target_role: str
    screen_score: int
    interview_score: int
    job_score: int
    verdict: str
    scoring_version: str
    has_blocker: bool
    dates_parsed: bool                  # False if any skill fell back to unknown date
    data_mode: str                      # "full" | "sample" | "fallback"
    components: List[ScoreComponentOut]
    extracted_evidence: List[EvidenceItem]
    requirement_gaps: List[RequirementGap]
    matched_requirements: List[RequirementGap]
    top_roi_gaps: List[str]
    skip_for_now: List[str]
    sprint_tasks: List[SprintTask]
    resume_bullets: List[str]


def _validate_pdf(resume: UploadFile) -> bytes:
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise ResumeParseFailed("Only PDF files are supported. Please upload a .pdf file.")

    contents = resume.file.read()
    if not contents:
        raise ResumeParseFailed("The uploaded file is empty.")
    if len(contents) > MAX_FILE_SIZE:
        raise ResumeParseFailed("File too large. Maximum size is 10MB.")
    if not contents.startswith(b"%PDF"):
        raise ResumeParseFailed("The file does not appear to be a valid PDF.")
    return contents


def _candidate_skills(core: Any) -> List[str]:
    """Vocabulary used to detect requirements in the pasted job descriptions.

    SkillExtractor is built from the same BASE_SKILLS merge (see
    core_ml/skill_taxonomy.py), so requirement detection and resume detection
    share one vocabulary and no requirement is structurally unmatchable.
    """
    if hasattr(core, "skill_extractor") and getattr(core.skill_extractor, "skill_list", None):
        skill_list = core.skill_extractor.skill_list
        logger.info(f"Using skill_extractor.skill_list with {len(skill_list)} skills")
        return merge_skills(skill_list, BASE_SKILLS)

    if hasattr(core, "dataset_loader"):
        try:
            tech_skills = core.dataset_loader.get_all_tech_skills()
            logger.info(f"Using dataset_loader.get_all_tech_skills() with {len(tech_skills)} skills")
            return merge_skills(tech_skills, BASE_SKILLS)
        except Exception as e:
            logger.warning(f"dataset_loader.get_all_tech_skills() failed: {e}")

    logger.warning(f"Falling back to base skill list ({len(BASE_SKILLS)} skills)")
    return _hardcoded_skill_list()


def _hardcoded_skill_list() -> List[str]:
    """Base vocabulary, kept as a function for callers/tests that import it."""
    return list(BASE_SKILLS)


def _term_pattern(term: str) -> str:
    """Word-boundary regex for a skill term, tolerant of space/hyphen/underscore."""
    words = term.split()
    if len(words) == 1:
        return rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
    escaped = [re.escape(w) for w in words]
    return r"(?<![a-z0-9])" + r"[\s\-_]+".join(escaped) + r"(?![a-z0-9])"


def _extract_requirements(job_descriptions: List[str], skills: List[str]) -> Counter:
    """Count how many postings mention each requirement.

    Counting is per POSTING, over CANONICAL skill names.  Both matter:

    * Per posting, not per match — `frequency` downstream is "share of postings
      that ask for this", so a posting repeating a term must not inflate it.
    * Canonical names — several vocabulary entries can describe one skill, and
      a single phrase can therefore trigger several of them.  "Hugging Face
      Transformers" matched `huggingface`, `hugging face transformers` AND
      `transformers`, producing three weighted requirements that a resume could
      satisfy at most one of; the leftovers surfaced as top-ROI gaps for a skill
      the candidate plainly had.  Collapsing through `canonical_skill` before
      counting means one concept costs one requirement's worth of weight.
    """
    counts: Counter = Counter()

    for description in job_descriptions:
        text = f" {description.lower()} "
        # Set, not Counter: one posting contributes at most 1 to each skill.
        present: set = set()
        for skill in skills:
            for term in [skill] + SKILL_ALIASES.get(skill, []):
                if re.search(_term_pattern(term), text, re.IGNORECASE):
                    present.add(canonical_skill(skill))
                    break  # this skill is present; other aliases add nothing
        # sorted(), not the raw set: Counter preserves insertion order, and
        # most_common() breaks ties by it.  Feeding it set-iteration order makes
        # the tie-break depend on PYTHONHASHSEED, so the same resume and the
        # same postings score differently across server restarts.
        counts.update(sorted(present))

    return counts


def _evidence_level_and_tenure(
    skill: Any,
    resume_sections: Dict[str, str] | None = None,
) -> tuple[int, TenureInfo]:
    """
    Derive evidence level and tenure info from context.
    Extraction confidence is intentionally ignored here (rule #4 in project.md).
    Returns (level, TenureInfo) so the route can track whether dates were parsed.
    """
    context_text = str(getattr(skill, "context", ""))
    normalized   = str(getattr(skill, "normalized", "")).lower().strip()
    sections     = resume_sections or {}

    in_skills   = normalized in sections.get("skills", "").lower()
    in_summary  = normalized in sections.get("summary", "").lower()
    in_projects = normalized in sections.get("projects", "").lower()
    in_exp      = normalized in sections.get("experience", "").lower()

    # Date parsing now lives in evidence.py where it belongs
    tenure_info = extract_tenure_and_last_used(context_text, sections.get("experience", ""))

    ctx = EvidenceContext(
        skill=normalized,
        found=True,
        in_skills_section=in_skills,
        in_summary_section=in_summary,
        in_experience_section=in_exp,
        in_projects_section=in_projects,
        verb_strength=detect_verb_strength(context_text),
        tenure_months=tenure_info.tenure_months,
        has_scope_marker=detect_scope_markers(context_text),
        context_text=context_text,
    )
    return determine_evidence_level(ctx), tenure_info


@router.post("/readiness", response_model=ReadinessResponse)
@limiter.limit("10/hour")
# ^ Flat 10/hour per IP as a pragmatic v1 backstop.
# v2 improvement: tiered limiting — anonymous callers should be capped at
# 3/hour while authenticated users get 20/hour. slowapi supports conditional
# key functions but tiered per-identity limiting requires extra plumbing
# (custom key_func + override storage key). Deferred to v2; the flat IP
# ceiling is still meaningful abuse protection for a portfolio deployment.
def generate_readiness_report(
    request: Request,  # required by slowapi for rate-limit key derivation
    resume: UploadFile = File(...),
    target_role: str = Form(...),
    job_descriptions: str = Form(...),
    weekly_hours: int = Form(8),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_optional),
):
    import datetime as _dt

    target_role = target_role.strip()
    if len(target_role) < 3:
        raise ResumeParseFailed("Target role must be a real job title.")

    postings = [item.strip() for item in re.split(r"\n---+\n|\n\n+", job_descriptions) if item.strip()]
    if len(postings) < 1:
        raise ResumeParseFailed("Paste at least one real job description.")

    contents = _validate_pdf(resume)

    from core.logging_config import get_request_id
    _rid = get_request_id()
    logger.info(
        "readiness request received | rid=%s target_role=%r num_postings=%d file_size=%d",
        _rid, target_role, len(postings), len(contents),
    )

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        core = get_core()
        resume_data = core.resume_parser.parse(tmp_path)
        extracted = core.skill_extractor.extract(resume_data)

        # Log resume parse result
        full_text = resume_data.get("full_text", "")
        sections = resume_data.get("sections", {})
        logger.info(
            "resume parsed | rid=%s page_count=%s char_count=%d sections_found=%s",
            _rid,
            resume_data.get("page_count", "unknown"),
            len(full_text),
            list(sections.keys()),
        )

        # Build evidence map; track whether any date was unparsed
        user_levels: Dict[str, EvidenceItem] = {}
        any_date_unparsed = False

        for skill in extracted:
            # Canonicalise to the same form the requirement side counts under,
            # otherwise evidence for "hugging face transformers" never matches a
            # requirement recorded as "huggingface".  Duplicates that collapse
            # onto one canonical name keep the highest level (see below).
            normalized = canonical_skill(str(getattr(skill, "normalized", "")))
            if not normalized:
                continue
            level, tenure_info = _evidence_level_and_tenure(skill, resume_data.get("sections", {}))
            if not tenure_info.parsed:
                any_date_unparsed = True
            existing = user_levels.get(normalized)
            if not existing or level > existing.level:
                user_levels[normalized] = EvidenceItem(
                    skill=normalized,
                    level=level,
                    source=str(getattr(skill, "source", "resume")),
                    evidence=str(getattr(skill, "context", ""))[:220],
                    last_used=tenure_info.last_used,
                )

        skill_counts = _extract_requirements(postings, _candidate_skills(core))

        logger.info(
            "skills extracted | rid=%s count=%d any_date_unparsed=%s",
            _rid, len(user_levels), any_date_unparsed,
        )

        # Zero skills from a resume that clearly has text is never a legitimate
        # result — it means the extraction stack is broken, not that the
        # candidate has no skills.  Every score would come back 0% and look like
        # a real verdict.  Shout about it rather than serving a silent zero.
        if not user_levels and len(full_text.strip()) > 100:
            logger.error(
                "EXTRACTION PRODUCED ZERO SKILLS from %d chars of resume text | rid=%s. "
                "This is a broken pipeline, not a weak resume — check that spacy and "
                "sentence-transformers are really installed (a MagicMock stub iterates "
                "as empty and fails silently). All scores will be 0%%.",
                len(full_text), _rid,
            )
        if not skill_counts:
            try:
                fallback = core.analyze(tmp_path, target_role)
                fallback_dict = fallback.model_dump() if hasattr(fallback, "model_dump") else fallback.dict()
                for skill in fallback_dict.get("missing_required", []) + fallback_dict.get("matched_skills", []):
                    name = skill.get("name") if isinstance(skill, dict) else str(skill)
                    if name:
                        skill_counts[name.lower().strip()] += 1
            except Exception:
                pass

        # Explicit tie-break by skill name. most_common() alone falls back to
        # insertion order for equal counts, which decides which requirements
        # survive the cut — that must not vary between identical requests.
        top_requirements = sorted(
            skill_counts.items(), key=lambda kv: (-kv[1], kv[0])
        )[:18]

        # Build ScoreInput and call the single scoring implementation
        today_str = _dt.date.today().isoformat()
        score_user_skills = [
            UserSkill(
                skill=ev.skill,
                level=ev.level,
                last_used=ev.last_used,
            )
            for ev in user_levels.values()
        ]

        score_requirements: List[Requirement] = []
        for skill, count in top_requirements:
            frequency = count / len(postings)          # 0.0-1.0
            # criticality is not yet derived from any signal; constant 1.0 means
            # weight == frequency until a real signal is available (see ASSUMPTIONS.md)
            criticality = 1.0
            required_level = 3 if count >= max(2, len(postings) // 2) else 2
            score_requirements.append(Requirement(
                skill=skill,
                required_level=required_level,
                criticality=criticality,
                frequency=frequency,
                is_blocker=False,  # no blocker detection yet
            ))

        score_input = ScoreInput(
            user_skills=score_user_skills,
            requirements=score_requirements,
            today=today_str,
        )
        result: ScoreResult = score(score_input)

        logger.info(
            "scoring complete | rid=%s screen_score=%s interview_score=%s job_score=%s verdict=%r",
            _rid,
            round(result.screen_score),
            round(result.interview_score),
            round(result.job_score),
            result.verdict,
        )

        # Map ScoreComponent → ScoreComponentOut
        components_out: List[ScoreComponentOut] = [
            ScoreComponentOut(
                skill=c.skill,
                weight=c.weight,
                user_level=c.user_level,
                required_level=c.required_level,
                recency_mult=c.recency_mult,
                coverage=c.interview_coverage,
                points_lost=round((c.points_possible - c.points_earned) * 10),
                reason=c.reason,
            )
            for c in result.components
        ]

        # Build gap/match lists for the existing UI fields
        level_map = {ev.skill: ev for ev in user_levels.values()}
        matched: List[RequirementGap] = []
        gaps: List[RequirementGap] = []

        for req in score_requirements:
            ev = level_map.get(req.skill)
            user_level = ev.level if ev else 0
            weight = req.criticality * req.frequency
            item = RequirementGap(
                skill=req.skill,
                appears_in=round(req.frequency * len(postings)),
                required_level=req.required_level,
                user_level=user_level,
                evidence=ev.evidence if ev else "No resume evidence found",
                points_lost=round(weight * max(req.required_level - user_level, 0) * 10),
            )
            if user_level >= req.required_level:
                matched.append(item)
            else:
                gaps.append(item)

        gaps = sorted(gaps, key=lambda x: (x.appears_in, x.points_lost), reverse=True)
        matched = sorted(matched, key=lambda x: x.appears_in, reverse=True)
        top_roi = [g.skill for g in gaps[:5]]
        skip = [] if len(postings) < 3 else [skill for skill, _ in skill_counts.most_common()[-5:] if skill not in top_roi]

        sprint_days = 14
        task_count = min(4, max(2, weekly_hours // 3))

        sprint_tasks = [
            SprintTask(
                day_range=f"Days {i * (sprint_days // task_count) + 1}-{(i + 1) * (sprint_days // task_count)}",
                title=f"Build evidence for {skill}",
                outcome=f"Create one concrete artifact that proves {skill} at Level 3 for {target_role}.",
                lifts=[skill],
            )
            for i, skill in enumerate(top_roi[:task_count])
        ]

        # Generate varied resume bullets
        bullet_templates = [
            f"Strengthened {target_role} readiness by demonstrating {{skill}} through a focused project aligned to real job requirements.",
            f"Enhanced {{skill}} capabilities with hands-on project work, directly addressing {target_role} role requirements.", 
            f"Developed concrete {{skill}} expertise through targeted learning and application for {target_role} positions.",
            f"Built verifiable {{skill}} competency via practical implementation, closing key gaps for {target_role} roles."
        ]
        
        resume_bullets = [
            bullet_templates[i % len(bullet_templates)].format(skill=skill)
            for i, skill in enumerate(top_roi[:5])
        ]

        # Create the response
        response = ReadinessResponse(
            target_role=target_role,
            screen_score=round(result.screen_score),
            interview_score=round(result.interview_score),
            job_score=round(result.job_score),
            verdict=result.verdict,
            scoring_version=result.scoring_version,
            has_blocker=result.has_blocker,
            dates_parsed=not any_date_unparsed,
            data_mode=_get_data_mode(),
            components=components_out,
            extracted_evidence=sorted(user_levels.values(), key=lambda x: x.level, reverse=True)[:30],
            requirement_gaps=gaps[:12],
            matched_requirements=matched[:12],
            top_roi_gaps=top_roi,
            skip_for_now=skip,
            sprint_tasks=sprint_tasks,
            resume_bullets=resume_bullets,
        )

        # Save analysis to database if user is authenticated.
        # DB failure must never break the API response — try/except wraps only
        # the db.add/db.commit block, not the response construction above.
        if current_user and current_user.get("uid"):
            try:
                analysis_record = Analysis(
                    user_id=current_user["uid"],
                    target_role=target_role,
                    match_score=round(result.screen_score),
                    # feasibility_score is JSON — store a dict for future extensibility
                    feasibility_score={
                        "job_score": round(result.job_score),
                        "verdict": result.verdict,
                    },
                    # skill_gaps: gaps list serialised as plain dicts (JSON-safe)
                    skill_gaps=[g.model_dump() for g in gaps],
                    # matched_skills: matched list serialised as plain dicts
                    matched_skills=[m.model_dump() for m in matched],
                    # roadmap_inputs: everything the roadmap generator needs
                    roadmap_inputs={
                        "screen_score": round(result.screen_score),
                        "interview_score": round(result.interview_score),
                        "job_score": round(result.job_score),
                        "verdict": result.verdict,
                        "has_blocker": result.has_blocker,
                        "top_roi_gaps": top_roi,
                        "scoring_version": result.scoring_version,
                    },
                )
                db.add(analysis_record)
                db.commit()
                logger.info("analysis persisted | rid=%s user=%s", _rid, current_user["uid"])
            except Exception as e:
                # Log the real error so it's visible — do NOT swallow silently
                logger.error("analysis persist failed | rid=%s error=%s", _rid, e, exc_info=True)
                # Roll back the failed transaction so the session stays usable
                db.rollback()

        return response
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
