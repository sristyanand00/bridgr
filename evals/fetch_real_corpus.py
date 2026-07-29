#!/usr/bin/env python3
"""
Download real resume data from public gist and extract tech bullets
for evidence-level labeling.

Source: public gist (happycoder0011) - resume dataset CSV
Output: evals/corpus/real_unlabeled_pairs.json

Usage:
    python evals/fetch_real_corpus.py
"""

from __future__ import annotations
import csv
import io
import json
import re
import urllib.request
from pathlib import Path
from typing import List, Dict, Any

# ── Config ────────────────────────────────────────────────────────────────────
DATA_URL = (
    "https://gist.githubusercontent.com/happycoder0011/"
    "63291742f5b2baffd0c4b781f7084b1e/raw/"
    "3d6248da7324008d738b2fc2ba1166f21756980a/Resumedatatset"
)

OUTPUT_FILE = Path(__file__).parent / "corpus" / "real_unlabeled_pairs.json"

# Only these categories are relevant to our tech scoring system
TECH_CATEGORIES = {
    "Data Science",
    "Python Developer",
    "Java Developer",
    "Web Designing",
    "DevOps Engineer",
    "Database",
    "Hadoop",
    "ETL Developer",
    "DotNet Developer",
    "Blockchain",
    "Testing",
    "Network Security Engineer",
}

# Skills we care about — matches what scoring.py and extractor.py handle
TARGET_SKILLS_MAP = {
    "python":           ["python"],
    "sql":              ["sql", "mysql", "postgresql", "sqlite", "sqlserver"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "docker":           ["docker"],
    "kubernetes":       ["kubernetes", "k8s"],
    "aws":              ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "tensorflow":       ["tensorflow", "tf"],
    "pytorch":          ["pytorch"],
    "spark":            ["spark", "apache spark", "pyspark"],
    "java":             ["java"],
    "javascript":       ["javascript", "js", "jquery"],
    "react":            ["react", "reactjs", "react.js"],
    "docker":           ["docker"],
    "git":              ["git", "github", "gitlab"],
    "tableau":          ["tableau"],
    "kafka":            ["kafka"],
    "flask":            ["flask"],
    "django":           ["django"],
    "fastapi":          ["fastapi"],
    "linux":            ["linux", "unix"],
}


# ── Bullet extraction ─────────────────────────────────────────────────────────

def extract_bullets(resume_text: str) -> List[str]:
    """
    Pull out meaningful bullet-like sentences from raw resume text.
    Looks for:
      - Lines starting with * or -
      - Sentences with strong/weak verbs (action-oriented)
      - Skill detail lines like "Python- Experience - 24 months"
    """
    bullets = []
    lines = resume_text.split("\n")

    for line in lines:
        line = line.strip()
        if len(line) < 20:
            continue

        # Bullet markers
        if line.startswith(("*", "-", "•")):
            clean = line.lstrip("*-• ").strip()
            if len(clean) > 20:
                bullets.append(clean)
            continue

        # Skill + experience lines: "Python- Experience - 24 months"
        if re.search(r"experience\s*[-–]\s*\d+\s*months?", line, re.IGNORECASE):
            bullets.append(line)
            continue

        # Action verb sentences
        if re.search(
            r"\b(developed|built|implemented|designed|led|managed|created|"
            r"deployed|architected|owned|assisted|helped|supported|worked)\b",
            line, re.IGNORECASE
        ):
            if len(line) < 300:  # skip very long blobs
                bullets.append(line)

    return bullets


def find_skills_in_bullet(bullet: str) -> List[str]:
    """Return which target skills appear in this bullet."""
    bullet_lower = bullet.lower()
    found = []
    for skill_name, aliases in TARGET_SKILLS_MAP.items():
        if any(alias in bullet_lower for alias in aliases):
            if skill_name not in found:
                found.append(skill_name)
    return found


def infer_category_jd(category: str) -> str:
    """Map dataset category to a JD type."""
    mapping = {
        "Data Science":           "ml_engineer",
        "Python Developer":       "backend_se",
        "Java Developer":         "backend_se",
        "Web Designing":          "backend_se",
        "DevOps Engineer":        "devops",
        "Database":               "backend_se",
        "ETL Developer":          "backend_se",
        "Hadoop":                 "ml_engineer",
        "Testing":                "backend_se",
        "Blockchain":             "backend_se",
        "Network Security Engineer": "devops",
        "DotNet Developer":       "backend_se",
    }
    return mapping.get(category, "backend_se")


def infer_target_role(category: str) -> str:
    mapping = {
        "Data Science":    "Data Scientist / ML Engineer",
        "Python Developer": "Python Backend Developer",
        "Java Developer":  "Java Backend Developer",
        "DevOps Engineer": "DevOps / Platform Engineer",
        "Database":        "Database Engineer",
        "ETL Developer":   "Data Engineer",
        "Hadoop":          "Big Data Engineer",
        "Web Designing":   "Frontend / Full Stack Developer",
        "Testing":         "QA / SDET",
        "Blockchain":      "Blockchain Developer",
    }
    return mapping.get(category, "Software Engineer")


# ── Main ──────────────────────────────────────────────────────────────────────

def fetch_csv(url: str) -> str:
    print(f"Downloading dataset from gist...")
    with urllib.request.urlopen(url) as resp:
        raw = resp.read()
    # Handle encoding — dataset has some latin-1 characters
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def build_pairs(csv_text: str, max_per_category: int = 15) -> List[Dict[str, Any]]:
    pairs = []
    pair_id = 1
    category_counts: Dict[str, int] = {}

    reader = csv.DictReader(io.StringIO(csv_text))

    for row in reader:
        category = row.get("Category", "").strip()
        resume   = row.get("Resume", "").strip()

        if category not in TECH_CATEGORIES:
            continue
        if category_counts.get(category, 0) >= max_per_category:
            continue

        bullets = extract_bullets(resume)
        if not bullets:
            continue

        # Take up to 3 bullets per resume (avoid domination by one person)
        added = 0
        for bullet in bullets:
            if added >= 3:
                break

            skills = find_skills_in_bullet(bullet)
            if not skills:
                continue

            pairs.append({
                "pair_id":        f"real_p{pair_id:03d}",
                "source":         "kaggle_gist_real_resume",
                "category":       category,
                "target_role":    infer_target_role(category),
                "resume_bullet":  bullet,
                "job_description": infer_category_jd(category),
                "target_skills":  skills,
                "notes":          (
                    "Real resume bullet — apply ANNOTATION_GUIDE.md rules: "
                    "check verb strength, section context, and tenure mentions."
                ),
                "labels": {
                    skill: {"level": None, "reasoning": ""}
                    for skill in skills
                },
                "_annotation_instructions": (
                    "Fill in 'level' (0-4) per ANNOTATION_GUIDE.md. "
                    "Add brief 'reasoning'. Copy to gold_set.json when done."
                ),
            })

            pair_id += 1
            added += 1

        if added > 0:
            category_counts[category] = category_counts.get(category, 0) + 1

    return pairs


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    csv_text = fetch_csv(DATA_URL)

    pairs = build_pairs(csv_text, max_per_category=15)

    if not pairs:
        print("No pairs extracted. Check the URL or category filter.")
        return

    # Category breakdown
    by_cat: Dict[str, int] = {}
    for p in pairs:
        by_cat[p["category"]] = by_cat.get(p["category"], 0) + 1

    output = {
        "metadata": {
            "source":       "Real resume data — public gist (happycoder0011)",
            "url":          DATA_URL,
            "total_pairs":  len(pairs),
            "by_category":  by_cat,
            "note":         (
                "These are REAL resume bullets from real people. "
                "Labels (level field) are null — fill them in using ANNOTATION_GUIDE.md. "
                "Do NOT fabricate labels."
            ),
        },
        "pairs": pairs,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nExtracted {len(pairs)} real resume bullets")
    print(f"Saved to: {OUTPUT_FILE}")
    print()
    print("Category breakdown:")
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"  {cat:<35} {count:>3} pairs")

    print()
    print("Sample bullet:")
    if pairs:
        p = pairs[0]
        print(f"  [{p['category']}] {p['resume_bullet'][:80]}...")
        print(f"  Skills found: {p['target_skills']}")

    print()
    print("Next steps:")
    print("  1. Open evals/corpus/real_unlabeled_pairs.json")
    print("  2. For each pair, read the bullet and fill in level (0-4) + reasoning")
    print("  3. Use ChatGPT with ANNOTATION_GUIDE.md as prompt for speed")
    print("  4. Copy labeled examples to evals/gold_set.json")
    print("  5. Run: python evals/run_all.py")


if __name__ == "__main__":
    main()
