import json
from pathlib import Path
from collections import Counter

print("=" * 50)
print("BRIDGR EVAL — FULL STATUS CHECK")
print("=" * 50)

# ── gold_set ──────────────────────────────────────
gold = json.load(open("gold_set.json", encoding="utf-8"))
examples = gold["examples"]
total_skills = sum(len(ex["skills"]) for ex in examples)
levels = Counter()
for ex in examples:
    for s, d in ex["skills"].items():
        levels[d["level"]] += 1

print("\n1. LABELED DATA (gold_set.json)")
print(f"   Labeled examples    : {len(examples)}")
print(f"   Skill instances     : {total_skills}")
print(f"   Level 0 (absent)    : {levels[0]}")
print(f"   Level 1 (claimed)   : {levels[1]}")
print(f"   Level 2 (exposed)   : {levels[2]}")
print(f"   Level 3 (applied)   : {levels[3]}")
print(f"   Level 4 (owned)     : {levels[4]}")
target = 100
remaining = max(0, target - len(examples))
print(f"   Target              : {target} examples")
print(f"   Still needed        : {remaining} more examples")

# ── corpus ────────────────────────────────────────
corpus = json.load(open("corpus/real_unlabeled_pairs.json", encoding="utf-8"))
unique_bullets = set(p["resume_bullet"][:100] for p in corpus["pairs"])
labeled_bullets = set(ex["bullet"][:100] for ex in examples)
unlabeled_unique = unique_bullets - labeled_bullets

print("\n2. UNLABELED CORPUS")
print(f"   real_unlabeled_pairs: 180 pairs ({len(unique_bullets)} unique bullets)")
print(f"   Already labeled     : {len(unique_bullets) - len(unlabeled_unique)}")
print(f"   Still unlabeled     : {len(unlabeled_unique)} unique bullets available")

# ── eval results ─────────────────────────────────
print("\n3. CURRENT EVAL RESULTS")
res = json.load(open("results/evaluation_results.json", encoding="utf-8"))
print(f"   {'Approach':<20} {'F1':>6}  {'Kappa':>6}  {'CI':>8}")
print(f"   {'-'*46}")
for r in res["results"]:
    ci = r["f1_ci"]
    ci_str = f"+-{(ci[1]-ci[0])/2:.3f}"
    print(f"   {r['approach']:<20} {r['f1']:>6.3f}  {r['kappa']:>6.3f}  {ci_str:>8}")

# ── README tables ─────────────────────────────────
readme = Path("../README.md").read_text(encoding="utf-8")
pending_count = readme.count("pending")
print("\n4. README STATUS")
print(f"   'pending' entries remaining: {pending_count}")
if pending_count == 0:
    print("   All tables filled ✅")
else:
    print("   Some tables still say 'pending'")

# ── scripts ──────────────────────────────────────
print("\n5. SCRIPTS")
scripts = [
    ("run_all.py",                          "Run eval against gold_set"),
    ("sweep_threshold.py",                  "Sweep semantic threshold"),
    ("label.py",                            "Interactive labeling tool"),
    ("generate_synthetic_resumes.py",       "Generate synthetic corpus"),
    ("fetch_real_corpus.py",               "Download real resume data"),
    ("merge_claude_labels.py",             "Merge Claude labels"),
    ("ANNOTATION_GUIDE.md",               "Labeling rubric"),
    ("human_study/RATER_INSTRUCTIONS.md", "Rater guide for alpha"),
    ("human_study/rate.py",               "Pairwise rating CLI"),
    ("human_study/agreement.py",          "Krippendorff alpha"),
    ("presentation_study/run_study.py",   "Score presentation variants"),
    ("presentation_study/decompose.py",   "Variance decomposition"),
]
for fname, desc in scripts:
    exists = "✅" if Path(fname).exists() else "❌ MISSING"
    print(f"   {exists}  {fname:<42} {desc}")

# ── what's left ───────────────────────────────────
print("\n6. WHAT'S LEFT (priority order)")
tasks = []
if len(examples) < 100:
    tasks.append(f"Label {100 - len(examples)} more examples → run: python label.py")
if pending_count > 0:
    tasks.append("Update README pending tables with real numbers")
if not Path("human_study/judgements.json").exists():
    tasks.append("Recruit 1-2 raters → run: python human_study/rate.py --rater name")
    tasks.append("Compute alpha → run: python human_study/agreement.py")
if not Path("presentation_study/results.json").exists():
    tasks.append("Run presentation study → python presentation_study/run_study.py --variants variants/ --output results.json")

for i, t in enumerate(tasks, 1):
    print(f"   {i}. {t}")

if not tasks:
    print("   All done! 🎉")
