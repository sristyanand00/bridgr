import os
import re
import tempfile
import logging
from collections import Counter
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Analysis
from services.auth_service import get_user_optional
from pydantic import BaseModel

from core.exceptions import ResumeParseFailed
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
from ml.model_loader import get_core
from core_ml import loader as _core_loader

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
    if hasattr(core, "skill_extractor") and getattr(core.skill_extractor, "skill_list", None):
        skill_list = core.skill_extractor.skill_list
        logger.info(f"Using skill_extractor.skill_list with {len(skill_list)} skills")
        return sorted({str(skill).lower().strip() for skill in skill_list if skill})

    if hasattr(core, "dataset_loader"):
        try:
            tech_skills = core.dataset_loader.get_all_tech_skills()
            logger.info(f"Using dataset_loader.get_all_tech_skills() with {len(tech_skills)} skills")
            return sorted({str(skill).lower().strip() for skill in tech_skills if skill})
        except Exception as e:
            logger.warning(f"dataset_loader.get_all_tech_skills() failed: {e}")

    logger.warning("Falling back to hardcoded skill list (244 skills)")
    return [
        # Core programming languages
        "python", "java", "javascript", "typescript", "c++", "c#", "r", "scala", "go", "rust", "kotlin", "swift",
        
        # Web frameworks and technologies
        "react", "node.js", "vue.js", "angular", "django", "flask", "fastapi", "express.js", "spring", "asp.net", 
        "html", "css", "jquery", "bootstrap", "tailwind", "sass", "webpack", "babel",
        
        # Databases and storage
        "sql", "postgresql", "mysql", "mongodb", "redis", "cassandra", "elasticsearch", "sqlite", "oracle",
        
        # Cloud platforms and DevOps
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "linux", "bash", "git",
        "github actions", "gitlab ci", "ansible", "chef", "puppet", "vagrant", "nginx", "apache",
        
        # Data science and analytics
        "pandas", "numpy", "matplotlib", "seaborn", "plotly", "jupyter", "r studio", "tableau", "power bi", 
        "excel", "statistics", "data analysis", "data visualization", "sql server", "spark", "hadoop", "hive",
        
        # Machine learning and AI
        "machine learning", "deep learning", "neural networks", "tensorflow", "pytorch", "keras", "scikit-learn",
        "xgboost", "lightgbm", "catboost", "opencv", "nltk", "spacy", "transformers", "bert", "gpt",
        
        # Modern ML/GenAI/MLOps stack
        "huggingface", "hugging face transformers", "sentence transformers", "langchain", "langgraph", "rag", "retrieval augmented generation",
        "prompt engineering", "vector database", "faiss", "pinecone", "chromadb", "weaviate", "chroma",
        "mlflow", "kubeflow", "dvc", "weights and biases", "wandb", "tensorboard", "mlops", "model deployment",
        "named entity recognition", "ner", "semantic search", "text classification", "sentiment analysis",
        "cnn", "rnn", "lstm", "gru", "attention mechanism", "llm", "large language model", "openai api",
        "claude api", "gemini api", "fine tuning", "few shot learning", "zero shot learning",
        
        # API and web services
        "rest api", "graphql", "grpc", "soap", "json", "xml", "microservices", "api gateway", "oauth", "jwt",
        "jwt authentication", "authentication", "authorization", "security", "https", "ssl", "cors",
        
        # Message queues and streaming
        "kafka", "rabbitmq", "redis pub/sub", "aws sqs", "aws sns", "apache pulsar", "nats", "event sourcing",
        "airflow", "luigi", "prefect", "dagster", "cron", "celery", "background jobs",
        
        # Testing and quality
        "testing", "unit testing", "integration testing", "pytest", "jest", "selenium", "cypress", "postman",
        "test automation", "tdd", "bdd", "code review", "linting", "static analysis", "sonarqube",
        
        # Mobile development
        "android", "ios", "react native", "flutter", "kotlin", "swift", "objective-c", "xamarin", "cordova",
        "android studio", "xcode", "firebase", "push notifications", "app store", "play store",
        
        # Business intelligence and visualization
        "business intelligence", "data warehousing", "etl", "elt", "data pipeline", "dbt", "looker", "qlik",
        "pentaho", "talend", "informatica", "ssis", "ssrs", "crystal reports",
        
        # Project management and collaboration
        "agile", "scrum", "kanban", "jira", "confluence", "asana", "trello", "slack", "teams", "zoom",
        "project management", "stakeholder management", "product management", "roadmapping", "user stories",
        
        # Core computer science
        "data structures", "algorithms", "system design", "design patterns", "object oriented programming",
        "functional programming", "concurrent programming", "distributed systems", "scalability", "performance",
        
        # Soft skills
        "communication", "teamwork", "leadership", "problem solving", "analytical thinking", "critical thinking",
        "creativity", "adaptability", "time management", "attention to detail", "documentation", "mentoring",
    ]


def _extract_requirements(job_descriptions: List[str], skills: List[str]) -> Counter:
    counts: Counter = Counter()
    aliases = {
        # Web frameworks
        "react": ["react.js", "reactjs", "react js"],
        "node.js": ["node", "nodejs", "node.js", "node js"],
        "vue.js": ["vue", "vuejs", "vue js"],
        "angular": ["angularjs", "angular.js", "angular js"],
        
        # APIs and services
        "rest api": ["rest", "restful", "api", "rest apis", "restful apis"],
        "graphql": ["graph ql", "graph-ql"],
        
        # DevOps and CI/CD
        "ci/cd": ["ci cd", "cicd", "ci-cd", "continuous integration", "continuous deployment", "continuous delivery"],
        "github actions": ["github action", "gh actions"],
        
        # Databases
        "postgresql": ["postgres", "postgresql", "postgre sql"],
        "mongodb": ["mongo db", "mongo", "mongodb"],
        "mysql": ["my sql"],
        "sql server": ["sqlserver", "mssql", "ms sql"],
        
        # ML and AI
        "machine learning": ["ml", "machine learning", "machine-learning"],
        "deep learning": ["dl", "deep learning", "deep-learning"],
        "artificial intelligence": ["ai", "artificial intelligence", "artificial-intelligence"],
        "huggingface": ["hugging face", "hugging-face", "hf", "transformers library"],
        "hugging face transformers": ["huggingface transformers", "hf transformers", "transformers"],
        "langchain": ["lang chain", "lang-chain"],
        "langgraph": ["lang graph", "lang-graph"],
        "rag": ["retrieval augmented generation", "retrieval-augmented generation"],
        "vector database": ["vector db", "vectordb", "vector databases"],
        "large language model": ["llm", "llms", "large language models"],
        "prompt engineering": ["prompt-engineering", "prompting"],
        "named entity recognition": ["ner", "named-entity recognition", "entity recognition"],
        "natural language processing": ["nlp", "natural-language processing"],
        
        # Cloud platforms
        "aws": ["amazon web services", "amazon aws"],
        "gcp": ["google cloud platform", "google cloud", "gcloud"],
        "azure": ["microsoft azure", "ms azure"],
        
        # Programming languages
        "c++": ["cpp", "c plus plus"],
        "c#": ["csharp", "c sharp"],
        "javascript": ["js", "javascript", "java script"],
        "typescript": ["ts", "typescript", "type script"],
        
        # Data science
        "scikit-learn": ["sklearn", "scikit learn", "sci-kit learn"],
        "tensorflow": ["tensor flow", "tf"],
        "pytorch": ["torch", "py torch"],
        "sentence transformers": ["sentence-transformers", "sentencetransformers"],
        
        # Authentication
        "jwt": ["json web token", "json web tokens"],
        "jwt authentication": ["jwt auth", "json web token authentication", "jwt authentication"],
        "oauth": ["oauth2", "oauth 2.0", "o auth"],
        
        # Testing
        "unit testing": ["unit tests", "unittesting"],
        "integration testing": ["integration tests"],
        "test automation": ["automated testing", "test-automation"],
        
        # Mobile
        "react native": ["reactnative", "react-native"],
        "android studio": ["androidstudio", "android-studio"],
    }

    for description in job_descriptions:
        text = f" {description.lower()} "
        for skill in skills:
            terms = [skill] + aliases.get(skill, [])
            # Use case-insensitive matching with word boundaries
            for term in terms:
                # Create a pattern that handles spaces, hyphens, and case variations
                # Split the term and join with flexible separators
                words = term.split()
                if len(words) == 1:
                    # Single word - simple word boundary match
                    pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
                else:
                    # Multi-word - allow flexible separators between words
                    escaped_words = [re.escape(word) for word in words]
                    pattern = rf"(?<![a-z0-9])" + r"[\s\-_]+".join(escaped_words) + r"(?![a-z0-9])"
                
                if re.search(pattern, text, re.IGNORECASE):
                    counts[skill] += 1
                    break  # Found this skill, no need to check other aliases
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
def generate_readiness_report(
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
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        core = get_core()
        resume_data = core.resume_parser.parse(tmp_path)
        extracted = core.skill_extractor.extract(resume_data)

        # Build evidence map; track whether any date was unparsed
        user_levels: Dict[str, EvidenceItem] = {}
        any_date_unparsed = False

        for skill in extracted:
            normalized = str(getattr(skill, "normalized", "")).lower().strip()
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

        # Save analysis to database if user is authenticated
        if current_user and current_user.get("uid"):
            try:
                analysis_record = Analysis(
                    user_id=current_user["uid"],
                    target_role=target_role,
                    match_score=round(result.screen_score),
                    feasibility_score=round(result.job_score),
                    analysis_data={
                        "screen_score": round(result.screen_score),
                        "interview_score": round(result.interview_score), 
                        "job_score": round(result.job_score),
                        "verdict": result.verdict,
                        "has_blocker": result.has_blocker,
                        "top_roi_gaps": top_roi,
                        "matched_count": len(matched),
                        "gaps_count": len(gaps)
                    }
                )
                db.add(analysis_record)
                db.commit()
                import logging
                logging.getLogger(__name__).info(f"Saved analysis record for user {current_user['uid']}")
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to save analysis: {e}")
                # Don't fail the request if DB save fails
                pass

        return response
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
