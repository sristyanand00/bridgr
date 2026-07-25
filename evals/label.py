#!/usr/bin/env python3
"""
Interactive labeling tool for creating gold standard evidence level dataset.

Usage: python label.py [--resume-file] [--continue]
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

GOLD_SET_FILE = Path(__file__).parent / "gold_set.json"

def load_existing_labels() -> Dict:
    """Load existing labeled data if available."""
    if GOLD_SET_FILE.exists():
        with open(GOLD_SET_FILE) as f:
            return json.load(f)
    return {"metadata": {"created": None, "annotator": None, "version": "1.0"}, "examples": []}

def save_labels(data: Dict):
    """Save labeled data to JSON file."""
    with open(GOLD_SET_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def extract_bullets_from_resume(resume_text: str) -> List[str]:
    """Extract individual bullet points from resume text."""
    lines = resume_text.split('\n')
    bullets = []
    
    for line in lines:
        line = line.strip()
        # Look for bullet-like lines
        if (line.startswith(('•', '-', '*', '◦')) or 
            line.startswith(('- ', '• ', '* ', '◦ ')) or
            (len(line) > 20 and any(word in line.lower() for word in 
            ['developed', 'built', 'implemented', 'designed', 'led', 'managed', 'created']))):
            bullets.append(line)
    
    return bullets

def display_bullet(bullet: str, bullet_num: int, total: int):
    """Display a bullet point for annotation."""
    print("\n" + "="*80)
    print(f"BULLET {bullet_num}/{total}")
    print("="*80)
    print(f"\n{bullet}\n")

def get_skills_in_bullet(bullet: str) -> List[str]:
    """Interactive skill identification."""
    print("What skills/technologies are mentioned in this bullet?")
    print("Enter each skill on a separate line. Press Enter twice when done.")
    print("(Examples: python, react, sql, docker, machine learning, etc.)")
    
    skills = []
    while True:
        skill = input(f"Skill {len(skills)+1}: ").strip().lower()
        if not skill:
            break
        skills.append(skill)
    
    return skills

def get_evidence_level(skill: str, bullet: str) -> int:
    """Interactive evidence level assignment."""
    print(f"\nEVIDENCE LEVEL for '{skill}' in:")
    print(f"  \"{bullet}\"")
    print("\nLevels:")
    print("  0 = Absent (not mentioned)")
    print("  1 = Claimed (skills section only)")  
    print("  2 = Exposed (project/weak verb/short tenure)")
    print("  3 = Applied (professional + strong verb + 6+ months)")
    print("  4 = Owned (level 3 + leadership/scope/24+ months)")
    
    while True:
        try:
            level = int(input(f"\nLevel for '{skill}' [0-4]: "))
            if 0 <= level <= 4:
                return level
            print("Please enter 0, 1, 2, 3, or 4")
        except ValueError:
            print("Please enter a valid number")

def get_reasoning(skill: str, level: int) -> str:
    """Get reasoning for evidence level assignment."""
    if level >= 3:
        return input(f"Brief reasoning for level {level}: ").strip()
    return ""

def main():
    parser = argparse.ArgumentParser(description="Interactive evidence level labeling tool")
    parser.add_argument("--resume-file", help="Resume file to label")
    parser.add_argument("--continue", action="store_true", help="Continue existing session")
    args = parser.parse_args()

    # Load existing data
    data = load_existing_labels()
    
    if not args.continue:
        # Initialize new session
        print("Evidence Level Labeling Tool")
        print("============================")
        
        annotator = input("Your name: ").strip()
        if annotator:
            data["metadata"]["annotator"] = annotator
            data["metadata"]["created"] = "2026-07-25"
    
    # Get resume text
    if args.resume_file:
        with open(args.resume_file) as f:
            resume_text = f.read()
    else:
        print("\nPaste resume text (end with Ctrl+D on Unix or Ctrl+Z on Windows):")
        resume_text = sys.stdin.read()
    
    # Extract bullets
    bullets = extract_bullets_from_resume(resume_text)
    
    if not bullets:
        print("No bullet points found. Please check resume format.")
        return
    
    print(f"\nFound {len(bullets)} bullet points to label.")
    
    # Process each bullet
    start_idx = len(data["examples"]) if args.continue else 0
    
    try:
        for i, bullet in enumerate(bullets[start_idx:], start_idx + 1):
            display_bullet(bullet, i, len(bullets))
            
            # Get skills in this bullet
            skills = get_skills_in_bullet(bullet)
            
            if not skills:
                print("No skills identified, skipping bullet.")
                continue
            
            # Label each skill
            example = {
                "bullet": bullet,
                "skills": {}
            }
            
            for skill in skills:
                level = get_evidence_level(skill, bullet)
                reasoning = get_reasoning(skill, level)
                
                example["skills"][skill] = {
                    "level": level,
                    "reasoning": reasoning
                }
            
            # Save example
            data["examples"].append(example)
            
            # Save progress periodically
            save_labels(data)
            
            # Check if user wants to continue
            if i < len(bullets):
                continue_labeling = input("\nContinue to next bullet? [Y/n]: ").strip().lower()
                if continue_labeling == 'n':
                    break
    
    except KeyboardInterrupt:
        print("\n\nLabeling interrupted. Progress saved.")
    
    # Final save
    save_labels(data)
    
    print(f"\nLabeling complete! {len(data['examples'])} examples saved to {GOLD_SET_FILE}")
    
    # Show summary
    total_skills = sum(len(ex["skills"]) for ex in data["examples"])
    level_counts = {}
    for example in data["examples"]:
        for skill_data in example["skills"].values():
            level = skill_data["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
    
    print(f"\nSummary:")
    print(f"  Total skill instances: {total_skills}")
    for level in sorted(level_counts.keys()):
        count = level_counts[level]
        pct = count / total_skills * 100
        print(f"  Level {level}: {count} ({pct:.1f}%)")

if __name__ == "__main__":
    main()