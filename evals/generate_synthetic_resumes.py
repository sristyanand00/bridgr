#!/usr/bin/env python3
"""
Generate a synthetic resume/JD corpus for evidence-level labeling.

Produces ~50 (resume_bullet, job_description, skill) triples spanning:
  - Clearly qualified candidates (levels 3-4)
  - Clearly underqualified candidates (levels 0-1)
  - Borderline/ambiguous candidates (level 2, hard cases)
  - Adversarial keyword-stuffed resumes (level 1 with zero supporting evidence)

Output: evals/corpus/unlabeled_pairs.json

Schema matches what label.py and run_all.py expect:
{
  "metadata": {...},
  "pairs": [
    {
      "pair_id": "p001",
      "category": "qualified|underqualified|borderline|adversarial",
      "resume_bullet": "...",
      "job_description": "...",
      "target_skills": ["python", "sql", ...],
      "notes": "..."   # human hint about what makes this case interesting/hard
    },
    ...
  ]
}

The gold_set.json schema (used by run_all.py) expects:
{
  "examples": [
    {
      "bullet": "...",
      "skills": {
        "python": {"level": <int>, "reasoning": "..."}
      }
    }
  ]
}

label.py reads from this file and populates gold_set.json after human annotation.
The "level" field in gold_set.json must be filled in by a human — this script
leaves it as null with a note so the annotator knows what to fill.

To use:
  python evals/generate_synthetic_resumes.py
  # Then open evals/corpus/unlabeled_pairs.json and use evals/label.py to label each bullet
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

OUTPUT_DIR  = Path(__file__).parent / "corpus"
OUTPUT_FILE = OUTPUT_DIR / "unlabeled_pairs.json"


# ── Job descriptions (original text, not copied from real postings) ──────────
# Each JD captures the style and structure of real postings without copying them.

JD_BACKEND_SE = """\
Senior Backend Software Engineer

We are looking for a backend engineer with 4+ years of professional experience
building scalable APIs and services.

Requirements:
- Strong Python programming skills (3+ years professional)
- Experience designing and maintaining RESTful APIs
- Proficiency with SQL databases (PostgreSQL preferred)
- Familiarity with Docker and container orchestration
- Understanding of distributed systems and microservices patterns
- Git version control and CI/CD pipelines

Nice to have:
- Kubernetes or similar orchestration
- Redis for caching or queuing
- AWS or GCP cloud infrastructure experience
"""

JD_ML_ENGINEER = """\
Machine Learning Engineer

Seeking an ML engineer to join our platform team. You will own model training
pipelines and deploy models to production at scale.

Requirements:
- Proficiency in Python, with experience in ML frameworks (TensorFlow or PyTorch)
- Hands-on experience with scikit-learn for classical ML
- SQL skills for data extraction and analysis
- Understanding of MLOps practices (model versioning, A/B testing, monitoring)
- Experience with cloud ML services (AWS SageMaker, GCP Vertex AI, or Azure ML)

Nice to have:
- Familiarity with Apache Spark for large-scale data processing
- Experience with experiment tracking tools (MLflow, Weights & Biases)
- Docker and Kubernetes for containerised model serving
"""

JD_DATA_ANALYST = """\
Data Analyst

Join our analytics team to turn data into business insights.

Requirements:
- SQL proficiency — comfortable writing complex queries (CTEs, window functions)
- Python or R for data analysis and visualisation
- Experience with BI tools such as Tableau or Power BI
- Ability to communicate technical findings to non-technical stakeholders
- Attention to detail and strong analytical thinking

Nice to have:
- Experience with dbt or similar data transformation tools
- Basic understanding of statistics and A/B testing
"""

JD_DEVOPS = """\
DevOps / Platform Engineer

We need a platform engineer to maintain and improve our cloud infrastructure.

Requirements:
- Hands-on experience with Docker and Kubernetes
- AWS or GCP infrastructure management (EC2, EKS, Cloud Run, etc.)
- Infrastructure as Code: Terraform or CloudFormation
- CI/CD pipeline design and maintenance (GitHub Actions, GitLab CI, or Jenkins)
- Linux system administration
- Strong scripting skills (Bash or Python)

Nice to have:
- Prometheus / Grafana for observability
- Experience with multi-region deployments
- On-call experience and SLO/SLA management
"""


# ── Resume bullets by category ───────────────────────────────────────────────
# Each entry: (bullet_text, target_skills, category, notes)
# category: "qualified" | "underqualified" | "borderline" | "adversarial"

RESUME_BULLETS: List[Dict[str, Any]] = [

    # ── CLEARLY QUALIFIED (levels 3-4 expected) ──────────────────────────────
    {
        "bullet": "Led backend API development for a payments platform using Python (FastAPI) and PostgreSQL, serving 500K monthly active users over 28 months",
        "target_skills": ["python", "postgresql", "fastapi"],
        "jd": "backend_se",
        "category": "qualified",
        "notes": "Leadership verb + scope marker + long tenure → should be level 4 for python and postgresql",
    },
    {
        "bullet": "Architected and deployed microservices on AWS EKS, reducing deployment time by 60% through automated CI/CD pipelines (GitHub Actions)",
        "target_skills": ["aws", "kubernetes", "ci/cd"],
        "jd": "devops",
        "category": "qualified",
        "notes": "Leadership verb + scope/metric → level 4 for all three skills",
    },
    {
        "bullet": "Built and maintained TensorFlow-based recommendation models in production, serving 2M+ recommendations per day for 18 months",
        "target_skills": ["tensorflow", "python", "machine learning"],
        "jd": "ml_engineer",
        "category": "qualified",
        "notes": "Strong verb + scope marker (2M/day) + adequate tenure → 4 for tensorflow/ML, 3 for python",
    },
    {
        "bullet": "Developed Python ETL pipelines to process 50GB of daily sensor data, writing results to a PostgreSQL data warehouse",
        "target_skills": ["python", "sql", "postgresql"],
        "jd": "backend_se",
        "category": "qualified",
        "notes": "Strong verb + data scale marker → level 3/4 depending on tenure context",
    },
    {
        "bullet": "Owned Kubernetes cluster administration for a 40-node production environment on GCP, including autoscaling, monitoring, and on-call rotation for 2 years",
        "target_skills": ["kubernetes", "gcp", "docker"],
        "jd": "devops",
        "category": "qualified",
        "notes": "Owned verb + scope (40 nodes) + very long tenure → level 4",
    },
    {
        "bullet": "Senior Data Analyst (36 months) — built Tableau dashboards and SQL reports used by 15 product managers to track funnel metrics",
        "target_skills": ["sql", "tableau", "python"],
        "jd": "data_analyst",
        "category": "qualified",
        "notes": "Strong verb + long tenure + scope (15 PMs) → level 4 for SQL/Tableau",
    },
    {
        "bullet": "Implemented scikit-learn classification models for customer churn prediction, achieving 88% accuracy; models deployed to production serving 200K accounts",
        "target_skills": ["python", "scikit-learn", "machine learning"],
        "jd": "ml_engineer",
        "category": "qualified",
        "notes": "Strong verb + quantified impact + scope → level 3/4",
    },
    {
        "bullet": "Designed and implemented Redis-backed job queue handling 10K+ tasks/hour for an image processing service (12 months)",
        "target_skills": ["redis", "python", "docker"],
        "jd": "backend_se",
        "category": "qualified",
        "notes": "Strong verb + scale marker → level 3/4",
    },
    {
        "bullet": "Managed infrastructure-as-code migration to Terraform for AWS services (VPC, RDS, Lambda), enabling reproducible environments across 3 teams",
        "target_skills": ["terraform", "aws", "ci/cd"],
        "jd": "devops",
        "category": "qualified",
        "notes": "Managed (leadership-adjacent) verb + scope (3 teams) → level 4",
    },
    {
        "bullet": "Engineered REST APIs using Python Django REST Framework for an e-commerce platform, maintaining 99.9% uptime over 20 months",
        "target_skills": ["python", "sql", "docker"],
        "jd": "backend_se",
        "category": "qualified",
        "notes": "Strong verb + SLA scope marker + long tenure → level 4",
    },

    # ── CLEARLY UNDERQUALIFIED (levels 0-1 expected) ─────────────────────────
    {
        "bullet": "Skills: Python, SQL, Docker, Kubernetes, TensorFlow, PyTorch, AWS, React",
        "target_skills": ["python", "sql", "docker", "kubernetes", "tensorflow"],
        "jd": "ml_engineer",
        "category": "underqualified",
        "notes": "Pure skills section list — no application context anywhere → level 1 for all",
    },
    {
        "bullet": "Summary: Enthusiastic recent graduate with knowledge of machine learning, data science, Python, and SQL",
        "target_skills": ["python", "sql", "machine learning"],
        "jd": "ml_engineer",
        "category": "underqualified",
        "notes": "Summary-only mention with no application evidence → level 1",
    },
    {
        "bullet": "Technologies: React, Node.js, PostgreSQL, Docker, CI/CD, Agile",
        "target_skills": ["postgresql", "docker", "ci/cd"],
        "jd": "backend_se",
        "category": "underqualified",
        "notes": "Skills section only — no verbs, no context → level 1",
    },
    {
        "bullet": "Proficient in Tableau, Power BI, Excel, SQL, Python for data analysis",
        "target_skills": ["sql", "tableau", "python"],
        "jd": "data_analyst",
        "category": "underqualified",
        "notes": "'Proficient in' is a skills-section claim without evidence → level 1",
    },
    {
        "bullet": "Familiar with Docker, Kubernetes, Terraform, AWS services including EC2 and S3",
        "target_skills": ["docker", "kubernetes", "terraform", "aws"],
        "jd": "devops",
        "category": "underqualified",
        "notes": "'Familiar with' = claimed only → level 1",
    },
    {
        "bullet": "Core Competencies: Microservices architecture, RESTful APIs, Python backend development, SQL databases",
        "target_skills": ["python", "sql"],
        "jd": "backend_se",
        "category": "underqualified",
        "notes": "Competencies section listing → level 1, no application evidence",
    },

    # ── BORDERLINE / AMBIGUOUS (level 2 expected — these are the hard cases) ──
    {
        "bullet": "Assisted senior engineers with Python script maintenance and SQL query optimisation during a 3-month internship",
        "target_skills": ["python", "sql"],
        "jd": "backend_se",
        "category": "borderline",
        "notes": "Weak verb (assisted) + short tenure (3 months) → level 2. Tests verb-strength detection",
    },
    {
        "bullet": "Personal project: built a React + Node.js web app with a PostgreSQL backend for tracking personal expenses",
        "target_skills": ["postgresql", "sql"],
        "jd": "backend_se",
        "category": "borderline",
        "notes": "Project context (not professional) → level 2. Tests section detection",
    },
    {
        "bullet": "Helped implement machine learning features using scikit-learn as part of a university capstone project",
        "target_skills": ["machine learning", "scikit-learn", "python"],
        "jd": "ml_engineer",
        "category": "borderline",
        "notes": "Weak verb + academic context → level 2. University project = level 2 per guide",
    },
    {
        "bullet": "Worked with Docker containers during a 4-month co-op placement; helped set up local development environments",
        "target_skills": ["docker"],
        "jd": "devops",
        "category": "borderline",
        "notes": "Weak verb (worked with, helped) + short tenure → level 2",
    },
    {
        "bullet": "Contributed to SQL reporting for the business intelligence team, writing basic SELECT queries and joins",
        "target_skills": ["sql"],
        "jd": "data_analyst",
        "category": "borderline",
        "notes": "Weak verb (contributed) with some context — likely level 2. Verb strength is the deciding factor",
    },
    {
        "bullet": "Developed Python automation scripts during summer internship (2 months) under supervision of senior team",
        "target_skills": ["python"],
        "jd": "backend_se",
        "category": "borderline",
        "notes": "Strong verb BUT very short tenure (2 months) → level 2. Tests tenure threshold at <6 months",
    },
    {
        "bullet": "Used AWS S3 and EC2 for hosting a side project; deployed a small Flask API on EC2",
        "target_skills": ["aws", "python"],
        "jd": "devops",
        "category": "borderline",
        "notes": "Side project context → level 2. Note: 'used' is weak; tests whether project context overrides verb",
    },
    {
        "bullet": "Supported data migration from MySQL to PostgreSQL by writing test queries and validation scripts (5-month contract)",
        "target_skills": ["sql", "postgresql"],
        "jd": "backend_se",
        "category": "borderline",
        "notes": "Weak verb (supported) + borderline tenure (5 months < 6) → level 2",
    },
    {
        "bullet": "Participated in the ML team's model evaluation sprint, running scikit-learn experiments and logging results to MLflow",
        "target_skills": ["machine learning", "scikit-learn"],
        "jd": "ml_engineer",
        "category": "borderline",
        "notes": "Weak verb (participated) → level 2 even though in professional context",
    },
    {
        "bullet": "Junior Data Analyst (Jan 2025 – Apr 2025) — created Power BI dashboards for sales reporting",
        "target_skills": ["sql", "tableau"],
        "jd": "data_analyst",
        "category": "borderline",
        "notes": "Strong verb but very short tenure (3 months) → level 2. Tests date parsing and tenure logic",
    },
    {
        "bullet": "Implemented Kubernetes deployments for a staging environment as part of an internal hackathon project",
        "target_skills": ["kubernetes", "docker"],
        "jd": "devops",
        "category": "borderline",
        "notes": "Hackathon = project context → level 2 despite strong verb. Is this professional? Hard case.",
    },
    {
        "bullet": "Built a TensorFlow image classifier for a Kaggle competition, achieving top 15% on the leaderboard",
        "target_skills": ["tensorflow", "machine learning", "python"],
        "jd": "ml_engineer",
        "category": "borderline",
        "notes": "Kaggle = personal project context → level 2. Tests whether competition context is treated like projects",
    },
    {
        "bullet": "Wrote SQL queries for ad hoc analysis requests from the marketing team; no formal DBA role",
        "target_skills": ["sql"],
        "jd": "data_analyst",
        "category": "borderline",
        "notes": "Professional context but no tenure stated, task-level involvement. Ambiguous — annotator must judge",
    },

    # ── ADVERSARIAL (keyword-stuffed, no real evidence) ───────────────────────
    # These specifically test whether evidence-levelling catches keyword stuffing.
    # All skills are listed but no verb, no project context, no tenure — pure stuffing.
    {
        "bullet": "Python | Django | FastAPI | Flask | PostgreSQL | Redis | Docker | Kubernetes | AWS | Terraform | CI/CD | Microservices | REST APIs | GraphQL | Celery",
        "target_skills": ["python", "docker", "kubernetes", "postgresql"],
        "jd": "backend_se",
        "category": "adversarial",
        "notes": "Pure keyword list separated by pipes — should be level 1. No section header even — raw stuffing.",
    },
    {
        "bullet": "Technical Stack: Machine Learning, Deep Learning, NLP, Computer Vision, TensorFlow, PyTorch, Keras, scikit-learn, XGBoost, LightGBM, Pandas, NumPy, Matplotlib, Seaborn",
        "target_skills": ["machine learning", "tensorflow", "pytorch", "scikit-learn"],
        "jd": "ml_engineer",
        "category": "adversarial",
        "notes": "ML keyword dump under 'Technical Stack' — level 1, no application context",
    },
    {
        "bullet": "Experienced in: Docker, Kubernetes, AWS ECS/EKS/EC2/RDS/S3/Lambda, GCP, Azure, Terraform, Ansible, Helm, ArgoCD, Prometheus, Grafana, Jenkins, GitLab CI",
        "target_skills": ["docker", "kubernetes", "aws", "terraform"],
        "jd": "devops",
        "category": "adversarial",
        "notes": "Dense DevOps keyword dump — level 1. Tests whether extensive listing inflates score",
    },
    {
        "bullet": "I have knowledge and experience working with SQL, Tableau, Power BI, Python, R, Excel, Jupyter, dbt, Airflow, Spark, Hadoop for data analytics and business intelligence",
        "target_skills": ["sql", "tableau", "python"],
        "jd": "data_analyst",
        "category": "adversarial",
        "notes": "'I have knowledge of' framing with no evidence — level 1. High-keyword-density claimed-only",
    },
    {
        "bullet": "Skilled in Python, JavaScript, TypeScript, Java, Go, Rust, C++, SQL, NoSQL, MongoDB, PostgreSQL, MySQL, Redis, Kafka, RabbitMQ, Elasticsearch",
        "target_skills": ["python", "sql", "postgresql"],
        "jd": "backend_se",
        "category": "adversarial",
        "notes": "Impossible breadth of 'skills' — 15 languages/DBs in one bullet. Clear stuffing → level 1",
    },

    # ── MIXED EVIDENCE in single bullet (tricky multi-signal cases) ───────────
    {
        "bullet": "Skills: Python, Docker — also deployed a Python Flask API on Docker for a client project (6-month freelance engagement)",
        "target_skills": ["python", "docker"],
        "jd": "backend_se",
        "category": "borderline",
        "notes": "Skill listed AND used in project/freelance context. Guide says take highest level — is freelance professional? Hard case for annotator.",
    },
    {
        "bullet": "Led a team of 4 engineers building a Python microservices platform; also listed Python under skills section",
        "target_skills": ["python"],
        "jd": "backend_se",
        "category": "qualified",
        "notes": "Appears in BOTH skills section and experience with leadership verb → experience context wins → level 4",
    },
    {
        "bullet": "Junior Software Engineer (Mar 2024 – Jun 2024) — developed REST API endpoints in Python; also listed Python in skills section",
        "target_skills": ["python"],
        "jd": "backend_se",
        "category": "borderline",
        "notes": "Appears in both sections; experience wins; strong verb BUT short tenure (3 months) → level 2",
    },
    {
        "bullet": "Implemented Spark jobs to process daily batch data (100GB/day) as part of my MSc dissertation research project",
        "target_skills": ["python", "machine learning"],
        "jd": "ml_engineer",
        "category": "borderline",
        "notes": "Strong verb + scale marker, BUT academic context (MSc). Guide says university = level 2. Tests priority of context-type over verb strength.",
    },
    {
        "bullet": "Deployed machine learning models to production using Docker and FastAPI; responsible for maintaining model health for 14 months",
        "target_skills": ["machine learning", "docker", "python"],
        "jd": "ml_engineer",
        "category": "qualified",
        "notes": "Strong verb + adequate tenure (14 months); no scope marker → level 3. Tests boundary between 3 and 4.",
    },
    {
        "bullet": "Worked on SQL query optimisation as part of DBA team rotation; improved query response time by 30% for the reporting database",
        "target_skills": ["sql", "postgresql"],
        "jd": "data_analyst",
        "category": "borderline",
        "notes": "Weak verb (worked on) but has a scope/metric (30%). Does metric redeem the verb? Per guide: verb weakness → level 2 regardless of metric.",
    },
    {
        "bullet": "AWS-certified; used AWS services (S3, Lambda, RDS) for a personal automation project; no professional AWS experience",
        "target_skills": ["aws"],
        "jd": "devops",
        "category": "borderline",
        "notes": "Certification + personal project → level 2. Explicitly states no professional experience. Tests certification vs. project evidence.",
    },
    {
        "bullet": "Assisted in maintaining CI/CD pipelines (GitHub Actions) for a year during an SRE rotation at a large tech company",
        "target_skills": ["ci/cd"],
        "jd": "devops",
        "category": "borderline",
        "notes": "Weak verb (assisted) + 12-month tenure → verb weakness wins → level 2. Tests: does long tenure override weak verb?",
    },
    {
        "bullet": "Built a Tableau dashboard for internal sales reporting (used by 3 sales managers); personal initiative, not part of job description",
        "target_skills": ["tableau", "sql"],
        "jd": "data_analyst",
        "category": "borderline",
        "notes": "Strong verb + scope (3 users) but personal initiative, not assigned work. Counts as professional context if at the company? Hard case.",
    },
    {
        "bullet": "Responsible for Python backend for 30 months; managed 2 junior developers; stack included FastAPI, PostgreSQL, Redis, Docker",
        "target_skills": ["python", "postgresql", "docker"],
        "jd": "backend_se",
        "category": "qualified",
        "notes": "Leadership (managed team) + very long tenure (30 months) → level 4 for all. Stack context confirms professional use.",
    },
]


def build_pair(idx: int, entry: Dict[str, Any]) -> Dict[str, Any]:
    """Build one unlabeled pair record."""
    jd_map = {
        "backend_se":  JD_BACKEND_SE,
        "ml_engineer": JD_ML_ENGINEER,
        "data_analyst": JD_DATA_ANALYST,
        "devops":      JD_DEVOPS,
    }
    return {
        "pair_id":       f"p{idx:03d}",
        "category":      entry["category"],
        "resume_bullet": entry["bullet"],
        "job_description": jd_map.get(entry["jd"], JD_BACKEND_SE),
        "target_role":   {
            "backend_se":   "Backend Software Engineer",
            "ml_engineer":  "Machine Learning Engineer",
            "data_analyst": "Data Analyst",
            "devops":       "DevOps / Platform Engineer",
        }.get(entry["jd"], "Software Engineer"),
        "target_skills": entry["target_skills"],
        "notes":         entry.get("notes", ""),
        "labels": {
            skill: {"level": None, "reasoning": ""}
            for skill in entry["target_skills"]
        },
        "_annotation_instructions": (
            "For each skill in 'target_skills', set 'level' to 0-4 per ANNOTATION_GUIDE.md. "
            "Add brief 'reasoning'. When done, copy this bullet + your labels into gold_set.json."
        ),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pairs = [build_pair(i + 1, entry) for i, entry in enumerate(RESUME_BULLETS)]

    by_category = {}
    for p in pairs:
        c = p["category"]
        by_category[c] = by_category.get(c, 0) + 1

    output = {
        "metadata": {
            "description":    "Synthetic resume corpus for evidence-level labeling",
            "total_pairs":    len(pairs),
            "by_category":    by_category,
            "label_format":   "See ANNOTATION_GUIDE.md. Levels 0-4.",
            "next_step":      (
                "Run: python evals/label.py\n"
                "Or open this file, fill in level/reasoning for each skill under 'labels', "
                "then paste completed examples into evals/gold_set.json."
            ),
        },
        "pairs": pairs,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(pairs)} unlabeled pairs → {OUTPUT_FILE}")
    print()
    print("Breakdown by category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat:<20} {count:>3} pairs")
    print()
    print("Next steps:")
    print("  1. Open evals/ANNOTATION_GUIDE.md and read the level definitions")
    print("  2. For each pair in unlabeled_pairs.json, fill in 'level' (0-4) and 'reasoning'")
    print("  3. Copy completed examples into evals/gold_set.json (examples array)")
    print("  4. Run: python evals/run_all.py")
    print()
    print("  Or use label.py interactively:")
    print("  python evals/label.py")
    print("  Paste the bullet text when prompted, then identify skills and assign levels")


if __name__ == "__main__":
    main()
