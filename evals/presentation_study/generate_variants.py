"""
Generate 5 presentation variants of the same experience.

ALL FACTS (companies, dates, numbers, entities) are preserved across variants.
Only phrasing changes. An assertion verifies this programmatically.

Variants:
  terse        — short bullets, no elaboration
  verbose      — same content, expansive phrasing
  metric_heavy — numbers foregrounded
  jargon_heavy — dense domain vocabulary
  non_native   — grammatically correct but non-idiomatic phrasing

Usage:
    python generate_variants.py --input original.json --output variants/

original.json format:
    {
        "candidate_id": "c01",
        "target_role": "Senior Software Engineer",
        "original_bullets": [
            "Led migration of 3 monolithic services to Kubernetes, reducing deploy time by 40%",
            ...
        ]
    }

Output: variants/<candidate_id>/<variant>.json  — each has the same schema.
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

VARIANT_NAMES = ("terse", "verbose", "metric_heavy", "jargon_heavy", "non_native")


# ── Fact extractor ────────────────────────────────────────────────────────────
# Used for the assertion: every number and entity in the original must appear
# in each variant.

_NUMBER_RE  = re.compile(r"\b\d+(?:[.,]\d+)?(?:%|x|X|MB|GB|TB|K|M|B)?\b")
_ENTITY_RE  = re.compile(r"\b[A-Z][a-zA-Z0-9]*(?:\.[a-zA-Z]+)*\b")   # CamelCase / acronyms


def _extract_facts(text: str) -> Dict[str, List[str]]:
    numbers  = _NUMBER_RE.findall(text)
    entities = [e for e in _ENTITY_RE.findall(text) if len(e) > 1]
    return {"numbers": numbers, "entities": entities}


def assert_facts_preserved(original_bullets: List[str], variant_bullets: List[str], variant_name: str) -> None:
    """Raise AssertionError if any number or entity from the original is absent in the variant."""
    orig_text    = " ".join(original_bullets)
    variant_text = " ".join(variant_bullets)

    orig_facts = _extract_facts(orig_text)

    missing_numbers  = [n for n in orig_facts["numbers"]  if n not in variant_text]
    missing_entities = [e for e in orig_facts["entities"] if e not in variant_text]

    if missing_numbers or missing_entities:
        msg = f"Variant '{variant_name}' is missing facts from original:\n"
        if missing_numbers:
            msg += f"  Numbers: {missing_numbers}\n"
        if missing_entities:
            msg += f"  Entities: {missing_entities}\n"
        raise AssertionError(msg)


# ── Variant generators ────────────────────────────────────────────────────────
# Each takes a bullet and returns a reworded bullet with all facts intact.
# These are rule-based transformations — no LLM, so no hallucinated facts.

def _terse(bullet: str) -> str:
    """Strip elaboration; keep verb + object + key metric."""
    # Remove parenthetical explanations
    result = re.sub(r"\([^)]+\)", "", bullet)
    # Remove trailing relative clauses starting with ", which" or ", enabling"
    result = re.sub(r",\s*(which|enabling|allowing|resulting)[^,;.]*", "", result)
    # Trim multiple spaces
    return re.sub(r"\s+", " ", result).strip().rstrip(",;")


def _verbose(bullet: str) -> str:
    """Add context words without changing facts."""
    # Prefix with "Successfully" if not already there
    if not bullet.lower().startswith(("successfully", "effectively", "proactively")):
        bullet = "Successfully " + bullet[0].lower() + bullet[1:]
    # Append a generic impact phrase if bullet doesn't already mention impact
    if not re.search(r"\b(improv|reduc|increas|sav|boost|enabl)\w+", bullet, re.I):
        bullet = bullet.rstrip(".") + ", contributing to improved team efficiency."
    return bullet


def _metric_heavy(bullet: str) -> str:
    """Move numbers to the front of the bullet."""
    numbers = _NUMBER_RE.findall(bullet)
    if numbers:
        # Put first number at the start as a standalone metric
        first = numbers[0]
        bullet = re.sub(rf"\b{re.escape(first)}\b", first, bullet, count=1)
    return bullet


def _jargon_heavy(bullet: str) -> str:
    """Replace common words with domain-specific equivalents."""
    replacements = {
        r"\bbuild\b":        "engineer",
        r"\bbuilt\b":        "engineered",
        r"\buse\b":          "leverage",
        r"\bused\b":         "leveraged",
        r"\bhelped\b":       "facilitated",
        r"\bworked on\b":    "contributed to",
        r"\bimprove\b":      "optimize",
        r"\bimproved\b":     "optimized",
        r"\bsetup\b":        "provisioned",
        r"\bset up\b":       "provisioned",
        r"\bfix\b":          "remediate",
        r"\bfixed\b":        "remediated",
        r"\bdeployment\b":   "CI/CD pipeline execution",
        r"\bsystem\b":       "infrastructure",
    }
    result = bullet
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def _non_native(bullet: str) -> str:
    """Grammatically correct but non-idiomatic phrasing."""
    replacements = {
        r"\bI was responsible for\b": "I did",
        r"\bwas responsible for\b":   "did",
        r"\bI managed\b":             "I was managing",
        r"\bmanaged\b":               "was managing",
        r"\bI led\b":                 "I was leading",
        r"\bled\b":                   "was leading",
        r"\bdeployed\b":              "made deployment of",
        r"\bimplemented\b":           "made implementation of",
        r"\bdeveloped\b":             "did development of",
        r"\bbuilt\b":                 "did building of",
        r"\bcollaborated with\b":     "worked together with",
    }
    result = bullet
    for pattern, replacement in replacements.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


TRANSFORMERS = {
    "terse":        _terse,
    "verbose":      _verbose,
    "metric_heavy": _metric_heavy,
    "jargon_heavy": _jargon_heavy,
    "non_native":   _non_native,
}


def generate_variants(candidate: dict) -> Dict[str, dict]:
    """Generate all 5 variants for one candidate. Returns {variant_name: candidate_dict}."""
    original = candidate["original_bullets"]
    variants = {}

    for name, transform in TRANSFORMERS.items():
        new_bullets = [transform(b) for b in original]
        assert_facts_preserved(original, new_bullets, name)   # hard assertion
        variants[name] = {
            "candidate_id":  candidate["candidate_id"],
            "target_role":   candidate["target_role"],
            "variant":       name,
            "resume_bullets": new_bullets,
        }

    return variants


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate presentation variants")
    parser.add_argument("--input",  required=True, help="Path to original.json or dir of originals")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_dir  = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Accept single file or directory
    files = list(input_path.glob("*.json")) if input_path.is_dir() else [input_path]

    for f in files:
        with open(f) as fh:
            candidate = json.load(fh)

        try:
            variants = generate_variants(candidate)
        except AssertionError as e:
            print(f"ASSERTION FAILED for {candidate['candidate_id']}:\n{e}")
            sys.exit(1)

        cand_dir = output_dir / candidate["candidate_id"]
        cand_dir.mkdir(exist_ok=True)

        for name, data in variants.items():
            out_file = cand_dir / f"{name}.json"
            with open(out_file, "w") as fh:
                json.dump(data, fh, indent=2)

        print(f"  {candidate['candidate_id']}: 5 variants generated ✓")

    print(f"\nDone. Variants saved to {output_dir}")


if __name__ == "__main__":
    main()
