"""
Lunar Content Moderation Benchmark — Domain-Specific Graders

Three grading systems with genuinely different evaluation mechanics:

1. TextClassificationGrader — multi-factor scoring: category + severity + reasoning quality
2. ContextualPolicyGrader   — context-aware: policy compliance + context usage + edge case handling
3. ThreatAssessmentGrader   — threat pipeline: detection + severity + response plan + confidence calibration

All scores are STRICTLY within (0, 1) — never 0.0 or 1.0.
"""

from typing import Dict, Any, List, Optional
import re
import math


# ─── Constants ──────────────────────────────────────────────────────────────

SCORE_MIN = 0.01
SCORE_MAX = 0.99
SCORE_DEFAULT = 0.5


def safe_clamp(score: float) -> float:
    """Ensure score is strictly within (0, 1). Single source of truth."""
    try:
        score = float(score)
    except (ValueError, TypeError):
        return SCORE_DEFAULT
    if score != score or score == float('inf') or score == float('-inf'):
        return SCORE_DEFAULT
    if score <= 0.0:
        return SCORE_MIN
    if score >= 1.0:
        return SCORE_MAX
    score = round(score, 4)
    if score <= 0.0 or score >= 1.0:
        return SCORE_DEFAULT
    return score


# ─── Task Metadata Registry ────────────────────────────────────────────────

TASK_DOMAINS = {
    # Domain 1: Text Classification (Tasks 1-10)
    1: "text_classification", 2: "text_classification", 3: "text_classification",
    4: "text_classification", 5: "text_classification", 6: "text_classification",
    7: "text_classification", 8: "text_classification", 9: "text_classification",
    10: "text_classification",
    # Domain 2: Contextual Policy (Tasks 11-20)
    11: "contextual_policy", 12: "contextual_policy", 13: "contextual_policy",
    14: "contextual_policy", 15: "contextual_policy", 16: "contextual_policy",
    17: "contextual_policy", 18: "contextual_policy", 19: "contextual_policy",
    20: "contextual_policy",
    # Domain 3: Threat Assessment (Tasks 21-30)
    21: "threat_assessment", 22: "threat_assessment", 23: "threat_assessment",
    24: "threat_assessment", 25: "threat_assessment", 26: "threat_assessment",
    27: "threat_assessment", 28: "threat_assessment", 29: "threat_assessment",
    30: "threat_assessment",
}

TASK_DIFFICULTIES = {
    1: "easy", 2: "easy", 3: "easy", 4: "medium", 5: "medium",
    6: "medium", 7: "hard", 8: "hard", 9: "hard", 10: "hard",
    11: "easy", 12: "easy", 13: "easy", 14: "medium", 15: "medium",
    16: "medium", 17: "hard", 18: "hard", 19: "hard", 20: "hard",
    21: "easy", 22: "easy", 23: "medium", 24: "medium", 25: "medium",
    26: "hard", 27: "hard", 28: "hard", 29: "hard", 30: "hard",
}


# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN 1 — TEXT CLASSIFICATION GRADER (Tasks 1-10)
# Multi-factor scoring: category + severity + reasoning quality
# ═══════════════════════════════════════════════════════════════════════════

class TextClassificationGrader:
    """
    Grades text classification tasks with tiered partial credit.

    Reward breakdown:
      0.05  Empty / invalid response
      0.15  Valid format but wrong category
      0.30  Correct category, wrong severity (off by 2+)
      0.50  Correct category, close severity (off by 1)
      0.70  Correct category + exact severity, weak reasoning
      0.85  All correct with good reasoning
      0.95  Perfect: all correct + expert-level reasoning with policy citations
    """

    VALID_CATEGORIES = {"safe", "hate_speech", "spam", "misinformation", "harassment", "violence"}

    QUALITY_KEYWORDS = {
        "basic": ["because", "since", "due to", "reason"],
        "good": ["context", "intent", "pattern", "history", "policy", "guideline"],
        "expert": ["precedent", "false positive", "edge case", "cultural",
                    "systematic", "coordinated", "escalation protocol", "severity assessment"],
    }

    def grade(self, task_id: int, prediction: Dict[str, Any],
              ground_truth: Dict[str, Any], step_num: int = 1) -> tuple:
        """
        Returns (score, feedback_str, done).
        """
        difficulty = TASK_DIFFICULTIES.get(task_id, "easy")
        weights = self._get_weights(difficulty)

        scores = {}
        feedback_parts = []

        # ── Category accuracy ──
        pred_cat = str(prediction.get("category", "")).lower().strip()
        true_cat = str(ground_truth.get("category", "")).lower().strip()

        if not pred_cat or pred_cat not in self.VALID_CATEGORIES:
            scores["category"] = 0.05
            feedback_parts.append(f"Invalid category '{pred_cat}'. Expected one of: {', '.join(sorted(self.VALID_CATEGORIES))}")
        elif pred_cat == true_cat:
            scores["category"] = 0.95
            feedback_parts.append(f"✓ Correct category: {true_cat}")
        elif pred_cat in self.VALID_CATEGORIES:
            # Partial credit for semantically close categories
            close_pairs = {
                ("hate_speech", "harassment"): 0.35,
                ("harassment", "hate_speech"): 0.35,
                ("spam", "misinformation"): 0.20,
                ("misinformation", "spam"): 0.20,
            }
            scores["category"] = close_pairs.get((pred_cat, true_cat), 0.10)
            feedback_parts.append(f"✗ Wrong category: predicted '{pred_cat}', expected '{true_cat}'")
        else:
            scores["category"] = 0.05
            feedback_parts.append(f"✗ Unrecognized category: '{pred_cat}'")

        # ── Severity accuracy ──
        try:
            pred_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            sev_diff = abs(pred_sev - true_sev)

            if sev_diff == 0:
                scores["severity"] = 0.95
                feedback_parts.append(f"✓ Exact severity match: {true_sev}")
            elif sev_diff == 1:
                scores["severity"] = 0.65
                feedback_parts.append(f"~ Close severity: predicted {pred_sev}, expected {true_sev}")
            elif sev_diff == 2:
                scores["severity"] = 0.35
                feedback_parts.append(f"✗ Severity off by {sev_diff}: predicted {pred_sev}, expected {true_sev}")
            else:
                scores["severity"] = 0.10
                feedback_parts.append(f"✗ Severity far off: predicted {pred_sev}, expected {true_sev}")
        except (ValueError, TypeError):
            scores["severity"] = 0.05
            feedback_parts.append("✗ Invalid severity value")

        # ── Reasoning quality ──
        reasoning = str(prediction.get("reasoning", "")).strip()
        scores["reasoning"] = self._score_reasoning(reasoning, pred_cat, true_cat)
        if scores["reasoning"] >= 0.8:
            feedback_parts.append("✓ Strong reasoning with context awareness")
        elif scores["reasoning"] >= 0.5:
            feedback_parts.append("~ Adequate reasoning, could cite specific policies")
        else:
            feedback_parts.append("✗ Weak or missing reasoning. Explain WHY this content falls into the chosen category.")

        # ── Action correctness (for medium/hard tasks) ──
        if difficulty in ("medium", "hard"):
            pred_act = str(prediction.get("action", "")).lower().strip()
            true_act = str(ground_truth.get("action", "")).lower().strip()
            if pred_act == true_act:
                scores["action"] = 0.95
                feedback_parts.append(f"✓ Correct action: {true_act}")
            elif pred_act in {"keep", "label", "warn", "remove", "escalate", "ban"}:
                scores["action"] = 0.20
                feedback_parts.append(f"✗ Wrong action: predicted '{pred_act}', expected '{true_act}'")
            else:
                scores["action"] = 0.05
                feedback_parts.append(f"✗ Invalid action: '{pred_act}'")

        # ── Weighted final score ──
        total = sum(scores[k] * weights.get(k, 0.0) for k in scores)
        total = safe_clamp(total)

        feedback = " | ".join(feedback_parts)
        done = step_num >= 5
        return total, feedback, done

    def _score_reasoning(self, reasoning: str, pred_cat: str, true_cat: str) -> float:
        """Score reasoning quality with tiered evaluation."""
        if not reasoning or len(reasoning) < 10:
            return 0.05

        reasoning_lower = reasoning.lower()
        score = 0.15  # Base score for any reasoning

        # Length bonus
        if len(reasoning) > 30:
            score += 0.10
        if len(reasoning) > 80:
            score += 0.10
        if len(reasoning) > 150:
            score += 0.10

        # Quality keyword matching
        basic_hits = sum(1 for kw in self.QUALITY_KEYWORDS["basic"] if kw in reasoning_lower)
        good_hits = sum(1 for kw in self.QUALITY_KEYWORDS["good"] if kw in reasoning_lower)
        expert_hits = sum(1 for kw in self.QUALITY_KEYWORDS["expert"] if kw in reasoning_lower)

        score += min(basic_hits * 0.05, 0.15)
        score += min(good_hits * 0.08, 0.20)
        score += min(expert_hits * 0.10, 0.20)

        return min(0.95, score)

    def _get_weights(self, difficulty: str) -> Dict[str, float]:
        """Get component weights based on difficulty."""
        if difficulty == "easy":
            return {"category": 0.60, "severity": 0.25, "reasoning": 0.15}
        elif difficulty == "medium":
            return {"category": 0.35, "severity": 0.20, "reasoning": 0.20, "action": 0.25}
        else:  # hard
            return {"category": 0.25, "severity": 0.15, "reasoning": 0.30, "action": 0.30}


# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN 2 — CONTEXTUAL POLICY GRADER (Tasks 11-20)
# Context-aware: policy compliance + context usage + edge case handling
# ═══════════════════════════════════════════════════════════════════════════

class ContextualPolicyGrader:
    """
    Grades contextual policy enforcement tasks.

    These tasks require the agent to consider:
    - Author history and credibility
    - Trending topics and policy exceptions
    - Cultural context and sensitivity
    - Appeal review fairness

    Reward breakdown:
      0.05  No meaningful response
      0.20  Response ignores context entirely
      0.40  Correct base decision but no context reference
      0.60  Good decision with some context awareness
      0.80  Correct with strong context integration
      0.95  Expert: considers edge cases, cultural factors, policy exceptions
    """

    CONTEXT_KEYWORDS = {
        "author_history": ["history", "prior", "violations", "previous", "record", "repeat", "recidiv"],
        "policy": ["policy", "guideline", "exception", "rule", "standard", "protocol", "compliance"],
        "culture": ["cultural", "region", "language", "community", "local", "norms", "sensitivity"],
        "trust": ["trust", "credibility", "reputation", "reliability", "legitimate", "authentic"],
        "appeal": ["appeal", "review", "overturn", "uphold", "fairness", "evidence", "precedent"],
        "trending": ["trending", "news", "current", "event", "public interest", "discourse"],
    }

    def grade(self, task_id: int, prediction: Dict[str, Any],
              ground_truth: Dict[str, Any], step_num: int = 1) -> tuple:
        """Returns (score, feedback_str, done)."""
        difficulty = TASK_DIFFICULTIES.get(task_id, "medium")
        scores = {}
        feedback_parts = []

        # ── Base decision accuracy ──
        pred_act = str(prediction.get("action", "")).lower().strip()
        true_act = str(ground_truth.get("action", "")).lower().strip()

        if pred_act == true_act:
            scores["decision"] = 0.95
            feedback_parts.append(f"✓ Correct moderation action: {true_act}")
        elif pred_act in {"keep", "label", "warn", "remove", "escalate", "ban"}:
            # Partial credit based on severity alignment
            action_severity = {"keep": 0, "label": 1, "warn": 2, "remove": 3, "escalate": 4, "ban": 5}
            pred_sev = action_severity.get(pred_act, 2)
            true_sev = action_severity.get(true_act, 2)
            diff = abs(pred_sev - true_sev)
            if diff == 1:
                scores["decision"] = 0.55
                feedback_parts.append(f"~ Close action: '{pred_act}' vs expected '{true_act}'")
            elif diff == 2:
                scores["decision"] = 0.30
                feedback_parts.append(f"✗ Action too {'severe' if pred_sev > true_sev else 'lenient'}: '{pred_act}' vs '{true_act}'")
            else:
                scores["decision"] = 0.10
                feedback_parts.append(f"✗ Wrong action: '{pred_act}', expected '{true_act}'")
        else:
            scores["decision"] = 0.05
            feedback_parts.append(f"✗ Invalid action: '{pred_act}'")

        # ── Category accuracy ──
        pred_cat = str(prediction.get("category", "")).lower().strip()
        true_cat = str(ground_truth.get("category", "")).lower().strip()
        if pred_cat == true_cat:
            scores["category"] = 0.95
        elif pred_cat:
            scores["category"] = 0.15
        else:
            scores["category"] = 0.05

        # ── Context awareness scoring ──
        reasoning = str(prediction.get("reasoning", "")).lower()
        context_score = self._score_context_usage(reasoning, task_id)
        scores["context"] = context_score

        if context_score >= 0.7:
            feedback_parts.append("✓ Strong context awareness in reasoning")
        elif context_score >= 0.4:
            feedback_parts.append("~ Some context awareness. Consider: author history, policy exceptions, cultural factors.")
        else:
            feedback_parts.append("✗ Reasoning ignores context. This task requires considering background factors.")

        # ── Policy exception handling (medium/hard) ──
        if difficulty in ("medium", "hard"):
            pred_exc = prediction.get("policy_exception")
            true_exc = ground_truth.get("policy_exception")
            if true_exc is not None:
                pred_exc_bool = str(pred_exc).lower() in ("true", "1", "yes") if pred_exc is not None else False
                true_exc_bool = str(true_exc).lower() in ("true", "1", "yes") if isinstance(true_exc, str) else bool(true_exc)
                if pred_exc_bool == true_exc_bool:
                    scores["policy_exception"] = 0.95
                    feedback_parts.append("✓ Policy exception correctly identified")
                else:
                    scores["policy_exception"] = 0.15
                    feedback_parts.append(f"✗ Policy exception wrong: predicted {pred_exc_bool}, expected {true_exc_bool}")

        # ── Edge case awareness (hard only) ──
        if difficulty == "hard":
            edge_case_score = self._score_edge_case_handling(reasoning)
            scores["edge_cases"] = edge_case_score
            if edge_case_score >= 0.6:
                feedback_parts.append("✓ Good edge case consideration")
            else:
                feedback_parts.append("~ Consider: false positives, sarcasm, cultural nuance, evolving policies")

        # ── Weights by difficulty ──
        if difficulty == "easy":
            weights = {"decision": 0.45, "category": 0.30, "context": 0.25}
        elif difficulty == "medium":
            weights = {"decision": 0.30, "category": 0.20, "context": 0.25, "policy_exception": 0.25}
        else:
            weights = {"decision": 0.25, "category": 0.15, "context": 0.25, "policy_exception": 0.15, "edge_cases": 0.20}

        total = sum(scores.get(k, 0.3) * w for k, w in weights.items())
        total = safe_clamp(total)

        feedback = " | ".join(feedback_parts)
        done = step_num >= 5
        return total, feedback, done

    def _score_context_usage(self, reasoning: str, task_id: int) -> float:
        """Score how well the agent uses available context."""
        if not reasoning or len(reasoning) < 10:
            return 0.05

        # Determine relevant context types for this task
        relevant_contexts = []
        if task_id in (11, 12, 15):
            relevant_contexts = ["author_history", "trust"]
        elif task_id in (13, 14, 18):
            relevant_contexts = ["policy", "trending"]
        elif task_id in (16, 17):
            relevant_contexts = ["culture", "policy"]
        elif task_id in (19, 20):
            relevant_contexts = ["appeal", "policy", "trust"]
        else:
            relevant_contexts = ["policy", "author_history"]

        total_hits = 0
        for ctx_type in relevant_contexts:
            keywords = self.CONTEXT_KEYWORDS.get(ctx_type, [])
            hits = sum(1 for kw in keywords if kw in reasoning)
            total_hits += min(hits, 3)  # Cap per-context

        # Scale: 0 hits → 0.10, 6+ hits → 0.95
        score = 0.10 + min(total_hits / 6.0, 1.0) * 0.85
        return min(0.95, score)

    def _score_edge_case_handling(self, reasoning: str) -> float:
        """Score edge case awareness in reasoning."""
        edge_keywords = [
            "false positive", "sarcasm", "irony", "satire", "context matters",
            "edge case", "exception", "nuance", "ambiguous", "borderline",
            "cultural difference", "evolving", "precedent"
        ]
        hits = sum(1 for kw in edge_keywords if kw in reasoning)
        return min(0.95, 0.10 + hits * 0.15)


# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN 3 — THREAT ASSESSMENT GRADER (Tasks 21-30)
# Threat pipeline: detection + severity + response plan + confidence
# ═══════════════════════════════════════════════════════════════════════════

class ThreatAssessmentGrader:
    """
    Grades threat assessment tasks: coordinated attacks, misinformation cascades,
    harassment networks.

    These tasks require multi-step analysis:
    1. Is there a threat? (detection)
    2. How severe? (severity assessment)
    3. What should be done? (response pipeline)
    4. How confident? (calibration)

    Reward breakdown:
      0.05  No meaningful response
      0.15  Response doesn't address threat detection
      0.30  Detected threat presence correctly
      0.50  Correct detection + severity in right range
      0.70  Detection + severity + reasonable response plan
      0.85  Comprehensive: detection + severity + response + confidence
      0.95  Expert: all above + network analysis + escalation protocol
    """

    THREAT_LEVELS = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}

    RESPONSE_KEYWORDS = {
        "investigate": ["investigate", "analyze", "examine", "review", "monitor"],
        "contain": ["remove", "disable", "block", "suspend", "quarantine"],
        "escalate": ["escalate", "alert", "team", "management", "report"],
        "prevent": ["prevent", "pattern", "detection", "automated", "rule", "filter"],
    }

    def grade(self, task_id: int, prediction: Dict[str, Any],
              ground_truth: Dict[str, Any], step_num: int = 1) -> tuple:
        """Returns (score, feedback_str, done)."""
        difficulty = TASK_DIFFICULTIES.get(task_id, "hard")
        scores = {}
        feedback_parts = []

        # ── Threat detection ──
        pred_coord = prediction.get("is_coordinated")
        true_coord = ground_truth.get("is_coordinated")

        pred_coord_bool = str(pred_coord).lower() in ("true", "1", "yes") if pred_coord is not None else None
        true_coord_bool = str(true_coord).lower() in ("true", "1", "yes") if isinstance(true_coord, str) else bool(true_coord) if true_coord is not None else None

        if pred_coord_bool is not None and true_coord_bool is not None:
            if pred_coord_bool == true_coord_bool:
                scores["detection"] = 0.95
                feedback_parts.append(f"✓ Correct threat detection: coordinated={true_coord_bool}")
            else:
                scores["detection"] = 0.15
                missed = "missed threat (false negative)" if true_coord_bool else "false alarm (false positive)"
                feedback_parts.append(f"✗ Wrong detection: {missed}")
        else:
            scores["detection"] = 0.30
            feedback_parts.append("~ Threat detection unclear. State explicitly: is_coordinated=true/false")

        # ── Threat level severity ──
        pred_level = str(prediction.get("threat_level", "")).lower().strip()
        true_level = str(ground_truth.get("threat_level", "medium")).lower().strip()

        pred_sev = self.THREAT_LEVELS.get(pred_level, -1)
        true_sev = self.THREAT_LEVELS.get(true_level, 2)

        if pred_sev == -1:
            scores["severity"] = 0.10
            feedback_parts.append(f"✗ Invalid threat_level: '{pred_level}'. Use: none, low, medium, high, critical")
        else:
            diff = abs(pred_sev - true_sev)
            if diff == 0:
                scores["severity"] = 0.95
                feedback_parts.append(f"✓ Exact threat level: {true_level}")
            elif diff == 1:
                scores["severity"] = 0.60
                feedback_parts.append(f"~ Close threat level: '{pred_level}' vs expected '{true_level}'")
            else:
                scores["severity"] = 0.20
                feedback_parts.append(f"✗ Threat level off by {diff}: '{pred_level}' vs '{true_level}'")

        # ── Response plan quality ──
        reasoning = str(prediction.get("reasoning", "")).lower()
        action = str(prediction.get("action", "")).lower()
        response_score = self._score_response_plan(reasoning + " " + action, difficulty)
        scores["response"] = response_score

        if response_score >= 0.7:
            feedback_parts.append("✓ Comprehensive response plan")
        elif response_score >= 0.4:
            feedback_parts.append("~ Response plan needs more detail. Consider: investigate, contain, escalate, prevent.")
        else:
            feedback_parts.append("✗ Weak response. Outline: 1) investigation steps, 2) containment, 3) escalation, 4) prevention.")

        # ── Confidence calibration ──
        try:
            confidence = float(prediction.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))

            # Good calibration: high confidence on correct detection, low on uncertain
            if scores["detection"] >= 0.8:
                # Correct detection → reward high confidence
                scores["confidence"] = 0.30 + confidence * 0.65
            else:
                # Wrong detection → reward low confidence (at least agent is uncertain)
                scores["confidence"] = 0.30 + (1.0 - confidence) * 0.65
        except (ValueError, TypeError):
            scores["confidence"] = 0.30

        # ── Category (basic) ──
        pred_cat = str(prediction.get("category", "")).lower().strip()
        true_cat = str(ground_truth.get("category", "")).lower().strip()
        scores["category"] = 0.90 if pred_cat == true_cat else (0.30 if pred_cat else 0.10)

        # ── Weights ──
        if difficulty == "easy":
            weights = {"detection": 0.35, "severity": 0.25, "response": 0.15, "confidence": 0.10, "category": 0.15}
        elif difficulty == "medium":
            weights = {"detection": 0.30, "severity": 0.20, "response": 0.25, "confidence": 0.10, "category": 0.15}
        else:
            weights = {"detection": 0.25, "severity": 0.15, "response": 0.30, "confidence": 0.15, "category": 0.15}

        total = sum(scores.get(k, 0.3) * w for k, w in weights.items())
        total = safe_clamp(total)

        feedback = " | ".join(feedback_parts)
        done = step_num >= 5
        return total, feedback, done

    def _score_response_plan(self, text: str, difficulty: str) -> float:
        """Score the quality of the response plan."""
        if not text or len(text) < 10:
            return 0.05

        total_hits = 0
        categories_covered = 0

        for category, keywords in self.RESPONSE_KEYWORDS.items():
            cat_hits = sum(1 for kw in keywords if kw in text)
            if cat_hits > 0:
                categories_covered += 1
                total_hits += min(cat_hits, 2)

        # Scale based on categories covered and keyword density
        base = 0.10 + categories_covered * 0.15 + total_hits * 0.05

        # Length bonus for detailed plans
        if len(text) > 100:
            base += 0.10
        if len(text) > 200:
            base += 0.05

        return min(0.95, base)


# ═══════════════════════════════════════════════════════════════════════════
# UNIFIED GRADER — Routes to domain-specific graders
# ═══════════════════════════════════════════════════════════════════════════

class ModeratorGrader:
    """
    Central grader that routes to domain-specific graders.
    Provides multi-turn feedback for agent improvement.
    """

    def __init__(self):
        self.text_grader = TextClassificationGrader()
        self.context_grader = ContextualPolicyGrader()
        self.threat_grader = ThreatAssessmentGrader()
        self._cache = {}

    def grade(self, task_id: int, prediction: Dict[str, Any],
              ground_truth: Dict[str, Any], step_num: int = 1,
              use_cache: bool = False) -> float:
        """
        Grade a prediction. Returns score strictly in (0, 1).

        For backward compatibility, returns just the score.
        Use grade_with_feedback() for full feedback.
        """
        score, _, _ = self.grade_with_feedback(task_id, prediction, ground_truth, step_num)
        return score

    def grade_with_feedback(self, task_id: int, prediction: Dict[str, Any],
                            ground_truth: Dict[str, Any],
                            step_num: int = 1) -> tuple:
        """
        Grade and return (score, feedback, done).

        Routes to the appropriate domain grader based on task_id.
        """
        try:
            domain = TASK_DOMAINS.get(task_id, "text_classification")

            if domain == "text_classification":
                score, feedback, done = self.text_grader.grade(
                    task_id, prediction, ground_truth, step_num)
            elif domain == "contextual_policy":
                score, feedback, done = self.context_grader.grade(
                    task_id, prediction, ground_truth, step_num)
            elif domain == "threat_assessment":
                score, feedback, done = self.threat_grader.grade(
                    task_id, prediction, ground_truth, step_num)
            else:
                score, feedback, done = SCORE_DEFAULT, "Unknown domain", True

            score = safe_clamp(score)
            return score, feedback, done

        except Exception as e:
            return safe_clamp(SCORE_DEFAULT), f"Grading error: {str(e)[:50]}", True

    def get_domain(self, task_id: int) -> str:
        """Get the domain for a task."""
        return TASK_DOMAINS.get(task_id, "text_classification")

    def get_difficulty(self, task_id: int) -> str:
        """Get the difficulty for a task."""
        return TASK_DIFFICULTIES.get(task_id, "easy")
