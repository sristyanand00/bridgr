#!/usr/bin/env python3
"""
Run all evaluation approaches and compare against gold standard.

This script loads the manually labeled gold set and evaluates different
skill extraction and evidence leveling approaches.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np
from collections import defaultdict, Counter
import re

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sklearn.metrics import precision_recall_fscore_support, accuracy_score, cohen_kappa_score

GOLD_SET_FILE = Path(__file__).parent / "gold_set.json"

def load_gold_set() -> List[Dict]:
    """Load the manually labeled gold standard."""
    with open(GOLD_SET_FILE) as f:
        data = json.load(f)
    return data["examples"]

def regex_baseline(bullet: str, skill: str) -> int:
    """Baseline: regex matching with simple rules."""
    bullet_lower = bullet.lower()
    skill_lower = skill.lower()
    
    # Skill not mentioned = 0
    if skill_lower not in bullet_lower:
        return 0
    
    # Check for leadership verbs
    leadership_verbs = ['led', 'architected', 'owned', 'designed', 'drove', 'managed']
    if any(verb in bullet_lower for verb in leadership_verbs):
        return 4
    
    # Check for strong verbs
    strong_verbs = ['developed', 'built', 'implemented', 'created', 'deployed']
    if any(verb in bullet_lower for verb in strong_verbs):
        return 3
    
    # Check for weak verbs
    weak_verbs = ['assisted', 'helped', 'supported', 'worked with']
    if any(verb in bullet_lower for verb in weak_verbs):
        return 2
    
    # Default if mentioned
    return 1

def bm25_baseline(bullet: str, skill: str) -> int:
    """BM25-based scoring with thresholds."""
    # Simplified BM25-like scoring
    terms = bullet.lower().split()
    skill_terms = skill.lower().split()
    
    # Calculate term frequency
    tf_score = sum(terms.count(term) for term in skill_terms)
    
    if tf_score == 0:
        return 0
    elif tf_score >= 3:
        return 3
    elif tf_score >= 2:
        return 2
    else:
        return 1

def embedding_only(bullet: str, skill: str) -> int:
    """Embedding-based approach (mock implementation)."""
    # Mock semantic similarity scoring
    skill_lower = skill.lower()
    bullet_lower = bullet.lower()
    
    # Simple keyword matching as proxy for embeddings
    if skill_lower not in bullet_lower:
        return 0
    
    # Length-based proxy for context richness
    context_score = len(bullet_lower) / 100
    
    if context_score > 2.0:
        return 4
    elif context_score > 1.5:
        return 3
    elif context_score > 1.0:
        return 2
    else:
        return 1

def full_cascade(bullet: str, skill: str) -> int:
    """Full approach combining regex, BM25, and embedding signals."""
    # Start with regex baseline
    regex_level = regex_baseline(bullet, skill)
    
    # Adjust based on BM25
    bm25_level = bm25_baseline(bullet, skill)
    
    # Adjust based on embeddings  
    embedding_level = embedding_only(bullet, skill)
    
    # Take maximum signal
    return max(regex_level, bm25_level, embedding_level)

def bootstrap_ci(y_true: List, y_pred: List, n_iterations: int = 1000) -> Tuple[float, float, float]:
    """Calculate bootstrapped confidence intervals for F1 score."""
    scores = []
    n = len(y_true)

    for _ in range(n_iterations):
        # Resample indices
        indices = np.random.choice(n, n, replace=True)
        y_true_boot = [y_true[i] for i in indices]
        y_pred_boot = [y_pred[i] for i in indices]

        # Calculate F1 score — skip if only one class in this resample
        if len(set(y_true_boot)) > 1:
            _, _, f1, _ = precision_recall_fscore_support(
                y_true_boot, y_pred_boot, average='weighted', zero_division=0
            )
            scores.append(f1)

    if not scores:
        return 0.0, 0.0, 0.0

    # Calculate confidence interval
    scores = sorted(scores)
    ci_lower = np.percentile(scores, 2.5)
    ci_upper = np.percentile(scores, 97.5)
    mean_f1 = np.mean(scores)

    return mean_f1, ci_lower, ci_upper

def quadratic_weighted_kappa(y_true: List[int], y_pred: List[int]) -> float:
    """Calculate quadratic weighted kappa for ordinal data."""
    # Convert to numpy arrays
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # Get unique labels
    labels = sorted(set(list(y_true) + list(y_pred)))
    n_labels = len(labels)
    
    # Build weight matrix (quadratic)
    weights = np.zeros((n_labels, n_labels))
    for i in range(n_labels):
        for j in range(n_labels):
            weights[i][j] = (i - j) ** 2
    
    # Build confusion matrix
    hist = np.zeros((n_labels, n_labels))
    for t, p in zip(y_true, y_pred):
        hist[labels.index(t)][labels.index(p)] += 1
    
    # Calculate kappa
    sum_hist = np.sum(hist)
    if sum_hist == 0:
        return 0.0
    
    # Expected matrix
    expected = np.outer(np.sum(hist, axis=1), np.sum(hist, axis=0)) / sum_hist
    
    # Weighted sums
    nom = np.sum(weights * hist)
    den = np.sum(weights * expected)
    
    if den == 0:
        return 0.0
    
    return 1.0 - nom / den

def evaluate_approach(approach_func, gold_examples: List[Dict], approach_name: str) -> Dict:
    """Evaluate a single approach against gold standard."""
    y_true = []
    y_pred = []
    
    for example in gold_examples:
        bullet = example["bullet"]
        for skill, gold_data in example["skills"].items():
            true_level = gold_data["level"]
            pred_level = approach_func(bullet, skill)
            
            y_true.append(true_level)
            y_pred.append(pred_level)
    
    # Calculate metrics
    if len(set(y_true)) > 1:
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        f1_mean, f1_ci_lower, f1_ci_upper = bootstrap_ci(y_true, y_pred)
        kappa = quadratic_weighted_kappa(y_true, y_pred)
    else:
        precision = recall = f1 = f1_mean = f1_ci_lower = f1_ci_upper = kappa = 0.0
    
    return {
        "approach": approach_name,
        "precision": precision,
        "recall": recall, 
        "f1": f1_mean,
        "f1_ci": (f1_ci_lower, f1_ci_upper),
        "kappa": kappa,
        "y_true": y_true,
        "y_pred": y_pred
    }

def print_confusion_matrix(y_true: List[int], y_pred: List[int], approach_name: str):
    """Print confusion matrix for evidence levels."""
    labels = sorted(set(y_true + y_pred))
    
    print(f"\nConfusion Matrix - {approach_name}")
    print("True\\Pred", end="")
    for pred_label in labels:
        print(f"{pred_label:6}", end="")
    print()
    
    for true_label in labels:
        print(f"{true_label:8}", end="")
        for pred_label in labels:
            count = sum(1 for t, p in zip(y_true, y_pred) if t == true_label and p == pred_label)
            print(f"{count:6}", end="")
        print()

UNLABELED_CORPUS_FILE = Path(__file__).parent / "corpus" / "unlabeled_pairs.json"


def count_unlabeled() -> int:
    """Return number of pairs in the unlabeled corpus (for informational display)."""
    if not UNLABELED_CORPUS_FILE.exists():
        return 0
    try:
        with open(UNLABELED_CORPUS_FILE) as f:
            data = json.load(f)
        return len(data.get("pairs", []))
    except Exception:
        return 0


def main():
    # Check if gold set exists
    if not GOLD_SET_FILE.exists():
        print(f"Gold set not found at {GOLD_SET_FILE}")
        print("Please run label.py first to create labeled examples.")
        n_unlabeled = count_unlabeled()
        if n_unlabeled:
            print(f"\n{n_unlabeled} unlabeled pairs are waiting in evals/corpus/unlabeled_pairs.json")
            print("Open that file and run: python evals/label.py --resume-file <file>")
            print("See evals/ANNOTATION_GUIDE.md for labeling instructions.")
        return

    # Load gold standard
    gold_examples = load_gold_set()

    if not gold_examples:
        n_unlabeled = count_unlabeled()
        print("=" * 60)
        print("NO LABELED EXAMPLES YET — eval harness ready but empty.")
        print("=" * 60)
        print()
        if n_unlabeled:
            print(f"  {n_unlabeled} unlabeled pairs available in evals/corpus/unlabeled_pairs.json")
        print("  Next steps:")
        print("  1. Run: python evals/label.py")
        print("     (or open ANNOTATION_GUIDE.md and label evals/corpus/unlabeled_pairs.json manually)")
        print("  2. Label at least 100 (resume, skill) pairs")
        print("  3. Re-run: python evals/run_all.py")
        print()
        print("  The harness is working correctly. This is the expected state before")
        print("  any manual labeling has been done.")
        return

    print(f"Evaluating against {len(gold_examples)} labeled examples...")
    
    total_skills = sum(len(ex["skills"]) for ex in gold_examples)
    print(f"Total skill instances: {total_skills}")
    
    # Define approaches
    approaches = [
        (regex_baseline, "regex_baseline"),
        (bm25_baseline, "bm25_baseline"), 
        (embedding_only, "embedding_only"),
        (full_cascade, "full_cascade")
    ]
    
    # Evaluate each approach
    results = []
    for approach_func, name in approaches:
        print(f"\nEvaluating {name}...")
        result = evaluate_approach(approach_func, gold_examples, name)
        results.append(result)
    
    # Print comparison table
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    print(f"{'Approach':<20} {'P':>6} {'R':>6} {'F1':>6} {'±95% CI':>12} {'Kappa':>8}")
    print("-" * 80)
    
    for result in results:
        ci_str = f"±{(result['f1_ci'][1] - result['f1_ci'][0])/2:.3f}"
        print(f"{result['approach']:<20} "
              f"{result['precision']:>6.3f} "
              f"{result['recall']:>6.3f} " 
              f"{result['f1']:>6.3f} "
              f"{ci_str:>12} "
              f"{result['kappa']:>8.3f}")
    
    # Print confusion matrices
    for result in results:
        print_confusion_matrix(result['y_true'], result['y_pred'], result['approach'])
    
    # Save results
    results_file = Path(__file__).parent / "results" / "evaluation_results.json"
    results_file.parent.mkdir(exist_ok=True)
    
    # Prepare JSON-serializable results
    json_results = []
    for result in results:
        json_result = result.copy()
        # f1_ci is a tuple — convert to list for JSON serialization
        json_result['f1_ci'] = list(json_result['f1_ci'])
        json_results.append(json_result)
    
    with open(results_file, 'w') as f:
        json.dump({
            "evaluation_date": "2026-07-25",
            "total_examples": len(gold_examples),
            "total_skills": total_skills,
            "results": json_results
        }, f, indent=2)
    
    print(f"\nResults saved to {results_file}")

if __name__ == "__main__":
    main()