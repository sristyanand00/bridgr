import os
import re
import tempfile
from collections import Counter
from typing import Any, Dict, List

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from core.exceptions import ResumeParseFailed
from core_ml.evidence import (
    EvidenceContext,
    determine_evidence_level,
    detect_verb_strength,
    detect_scope_markers,
)
from ml.model_loader import get_core

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024


class EvidenceItem(BaseModel):
    skill: str
    level: int
    source: str
    evidence: str


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


class ReadinessResponse(BaseModel):
    target_role: str
    screen_score: int
    interview_score: int
    job_score: int
    verdict: str
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
    if hasattr(core, "skill_extractor") and getattr(core.skill_extractor, "skill_list", None):
        return sorted({str(skill).lower().strip() for skill in core.skill_extractor.skill_list if skill})

    if hasattr(core, "dataset_loader"):
        try:
            return sorted({str(skill).lower().strip() for skill in core.dataset_loader.get_all_tech_skills() if skill})
        except Exception:
            pass

    return [
        "python", "java", "javascript", "typescript", "react", "node.js", "sql",
        "postgresql", "mongodb", "git", "docker", "kubernetes", "aws", "gcp",
        "azure", "rest api", "fastapi", "django", "flask", "data structures",
        "algorithms", "system design", "machine learning", "pandas", "numpy",
        "scikit-learn", "tensorflow", "pytorch", "airflow", "spark", "kafka",
        "tableau", "power bi", "excel", "statistics", "communication",
        "stakeholder management", "testing", "ci/cd", "linux",
    ]


def _extract_requirements(job_descriptions: List[str], skills: List[str]) -> Counter:
    counts: Counter = Counter()
    aliases = {
        "react": ["react.js", "reactjs"],
        "node.js": ["node", "nodejs", "node.js"],
        "rest api": ["rest", "restful", "api"],
        "ci/cd": ["ci cd", "cicd", "continuous integration"],
        "postgresql": ["postgres", "postgresql"],
        "machine learning": ["ml", "machine learning"],
    }

    for description in job_descriptions:
        text = f" {description.lower()} "
        for skill in skills:
            terms = [skill] + aliases.get(skill, [])
            if any(re.search(rf"(?<![a-z0-9+#]){re.escape(term)}(?![a-z0-9+#])", text) for term in terms):
                counts[skill] += 1
    return counts


def _evidence_level(skill: Any, resume_sections: Dict[str, str] | None = None) -> int:
    """
    Derive evidence level from context — section, verb, tenure, scope.
    Extraction confidence is intentionally ignored here (rule #4 in project.md).
    """
    context_text = str(getattr(skill, "context", ""))
    source       = str(getattr(skill, "source", ""))
    normalized   = str(getattr(skill, "normalized", "")).lower().strip()
    sections     = resume_sections or {}

    in_skills    = normalized in sections.get("skills", "").lower()
    in_summary   = normalized in sections.get("summary", "").lower()
    in_projects  = normalized in sections.get("projects", "").lower()
    in_exp       = normalized in sections.get("experience", "").lower()

    # Tenure: look for the skill's context bullet in the experience block to
    # estimate months. Full date-range parsing lives in parser.py; here we
    # use a rough heuristic — if no date found, default 12 months so a
    # professional hit isn't unfairly capped at level 2.
    tenure = _estimate_tenure_months(context_text, sections.get("experience", ""))

    ctx = EvidenceContext(
        skill=normalized,
        found=True,
        in_skills_section=in_skills,
        in_summary_section=in_summary,
        in_experience_section=in_exp,
        in_projects_section=in_projects,
        verb_strength=detect_verb_strength(context_text),
        tenure_months=tenure,
        has_scope_marker=detect_scope_markers(context_text),
        context_text=context_text,
    )
    return determine_evidence_level(ctx)


# Date-range pattern used to estimate tenure from a bullet's surrounding text
_DATE_RANGE_RE = re.compile(
    r"(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'\-\.]*\d{2,4})"
    r"\s*[\-–—to]+\s*"
    r"(present|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s'\-\.]*\d{2,4})",
    re.IGNORECASE,
)
_YEAR_ONLY_RE = re.compile(r"\b(20\d{2})\s*[\-–—]\s*(20\d{2}|present)\b", re.IGNORECASE)


def _estimate_tenure_months(context_text: str, experience_section: str) -> int:
    """
    Rough tenure estimate from context or experience block.
    Returns months; defaults to 12 if no date range is found — better than
    wrongly capping professional experience at level 2.
    """
    from datetime import date as _date
    import calendar as _cal

    def _parse_month_year(s: str):
        """Return (year, month) or None."""
        s = s.strip().lower().replace("'", " ")
        months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
                  "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
        for abbr, num in months.items():
            if abbr in s:
                m = re.search(r"(\d{4}|\d{2})", s)
                if m:
                    yr = int(m.group(1))
                    if yr < 100:
                        yr += 2000
                    return yr, num
        m = re.search(r"(\d{4})", s)
        if m:
            return int(m.group(1)), 6  # mid-year default
        return None

    for text in (context_text, experience_section):
        for match in _DATE_RANGE_RE.finditer(text):
            start_s, end_s = match.group(1), match.group(2)
            start = _parse_month_year(start_s)
            if not start:
                continue
            if "present" in end_s.lower():
                end_yr, end_mo = _date.today().year, _date.today().month
            else:
                parsed = _parse_month_year(end_s)
                if not parsed:
                    continue
                end_yr, end_mo = parsed
            months = (end_yr - start[0]) * 12 + (end_mo - start[1])
            if months > 0:
                return months

        for match in _YEAR_ONLY_RE.finditer(text):
            start_yr = int(match.group(1))
            end_str  = match.group(2)
            end_yr   = _date.today().year if "present" in end_str.lower() else int(end_str)
            months   = (end_yr - start_yr) * 12
            if months > 0:
                return months

    return 12  # default: assume at least one year of professional use


def _verdict(screen: int, interview: int, job: int) -> str:
    lowest = min(screen, interview, job)
    if lowest >= 75:
        return "Ready to apply now"
    if lowest >= 55:
        return "Apply selectively while closing gaps"
    if lowest >= 35:
        return "Two to three focused sprints away"
    return "Not a realistic near-term target yet"


@router.post("/readiness", response_model=ReadinessResponse)
def generate_readiness_report(
    resume: UploadFile = File(...),
    target_role: str = Form(...),
    job_descriptions: str = Form(...),
    weekly_hours: int = Form(8),
):
    target_role = target_role.strip()
    if len(target_role) < 3:
        raise ResumeParseFailed("Target role must be a real job title.")

    postings = [item.strip() for item in re.split(r"\n---+\n|\n\n+", job_descriptions) if item.strip()]
    if len(postings) < 1:
        raise ResumeParseFailed("Paste at least one real job description.")

    contents = _validate_pdf(resume)
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        core = get_core()
        resume_data = core.resume_parser.parse(tmp_path)
        extracted = core.skill_extractor.extract(resume_data)

        user_levels: Dict[str, EvidenceItem] = {}
        for skill in extracted:
            normalized = str(getattr(skill, "normalized", "")).lower().strip()
            if not normalized:
                continue
            level = _evidence_level(skill, resume_data.get("sections", {}))
            existing = user_levels.get(normalized)
            if not existing or level > existing.level:
                user_levels[normalized] = EvidenceItem(
                    skill=normalized,
                    level=level,
                    source=str(getattr(skill, "source", "resume")),
                    evidence=str(getattr(skill, "context", ""))[:220],
                )

        skill_counts = _extract_requirements(postings, _candidate_skills(core))
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

        top_requirements = skill_counts.most_common(18)
        total_weight = sum(count for _, count in top_requirements) or 1

        matched: List[RequirementGap] = []
        gaps: List[RequirementGap] = []
        screen_points = 0
        interview_points = 0
        job_points = 0

        for skill, count in top_requirements:
            evidence = user_levels.get(skill)
            user_level = evidence.level if evidence else 0
            required_level = 3 if count >= max(2, len(postings) // 2) else 2
            weight = count / total_weight
            screen_points += weight * (100 if user_level > 0 else 0)
            interview_points += weight * min(user_level / required_level, 1) * 100
            job_points += weight * min(user_level / max(required_level + 1, 1), 1) * 100
            item = RequirementGap(
                skill=skill,
                appears_in=count,
                required_level=required_level,
                user_level=user_level,
                evidence=evidence.evidence if evidence else "No resume evidence found",
                points_lost=round(weight * max(required_level - user_level, 0) * 10),
            )
            if user_level >= required_level:
                matched.append(item)
            else:
                gaps.append(item)

        gaps = sorted(gaps, key=lambda item: (item.appears_in, item.points_lost), reverse=True)
        matched = sorted(matched, key=lambda item: item.appears_in, reverse=True)
        top_roi = [gap.skill for gap in gaps[:5]]
        skip = [skill for skill, count in skill_counts.most_common()[-5:] if skill not in top_roi]
        sprint_days = 14
        task_count = min(4, max(2, weekly_hours // 3))

        sprint_tasks = [
            SprintTask(
                day_range=f"Days {index * (sprint_days // task_count) + 1}-{(index + 1) * (sprint_days // task_count)}",
                title=f"Build evidence for {skill}",
                outcome=f"Create one concrete artifact that proves {skill} at Level 3 for {target_role}.",
                lifts=[skill],
            )
            for index, skill in enumerate(top_roi[:task_count])
        ]

        resume_bullets = [
            f"Strengthened {target_role} readiness by demonstrating {skill} through a focused project aligned to real job requirements."
            for skill in top_roi[:5]
        ]

        screen = round(screen_points)
        interview = round(interview_points)
        job = round(job_points)

        return ReadinessResponse(
            target_role=target_role,
            screen_score=screen,
            interview_score=interview,
            job_score=job,
            verdict=_verdict(screen, interview, job),
            extracted_evidence=sorted(user_levels.values(), key=lambda item: item.level, reverse=True)[:30],
            requirement_gaps=gaps[:12],
            matched_requirements=matched[:12],
            top_roi_gaps=top_roi,
            skip_for_now=skip,
            sprint_tasks=sprint_tasks,
            resume_bullets=resume_bullets,
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
