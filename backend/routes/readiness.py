import os
import re
import tempfile
from collections import Counter
from typing import Any, Dict, List

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from core.exceptions import ResumeParseFailed
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


def _evidence_level(skill: Any) -> int:
    confidence = float(getattr(skill, "confidence", 0.5))
    source = str(getattr(skill, "source", "resume"))
    if source == "phrase_match" and confidence >= 0.9:
        return 3
    if confidence >= 0.75:
        return 2
    return 1


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
            level = _evidence_level(skill)
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
