#!/usr/bin/env python3
"""
Test script to identify which tasks are returning boundary scores (0.0 or 1.0)
"""

from content_moderation_env.graders import ModeratorGrader

def test_all_tasks():
    """Test all 30 tasks with various prediction/ground_truth combinations"""
    grader = ModeratorGrader()
    
    # Sample prediction and ground truth data
    prediction = {
        "category": "hate_speech",
        "severity": 3,
        "action": "remove",
        "reasoning": "This contains hateful content targeting a protected group",
        "tone": "hostile",
        "is_coordinated": False,
        "confidence": 0.85,
        "is_false_positive": False,
        "policy_exception": False,
        "verdict": "uphold",
        "safety": "explicit",
        "toxicity": "high",
        "image_assessment": "safe",
        "text_assessment": "unsafe",
        "authenticity": "real",
        "workplace": "inappropriate",
        "home": "inappropriate",
        "public": "inappropriate",
        "credibility": "high",
        "is_bot": False,
        "coordination": "solo",
        "veracity": "false",
        "appeal_validity": "invalid",
        "trust_score": 7,
        "campaign_likelihood": "high",
        "spread_rate": "fast",
        "severity": "high",
        "consistency": "consistent",
        "classification": "satire",
        "appropriateness": "appropriate",
        "action": "label",
    }
    
    ground_truth = {
        "category": "hate_speech",
        "severity": 3,
        "action": "remove",
        "tone": "hostile",
        "is_coordinated": False,
        "confidence": 0.8,
        "is_false_positive": False,
        "policy_exception": False,
        "verdict": "uphold",
        "safety": "explicit",
        "toxicity": "high",
        "image_assessment": "safe",
        "text_assessment": "unsafe",
        "authenticity": "real",
        "workplace": "inappropriate",
        "home": "inappropriate",
        "public": "inappropriate",
        "credibility": "high",
        "is_bot": False,
        "coordination": "solo",
        "veracity": "false",
        "appeal_validity": "invalid",
        "trust_score": 7,
        "campaign_likelihood": "high",
        "spread_rate": "fast",
        "severity": "high",
        "consistency": "consistent",
        "classification": "satire",
        "appropriateness": "appropriate",
    }
    
    print("Testing all 30 tasks for boundary violations (0.0 or 1.0)...")
    print("=" * 70)
    
    violations = []
    for task_id in range(1, 31):
        score = grader.grade(task_id, prediction, ground_truth, use_cache=False)
        
        # Check for boundary violations
        if score <= 0.0 or score >= 1.0:
            violations.append((task_id, score))
            status = "❌ BOUNDARY VIOLATION"
        elif score < 0.001 or score > 0.999:
            status = "⚠️  EXTREME VALUE"
        else:
            status = "✅ SAFE"
        
        print(f"Task {task_id:2d}: {score:.6f} {status}")
    
    print("=" * 70)
    
    if violations:
        print(f"\n❌ FOUND {len(violations)} BOUNDARY VIOLATIONS:")
        for task_id, score in violations:
            print(f"  - Task {task_id}: {score}")
        return False
    else:
        print("\n✅ ALL TASKS PASSED - No boundary violations detected")
        return True

if __name__ == "__main__":
    success = test_all_tasks()
    exit(0 if success else 1)
