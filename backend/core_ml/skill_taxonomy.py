"""Single source of truth for the skill vocabulary.

Why this module exists
----------------------
Scoring compares two independently-built skill sets:

  * the REQUIREMENT side — skills detected in the pasted job descriptions
  * the RESUME side      — skills detected by SkillExtractor in the PDF

If the resume side's vocabulary is a subset of the requirement side's, every
skill in the difference is *structurally unscoreable*: it can be detected in a
posting, so it becomes a requirement with real weight, but it can never be
matched in a resume, so it always contributes user_level=0.

That is exactly what used to happen.  The requirement side merged this base
list into the O*NET vocabulary while SkillExtractor was built from the O*NET
vocabulary alone — in sample mode, 193 skills against 373, leaving 180 skills
(fastapi, django, redis, microservices, unit testing, …) permanently
unmatchable and silently draining points from every report.

Both sides now build from `BASE_SKILLS` via `merge_skills`, so the two
vocabularies are identical by construction.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

# Curated technology + soft-skill vocabulary, independent of O*NET coverage.
# O*NET's technology lists skew toward named commercial products and miss most
# of the modern web/ML stack, so this fills the gap in every data mode.
BASE_SKILLS: List[str] = [
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


def merge_skills(*sources: Iterable[str]) -> List[str]:
    """Normalise, de-duplicate and sort skills drawn from several vocabularies.

    Always include BASE_SKILLS in the call so the resume and requirement sides
    stay symmetric — see the module docstring for why that matters.
    """
    merged = set()
    for source in sources:
        for skill in source or ():
            if not skill:
                continue
            normalized = str(skill).lower().strip()
            if normalized:
                merged.add(normalized)
    return sorted(merged)


# ── Aliases and synonyms ──────────────────────────────────────────────────────
# Surface forms that should all be recognised as the same skill when scanning a
# job description.  Keyed by the vocabulary entry they resolve to.
SKILL_ALIASES: Dict[str, List[str]] = {
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


# Vocabulary entries that are different NAMES FOR THE SAME SKILL.
#
# These used to be scored as independent requirements, so a single job-posting
# phrase produced several competing gaps.  "Hugging Face Transformers" in a JD
# matched `huggingface` (via its "hugging face" alias), `hugging face
# transformers` (directly) and `transformers` (directly) — three requirements,
# of which a resume saying "Hugging Face Transformers" could satisfy only one.
# The other two showed up as top-ROI gaps telling the candidate to go learn a
# skill their resume already listed.
#
# Both the requirement side and the resume side resolve through
# `canonical_skill`, so one concept produces one requirement and matches one
# piece of evidence.  Direction of each mapping follows SKILL_ALIASES above.
SKILL_SYNONYMS: Dict[str, str] = {
    "hugging face transformers":      "huggingface",
    "transformers":                   "huggingface",
    "retrieval augmented generation": "rag",
    "llm":                            "large language model",
    "ner":                            "named entity recognition",
}


def canonical_skill(skill: str) -> str:
    """Collapse a skill name onto the single form used for scoring.

    Must be applied to BOTH the requirement side and the resume side — applying
    it to only one reintroduces the mismatch it exists to prevent.
    """
    normalized = str(skill).lower().strip()
    return SKILL_SYNONYMS.get(normalized, normalized)
