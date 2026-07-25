#!/usr/bin/env python3
"""
Sweep semantic threshold from 0.60 to 0.90 and plot F1 with confidence intervals.
"""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple, Dict

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from sklearn.metrics import precision_recall_fscore_support

GOLD_SET_FILE = Path(__file__).parent / "gold_set.json"

def load_gold_set() -> List[Dict]:
    """Load the manually labeled gold standard."""
    with open(GOLD_SET_FILE) as f:
        data = json.load(f)
    return data["examples"]

def semantic_threshold_approach(bullet: str, skill: str, threshold: float) -> int:
    """Mock semantic approach with configurable threshold."""
    # Simulate embedding similarity scoring
    skill_lower = skill.lower()
    bullet_lower = bullet.lower()
    
    if skill_lower not in bullet_lower:
        return 0
    
    # Mock similarity score based on context richness
    # In real implementation, this would use actual embeddings
    context_words = len(bullet_lower.split())
    skill_mentions = bullet_lower.count(skill_lower)
    
    # Simulate similarity score (0.0 to 1.0)
    sim_score = min(1.0, (context_words * skill_mentions) / 50.0)
    
    if sim_score < threshold:
        return 0
    elif sim_score > 0.85:
        return 3
    elif sim_score > 0.75:
        return 2
    else:
        return 1

def bootstrap_f1(y_true: List, y_pred: List, n_iterations: int = 1000) -> Tuple[float, float, float]:
    """Calculate bootstrapped F1 score with confidence interval."""
    scores = []
    n = len(y_true)
    
    for _ in range(n_iterations):
        indices = np.random.choice(n, n, replace=True)
        y_true_boot = [y_true[i] for i in indices]
        y_pred_boot = [y_pred[i] for i in indices]
        
        if len(set(y_true_boot)) > 1 and len(set(y_pred_boot)) > 1:
            _, _, f1, _ = precision_recall_fscore_support(y_true_boot, y_pred_boot, average='weighted', zero_division=0)
            scores.append(f1)
    
    if scores:
        scores = sorted(scores)
        mean_f1 = np.mean(scores)
        ci_lower = np.percentile(scores, 2.5)
        ci_upper = np.percentile(scores, 97.5)
        return mean_f1, ci_lower, ci_upper
    else:
        return 0.0, 0.0, 0.0

def evaluate_threshold(threshold: float, gold_examples: List[Dict]) -> Tuple[float, float, float]:
    """Evaluate semantic approach at given threshold."""
    y_true = []
    y_pred = []
    
    for example in gold_examples:
        bullet = example["bullet"]
        for skill, gold_data in example["skills"].items():
            true_level = gold_data["level"]
            pred_level = semantic_threshold_approach(bullet, skill, threshold)
            
            y_true.append(true_level)
            y_pred.append(pred_level)
    
    return bootstrap_f1(y_true, y_pred)

def main():
    # Check if gold set exists
    if not GOLD_SET_FILE.exists():
        print(f"Gold set not found at {GOLD_SET_FILE}")
        print("Please run label.py first to create labeled examples.")
        return
    
    # Load gold standard
    gold_examples = load_gold_set()
    
    if not gold_examples:
        print("No labeled examples found in gold set.")
        return
    
    print("Sweeping semantic threshold from 0.60 to 0.90...")
    
    # Sweep thresholds
    thresholds = np.arange(0.60, 0.91, 0.01)
    results = []
    
    for i, threshold in enumerate(thresholds):
        print(f"Evaluating threshold {threshold:.2f} ({i+1}/{len(thresholds)})")
        mean_f1, ci_lower, ci_upper = evaluate_threshold(threshold, gold_examples)
        results.append({
            "threshold": threshold,
            "f1_mean": mean_f1,
            "f1_ci_lower": ci_lower,
            "f1_ci_upper": ci_upper
        })
    
    # Find peak F1
    best_result = max(results, key=lambda x: x["f1_mean"])
    best_threshold = best_result["threshold"]
    best_f1 = best_result["f1_mean"]
    
    print(f"\nBest threshold: {best_threshold:.2f}")
    print(f"Best F1 score: {best_f1:.3f}")
    
    # Create plot
    plt.figure(figsize=(10, 6))
    
    thresholds_plot = [r["threshold"] for r in results]
    f1_means = [r["f1_mean"] for r in results]
    f1_lowers = [r["f1_ci_lower"] for r in results]
    f1_uppers = [r["f1_ci_upper"] for r in results]
    
    # Plot F1 curve with confidence bands
    plt.plot(thresholds_plot, f1_means, 'b-', linewidth=2, label='F1 Score')
    plt.fill_between(thresholds_plot, f1_lowers, f1_uppers, alpha=0.3, color='blue', label='95% CI')
    
    # Mark best threshold
    plt.axvline(x=best_threshold, color='red', linestyle='--', alpha=0.7, label=f'Peak: {best_threshold:.2f}')
    plt.plot(best_threshold, best_f1, 'ro', markersize=8)
    
    plt.xlabel('Semantic Threshold')
    plt.ylabel('F1 Score')
    plt.title('Semantic Threshold Sweep - F1 Score with 95% Confidence Intervals')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0.60, 0.90)
    
    # Save plot
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    plot_file = results_dir / "threshold_sweep.png"
    
    plt.tight_layout()
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {plot_file}")
    
    # Save results data
    results_file = results_dir / "threshold_sweep_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "best_threshold": best_threshold,
            "best_f1": best_f1,
            "sweep_results": results
        }, f, indent=2)
    
    print(f"Results saved to {results_file}")
    
    # Display plot
    plt.show()

if __name__ == "__main__":
    main()