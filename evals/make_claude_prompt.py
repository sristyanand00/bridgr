"""
Generate a ready-to-paste Claude prompt for the 23 remaining unlabeled bullets.
Run: python evals/make_claude_prompt.py
Copy the output and paste into Claude.
"""
import json
from pathlib import Path

CORPUS    = Path("corpus/real_unlabeled_pairs.json")
GOLD_SET  = Path("gold_set.json")

corpus   = json.load(open(CORPUS, encoding="utf-8"))
gold     = json.load(open(GOLD_SET, encoding="utf-8"))

# Already labeled bullet texts
labeled_bullets = set(ex["bullet"][:100] for ex in gold["examples"])

# Find unique unlabeled bullets + their skills
seen = set()
unlabeled = []
for pair in corpus["pairs"]:
    key = pair["resume_bullet"][:100]
    if key in labeled_bullets or key in seen:
        continue
    seen.add(key)
    unlabeled.append({
        "pair_id": pair["pair_id"],
        "bullet":  pair["resume_bullet"].replace("â¢", "").replace("â", "").strip(),
        "skills":  pair["target_skills"],
    })

print("="*60)
print("COPY EVERYTHING BELOW THIS LINE AND PASTE INTO CLAUDE")
print("="*60)
print()
print("""I need to label resume bullets with evidence levels for a skill scoring system.

RULES:
- Level 0 = skill not mentioned at all in the bullet
- Level 1 = skill only listed (e.g. "Skills: Python, SQL") — no usage context
- Level 2 = personal project, OR internship, OR weak verb (assisted/helped/worked on/worked with/supported)
- Level 3 = real professional job + strong verb (built/developed/implemented/deployed/created/configured/performed) + skill named directly
- Level 4 = level 3 PLUS: led a team OR 2+ years tenure OR millions of users OR "architected/owned/designed"

IMPORTANT:
- If the skill word is NOT in the bullet at all → Level 0 (do not infer)
- "Worked on" and "Worked with" = weak verb → Level 2 max
- Personal project or university project → Level 2 max even with strong verb

For each bullet below, give me a JSON array. Format exactly:
[
  {"pair_id": "real_pXXX", "skill": "python", "level": 2, "reasoning": "one line reason"},
  ...
]

BULLETS TO LABEL:
""")

for i, item in enumerate(unlabeled, 1):
    print(f"--- Bullet {i} (pair_id: {item['pair_id']}) ---")
    print(f"Text: {item['bullet']}")
    print(f"Skills to label: {item['skills']}")
    print()

print("""Output ONLY the JSON array, nothing else.""")
print()
print("="*60)
print(f"Total bullets: {len(unlabeled)}")
print("="*60)
