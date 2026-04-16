#!/usr/bin/env python3
"""
Learning First Principles Analyzer
Analyzes if learning behaviors align with first principles
"""

import json
import sys
from typing import Dict, List, Tuple

# Principle Chain
PRINCIPLE_CHAIN = [
    ("Learning View", "Self-learning", "Tutoring/External Input"),
    ("Methodology", "Induction & Summary", "Time-consuming/Mechanical Repetition"),
    ("Processing", "Self-output", "Mechanical Copying"),
    ("Output", "Expression Restructuring", "Simple Repetition"),
    ("Expression", "Logic-driven", "Form/Template"),
    ("Understanding", "Practice", "Stopping at Theory")
]

# Keyword Pattern Matching
PATTERNS = {
    "Self-learning Drive": {
        "positive": ["self-study", "autonomous", "curiosity", "want to learn", "goal is", "for the purpose of", "my own decision", "interested in"],
        "negative": ["training class", "teacher teaches", "forced", "have to", "schedule", "others told me", "assigned", "required"]
    },
    "Induction & Summary": {
        "positive": ["summarize", "extract", "patterns", "framework", "core", "essence", "key points", "underlying logic"],
        "negative": ["practice problems", "repeat", "memorize", "remember", "time-wasting", "no thinking", "rote learning", "just reading"]
    },
    "Self-output": {
        "positive": ["explain", "write out", "output", "share", "teach others", "my own words", "in my own words", "summarize myself"],
        "negative": ["copy notes", "copy", "extract", "record", "transcribe", "just write down"]
    },
    "Expression Restructuring": {
        "positive": ["reorganize", "different angle", "diagram", "analogy", "restructure", "reframe", "different perspective", "simplify"],
        "negative": ["original text", "original words", "copy directly", "same", "verbatim", "word for word"]
    },
    "Logic-driven": {
        "positive": ["why", "principle", "cause and effect", "understand", "underlying", "reasoning", "logic", "because"],
        "negative": ["apply template", "steps", "template", "follow blindly", "don't know", "just do it", "without understanding"]
    },
    "Practice Verification": {
        "positive": ["use", "practice", "do", "verify", "experiment", "project", "apply", "build", "create"],
        "negative": ["finished learning", "understood", "theoretically", "someday", "plan to", "will do later"]
    }
}


def analyze_text(text: str) -> Dict[str, Tuple[int, List[str]]]:
    """Analyze text, return scores and matched keywords for each dimension"""
    text = text.lower()
    results = {}

    for dimension, pattern in PATTERNS.items():
        pos_matches = [w for w in pattern["positive"] if w in text]
        neg_matches = [w for w in pattern["negative"] if w in text]

        if neg_matches:
            score = 0
        elif pos_matches:
            score = 2
        else:
            score = 1

        results[dimension] = (score, pos_matches + neg_matches)

    return results


def generate_diagnosis(analysis: Dict) -> List[str]:
    """Generate problem diagnosis"""
    diagnosis = []

    for dim, (score, _) in analysis.items():
        if score == 0:
            for principle, positive, negative in PRINCIPLE_CHAIN:
                if dim in principle or principle in dim:
                    diagnosis.append(f"- {dim}: In {negative} mode, instead of {positive}")
                    break

    return diagnosis


def generate_actions(analysis: Dict) -> List[str]:
    """Generate improvement suggestions"""
    actions = []

    dimension_actions = {
        "Self-learning Drive": "Set an autonomous learning goal instead of following external curriculum",
        "Induction & Summary": "Spend 10 minutes extracting 3 core points after learning, instead of continuing to drill",
        "Self-output": "Try to restate in your own words instead of copying from textbook",
        "Expression Restructuring": "Explain this concept using an analogy or story",
        "Logic-driven": "Ask yourself three 'whys' to trace back to underlying principles",
        "Practice Verification": "Design a minimal experiment to verify understanding through practice"
    }

    for dim, (score, _) in analysis.items():
        if score < 2:
            actions.append(f"{dim} Improvement: {dimension_actions.get(dim, 'Reflect on current method')}")

    return actions[:3]  # Maximum 3 actions


def calculate_efficiency(analysis: Dict, time_hours: float) -> Dict:
    """Evaluate efficiency"""
    total = sum(score for score, _ in analysis.values())
    max_score = len(analysis) * 2

    if total <= 4:
        current_roi = "Low"
        improved_roi = "High"
        reason = "Passive learning mode, high forgetting rate, poor transferability"
    elif total <= 8:
        current_roi = "Medium"
        improved_roi = "High"
        reason = "Conscious but not internalized, insufficient output and restructuring"
    else:
        current_roi = "High"
        improved_roi = "High"
        reason = "First principles driven, continuous practice verification"

    return {
        "current_score": f"{total}/{max_score}",
        "current_roi": current_roi,
        "improved_roi": improved_roi,
        "reason": reason,
        "time_recommendation": f"Current: {time_hours} hours/week, Recommended: {time_hours * 0.7:.1f} hours learning + {time_hours * 0.3:.1f} hours output practice"
    }


def analyze_learning(input_data: str) -> str:
    """Main analysis function"""
    # Try to parse JSON
    try:
        data = json.loads(input_data)
        text = f"{data.get('Learning Content', '')} {data.get('Current Method', '')} {data.get('Confusion', '')}"
        time_hours = float(data.get('Time Investment', 1))
    except json.JSONDecodeError:
        # Direct text analysis
        text = input_data
        time_hours = 1

    # Analyze
    analysis = analyze_text(text)
    diagnosis = generate_diagnosis(analysis)
    actions = generate_actions(analysis)
    efficiency = calculate_efficiency(analysis, time_hours)

    # Build output
    output = []
    output.append("## Learning First Principles Analysis Report\n")

    output.append("### 1. Current Status Diagnosis")
    if diagnosis:
        output.extend(diagnosis)
    else:
        output.append("- No obvious patterns violating first principles detected")

    output.append("\n### 2. Improvement Suggestions")
    for i, action in enumerate(actions, 1):
        output.append(f"{i}. {action}")

    output.append("\n### 3. Efficiency Assessment")
    output.append(f"- Current Score: {efficiency['current_score']}")
    output.append(f"- Current ROI: {efficiency['current_roi']}")
    output.append(f"- Improved ROI: {efficiency['improved_roi']}")
    output.append(f"- Reason: {efficiency['reason']}")
    output.append(f"- Adjustment Recommendation: {efficiency['time_recommendation']}")

    output.append("\n### 4. Principle Chain Comparison")
    for dim, (score, _) in analysis.items():
        for principle, positive, negative in PRINCIPLE_CHAIN:
            if dim in principle or principle in dim:
                status = "✓" if score == 2 else ("△" if score == 1 else "✗")
                output.append(f"{status} {principle}: {positive if score >= 1 else negative}")
                break

    return "\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = analyze_learning(sys.argv[1])
        print(result)
    else:
        print("Usage: python analyze.py '<learning description>'")
        print("Or: python analyze.py '<json data>'")
