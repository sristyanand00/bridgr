#!/usr/bin/env python3
"""
Merge Claude's labels into gold_set.json.

Claude returned labels in this format:
  {"pair_id": "real_p001", "skill": "tensorflow", "level": 0, "reasoning": "..."}

This script:
1. Reads real_unlabeled_pairs.json to get bullet text for each pair_id
2. Reads Claude's labels
3. Converts to gold_set.json format: {"bullet": "...", "skills": {"python": {"level": 2, "reasoning": "..."}}}
4. Deduplicates (same bullet + skill combination, keep last label)
5. Appends to existing gold_set.json examples
"""

import json
from pathlib import Path
from collections import defaultdict

REAL_CORPUS   = Path(__file__).parent / "corpus" / "real_unlabeled_pairs.json"
GOLD_SET_FILE = Path(__file__).parent / "gold_set.json"

# ── Claude's output pasted here ───────────────────────────────────────────────
CLAUDE_LABELS = [
    {"pair_id": "real_p001", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned in the bullet text"},
    {"pair_id": "real_p002", "skill": "tableau", "level": 3, "reasoning": "strong verb 'Created', real job, tableau named directly"},
    {"pair_id": "real_p003", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned in the bullet text"},
    {"pair_id": "real_p004", "skill": "machine learning", "level": 3, "reasoning": "strong verb 'Developed and deployed', ML explicitly named in real job"},
    {"pair_id": "real_p005", "skill": "sql", "level": 3, "reasoning": "strong verb 'Developed', SQL scripts explicitly built in real job"},
    {"pair_id": "real_p006", "skill": "python", "level": 2, "reasoning": "weak verb 'Worked on'"},
    {"pair_id": "real_p042", "skill": "java", "level": 2, "reasoning": "weak verb 'Worked in Migration', no strong action verb"},
    {"pair_id": "real_p043", "skill": "java", "level": 3, "reasoning": "strong verb 'Developed 3 projects using java', real job title stated"},
    {"pair_id": "real_p043", "skill": "javascript", "level": 0, "reasoning": "javascript not named, only ajax/servlet/jsp mentioned"},
    {"pair_id": "real_p054", "skill": "java", "level": 2, "reasoning": "weak verb 'Worked as', role stated but no strong action"},
    {"pair_id": "real_p055", "skill": "python", "level": 3, "reasoning": "strong verb 'Developed views and templates', python named in real job"},
    {"pair_id": "real_p055", "skill": "django", "level": 3, "reasoning": "strong verb 'Developed', django explicitly used in real job"},
    {"pair_id": "real_p056", "skill": "python", "level": 2, "reasoning": "'this project' signals a personal project despite strong verb, caps at 2"},
    {"pair_id": "real_p056", "skill": "sql", "level": 2, "reasoning": "MySQL/PyMySQL used but in a personal project context"},
    {"pair_id": "real_p056", "skill": "machine learning", "level": 0, "reasoning": "ML never mentioned in the bullet"},
    {"pair_id": "real_p056", "skill": "aws", "level": 0, "reasoning": "AWS never mentioned in the bullet"},
    {"pair_id": "real_p056", "skill": "django", "level": 2, "reasoning": "django used but in a personal project context"},
    {"pair_id": "real_p057", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned; bullet is about CRUD/REST API"},
    {"pair_id": "real_p083", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned; bullet is about team management/support"},
    {"pair_id": "real_p098", "skill": "sql", "level": 2, "reasoning": "weak verb 'Worked on', Postgresql named"},
    {"pair_id": "real_p098", "skill": "linux", "level": 2, "reasoning": "weak verb 'Worked on', Redhat Linux named"},
    {"pair_id": "real_p099", "skill": "sql", "level": 2, "reasoning": "Postgresql named but action ties to LDAP config, weak overall"},
    {"pair_id": "real_p099", "skill": "linux", "level": 3, "reasoning": "strong verb 'Configured' applied directly to Windows-to-Linux setup"},
    {"pair_id": "real_p100", "skill": "sql", "level": 2, "reasoning": "weak verb 'Worked with', SQL migrations mentioned generically"},
    {"pair_id": "real_p101", "skill": "sql", "level": 3, "reasoning": "strong verb 'Performed', concrete SQL server patching/reporting tasks"},
    {"pair_id": "real_p102", "skill": "sql", "level": 3, "reasoning": "strong verb 'Performed', concrete SQL audit/mirroring/replication tasks"},
    {"pair_id": "real_p103", "skill": "aws", "level": 3, "reasoning": "extensive hands-on AWS services list with 'installing configuring and troubleshooting'"},
    {"pair_id": "real_p104", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned; bullet is about generic application upgrades"},
    {"pair_id": "real_p105", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned; bullet is about WebLogic platform support"},
    {"pair_id": "real_p106", "skill": "tensorflow", "level": 0, "reasoning": "tensorflow never mentioned; bullet is about Oracle/Linux databases"},
    {"pair_id": "real_p106", "skill": "linux", "level": 2, "reasoning": "weak verb 'Worked with', Linux platform mentioned"},
    {"pair_id": "real_p107", "skill": "machine learning", "level": 3, "reasoning": "ML named directly with substantive task 'design a predictive business model'"},
    {"pair_id": "real_p128", "skill": "sql", "level": 3, "reasoning": "strong verb 'Developed', MySQL database integration explicit"},
    {"pair_id": "real_p129", "skill": "spark", "level": 3, "reasoning": "strong verb 'Developed', Spark scripts named directly"},
    {"pair_id": "real_p130", "skill": "tableau", "level": 3, "reasoning": "strong verb 'Developed', Tableau reports named directly"},
    {"pair_id": "real_p131", "skill": "machine learning", "level": 0, "reasoning": "ML never mentioned; bullet is about a Hadoop health-check utility"},
    {"pair_id": "real_p132", "skill": "linux", "level": 3, "reasoning": "strong verb 'Developed and automated', Unix shell scripting named"},
    {"pair_id": "real_p133", "skill": "spark", "level": 3, "reasoning": "strong verb 'Implemented', Spark named with concrete algorithms"},
    {"pair_id": "real_p134", "skill": "java", "level": 2, "reasoning": "weak verb 'Worked on', Java named generically"},
    {"pair_id": "real_p135", "skill": "aws", "level": 2, "reasoning": "weak verb 'Worked on', AWS EMR named generically"},
    {"pair_id": "real_p157", "skill": "sql", "level": 3, "reasoning": "strong verb 'Created and deployed', extensive SQL objects/queries in real job"},
    {"pair_id": "real_p165", "skill": "sql", "level": 1, "reasoning": "SQL only listed as a tool used, no clear action verb tied to it"},
    {"pair_id": "real_p165", "skill": "machine learning", "level": 0, "reasoning": "ML never mentioned; bullet is about SQL/CSS/reporting controls"},
    {"pair_id": "real_p166", "skill": "sql", "level": 3, "reasoning": "strong verb 'Created web application ... used sql for database' in real job"},
    {"pair_id": "real_p173", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p174", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p175", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p176", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p177", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p178", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p179", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
    {"pair_id": "real_p180", "skill": "java", "level": 3, "reasoning": "strong verbs 'deployed', 'written API', 'build front end' with Java Spring/bytecode named"},
]


def main():
    # Step 1: Build pair_id → bullet text map
    print("Reading real corpus...")
    with open(REAL_CORPUS, encoding="utf-8") as f:
        corpus = json.load(f)

    bullet_map = {p["pair_id"]: p["resume_bullet"] for p in corpus["pairs"]}
    print(f"  {len(bullet_map)} pairs loaded")

    # Step 2: Group Claude's labels by pair_id, deduplicate same bullet+skill
    # (Claude repeated many pairs — keep unique bullet+skill combinations only)
    grouped = defaultdict(dict)  # {pair_id: {skill: {level, reasoning}}}
    for label in CLAUDE_LABELS:
        pid   = label["pair_id"]
        skill = label["skill"]
        grouped[pid][skill] = {
            "level":     label["level"],
            "reasoning": label["reasoning"],
        }

    # Step 3: Convert to gold_set examples format, dedup by bullet text
    seen_bullets = set()
    new_examples = []

    for pair_id, skills in grouped.items():
        bullet = bullet_map.get(pair_id)
        if not bullet:
            print(f"  WARNING: {pair_id} not found in corpus, skipping")
            continue

        # Clean up encoding artifacts (â¢ = bullet character in latin-1)
        bullet_clean = bullet.replace("â¢", "•").replace("â", "").strip()

        # Deduplicate — same bullet text may appear under multiple pair_ids
        bullet_key = bullet_clean[:100]
        if bullet_key in seen_bullets:
            continue
        seen_bullets.add(bullet_key)

        new_examples.append({
            "bullet": bullet_clean,
            "skills": skills,
        })

    print(f"  {len(new_examples)} unique labeled examples from Claude")

    # Step 4: Load existing gold_set and append
    with open(GOLD_SET_FILE, encoding="utf-8") as f:
        gold = json.load(f)

    existing = len(gold["examples"])
    gold["examples"].extend(new_examples)
    gold["metadata"]["annotator"] = "claude-sonnet-human-reviewed"

    # Step 5: Save
    with open(GOLD_SET_FILE, "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2, ensure_ascii=False)

    total = len(gold["examples"])
    total_skills = sum(len(ex["skills"]) for ex in gold["examples"])

    # Level distribution
    from collections import Counter
    levels = Counter()
    for ex in gold["examples"]:
        for s, d in ex["skills"].items():
            levels[d["level"]] += 1

    print()
    print(f"gold_set.json updated:")
    print(f"  Before : {existing} examples")
    print(f"  Added  : {len(new_examples)} examples")
    print(f"  Total  : {total} examples, {total_skills} skill instances")
    print()
    print("Level distribution:")
    for lvl in sorted(levels):
        print(f"  Level {lvl}: {levels[lvl]:>4} instances")
    print()
    print("Run: python evals/run_all.py")


if __name__ == "__main__":
    main()
