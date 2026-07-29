import json, sys

# ── 1. JSON validity ──────────────────────────────────────────────────────────
try:
    data = json.load(open("gold_set.json", encoding="utf-8"))
    print("JSON valid: YES")
except json.JSONDecodeError as e:
    print(f"JSON BROKEN at line {e.lineno}, col {e.colno}")
    print(f"Error: {e.msg}")
    sys.exit(1)

examples = data.get("examples", [])
print(f"Total examples: {len(examples)}")

# ── 2. Structure check ────────────────────────────────────────────────────────
problems = []
for i, ex in enumerate(examples):
    if "bullet" not in ex:
        problems.append(f"Example {i}: missing 'bullet' field")
    if "skills" not in ex:
        problems.append(f"Example {i}: missing 'skills' field")
        continue
    for skill, val in ex["skills"].items():
        if not isinstance(val, dict):
            problems.append(f"Example {i} / {skill}: value is not a dict, got {type(val)}")
        elif "level" not in val:
            problems.append(f"Example {i} / {skill}: missing 'level'")
        elif val["level"] is None:
            problems.append(f"Example {i} / {skill}: level is null — not labeled yet")
        elif not isinstance(val["level"], int):
            problems.append(f"Example {i} / {skill}: level is not int, got {type(val['level'])}")

if problems:
    print()
    print(f"PROBLEMS FOUND ({len(problems)} total, showing first 20):")
    for p in problems[:20]:
        print(" ", p)
else:
    print("Structure: ALL OK")

# ── 3. Stats ──────────────────────────────────────────────────────────────────
total_skills = sum(len(ex.get("skills", {})) for ex in examples)
print(f"Total skill instances: {total_skills}")

from collections import Counter
levels = Counter()
for ex in examples:
    for skill, val in ex.get("skills", {}).items():
        if isinstance(val.get("level"), int):
            levels[val["level"]] += 1
print(f"Level distribution: {dict(sorted(levels.items()))}")

# ── 4. Quick run_all test ─────────────────────────────────────────────────────
print()
print("Running run_all.py against gold_set...")
import subprocess, sys
result = subprocess.run(
    [sys.executable, "run_all.py"],
    capture_output=True, text=True, timeout=60
)
if result.returncode == 0:
    # Print just the results table
    lines = result.stdout.splitlines()
    for line in lines:
        if any(x in line for x in ["Evaluating", "RESULTS", "---", "Approach", "regex", "bm25", "embedding", "full_", "Results saved", "NO LABELED"]):
            print(line)
else:
    print("run_all.py FAILED:")
    print(result.stdout[-500:])
    print(result.stderr[-500:])
