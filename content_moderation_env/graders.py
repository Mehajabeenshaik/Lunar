"""
Optimized Task Graders for Content Moderation Environment
Improved reward calculation with better accuracy, partial credit, and caching

CRITICAL: All scores MUST be strictly within (0, 1) — never exactly 0.0 or 1.0.
The validator rejects any score that is <= 0 or >= 1.
"""

from typing import Dict, Any, Optional
from .tasks import ContentCategory, ModerationAction
import hashlib
import json


# Module-level constants for boundary-safe scores
SCORE_HIGH = 0.95      # Use instead of 0.99 or 0.999
SCORE_MEDIUM = 0.7     # Partial credit
SCORE_LOW = 0.3        # Poor but not zero
SCORE_FAIL = 0.05      # Use instead of 0.01 or 0.001
SCORE_DEFAULT = 0.5    # Safe fallback


def safe_clamp(score: float) -> float:
    """GLOBAL score clamp — ensures score is strictly within (0, 1).
    
    This is the SINGLE source of truth for score boundary enforcement.
    Every score MUST pass through this function before being returned.
    """
    try:
        score = float(score)
    except (ValueError, TypeError):
        return SCORE_DEFAULT
    
    # Handle NaN and Inf
    if score != score or score == float('inf') or score == float('-inf'):
        return SCORE_DEFAULT
    
    # Hard clamp: force into (0.01, 0.99)
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    
    # Tighten to safe range
    if score < 0.01:
        return 0.01
    if score > 0.99:
        return 0.99
    
    # Round to 4 decimal places
    score = round(score, 4)
    
    # Post-rounding safety check
    if score <= 0.0 or score >= 1.0:
        return SCORE_DEFAULT
    
    return score


class OptimizedModeratorGrader:
    """Central grading logic with boundary-safe scoring"""
    
    def __init__(self):
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    @staticmethod
    def _clamp_score(score: float) -> float:
        """Delegate to module-level safe_clamp."""
        return safe_clamp(score)
    
    def _get_cache_key(self, task_id: int, prediction: Dict, ground_truth: Dict) -> str:
        """Generate cache key for grading results"""
        key = f"{task_id}_{json.dumps(prediction, sort_keys=True, default=str)}_{json.dumps(ground_truth, sort_keys=True, default=str)}"
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def grade(self, task_id: int, prediction: Dict[str, Any], ground_truth: Dict[str, Any], use_cache: bool = True) -> float:
        """Route to task-specific grader with caching and boundary enforcement.
        
        Returns: float strictly in (0, 1)
        """
        if use_cache:
            cache_key = self._get_cache_key(task_id, prediction, ground_truth)
            if cache_key in self.cache:
                self.cache_hits += 1
                return self.cache[cache_key]
        
        self.cache_misses += 1
        
        graders = {
            1: self.grade_task_1,
            2: self.grade_task_2,
            3: self.grade_task_3,
            4: self.grade_task_4,
            5: self.grade_task_5,
            6: self.grade_task_6,
            7: self.grade_task_7,
            8: self.grade_task_8,
            9: self.grade_task_9,
            10: self.grade_task_10,
            11: self.grade_task_11,
            12: self.grade_task_12,
            13: self.grade_task_13,
            14: self.grade_task_14,
            15: self.grade_task_15,
            16: self.grade_task_16,
            17: self.grade_task_17,
            18: self.grade_task_18,
            19: self.grade_task_19,
            20: self.grade_task_20,
            21: self.grade_task_21,
            22: self.grade_task_22,
            23: self.grade_task_23,
            24: self.grade_task_24,
            25: self.grade_task_25,
            26: self.grade_task_26,
            27: self.grade_task_27,
            28: self.grade_task_28,
            29: self.grade_task_29,
            30: self.grade_task_30,
        }
        
        # Wrap ALL grading in try/except to guarantee safe output
        try:
            grader_fn = graders.get(task_id)
            if grader_fn is None:
                score = SCORE_DEFAULT
            else:
                score = grader_fn(prediction, ground_truth)
        except Exception:
            score = SCORE_DEFAULT
        
        # CRITICAL: Clamp score to valid range (0, 1)
        score = safe_clamp(score)
        
        if use_cache:
            self.cache[cache_key] = score
        
        return score
    
    # ============ DOMAIN 1: BASIC CLASSIFICATION ============
    
    @staticmethod
    def grade_task_1(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 1: Post Classification (Easy) - Exact match scoring"""
        try:
            pred = str(prediction.get("category", "")).lower().strip()
            true = str(ground_truth.get("category", "")).lower().strip()
            return SCORE_HIGH if pred == true else SCORE_FAIL
        except Exception:
            return SCORE_FAIL
    
    @staticmethod
    def grade_task_2(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 2: Classification with Severity (Medium) - Weighted composite"""
        scores = {}
        
        # Category accuracy (50%)
        try:
            pred_cat = str(prediction.get("category", "")).lower().strip()
            true_cat = str(ground_truth.get("category", "")).lower().strip()
            scores['category'] = SCORE_HIGH if pred_cat == true_cat else SCORE_FAIL
        except Exception:
            scores['category'] = SCORE_FAIL
        
        # Severity accuracy (50%)
        try:
            pred_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            sev_diff = abs(pred_sev - true_sev)
            
            if sev_diff == 0:
                scores['severity'] = SCORE_HIGH
            elif sev_diff == 1:
                scores['severity'] = SCORE_MEDIUM
            elif sev_diff == 2:
                scores['severity'] = 0.4
            else:
                scores['severity'] = SCORE_FAIL
        except Exception:
            scores['severity'] = SCORE_FAIL
        
        return safe_clamp((scores['category'] * 0.50) + (scores['severity'] * 0.50))
    
    @staticmethod
    def grade_task_3(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 3: Full Moderation Decision (Hard) - Multi-criteria scoring"""
        scores = {}
        
        # Category accuracy (25%)
        try:
            pred_cat = str(prediction.get("category", "")).lower().strip()
            true_cat = str(ground_truth.get("category", "")).lower().strip()
            scores['category'] = SCORE_HIGH if pred_cat == true_cat else SCORE_FAIL
        except Exception:
            scores['category'] = SCORE_FAIL
        
        # Severity accuracy (25%)
        try:
            pred_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            sev_diff = abs(pred_sev - true_sev)
            
            if sev_diff == 0:
                scores['severity'] = SCORE_HIGH
            elif sev_diff == 1:
                scores['severity'] = SCORE_MEDIUM
            elif sev_diff == 2:
                scores['severity'] = 0.4
            else:
                scores['severity'] = SCORE_FAIL
        except Exception:
            scores['severity'] = SCORE_FAIL
        
        # Action accuracy (25%)
        try:
            pred_act = str(prediction.get("action", "")).lower().strip()
            true_act = str(ground_truth.get("action", "")).lower().strip()
            scores['action'] = SCORE_HIGH if pred_act == true_act else SCORE_FAIL
        except Exception:
            scores['action'] = SCORE_FAIL
        
        # Reasoning quality (25%)
        try:
            reasoning = str(prediction.get("reasoning", "")).strip()
            reasoning_len = len(reasoning)
            
            if reasoning_len < 20:
                scores['reasoning'] = SCORE_LOW
            elif reasoning_len < 50:
                scores['reasoning'] = 0.6
            elif reasoning_len < 100:
                scores['reasoning'] = 0.85
            else:
                scores['reasoning'] = SCORE_HIGH
            
            # Bonus for mentioning key factors
            reasoning_lower = reasoning.lower()
            if any(word in reasoning_lower for word in ["severity", "policy", "context", "prior", "history"]):
                scores['reasoning'] = min(0.98, scores['reasoning'] + 0.1)
        except Exception:
            scores['reasoning'] = SCORE_FAIL
        
        return safe_clamp(sum(scores.values()) / 4.0)
    
    # ============ DOMAIN 2: CONTEXT-AWARE MODERATION ============
    
    @staticmethod
    def grade_task_4(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 4: Author History Context (Easy) - History-aware scoring"""
        scores = {}
        
        # Severity accuracy with author context (60%)
        try:
            pred_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            sev_diff = abs(pred_sev - true_sev)
            
            if sev_diff == 0:
                scores['severity'] = SCORE_HIGH
            elif sev_diff == 1:
                scores['severity'] = SCORE_MEDIUM
            else:
                scores['severity'] = SCORE_FAIL
        except Exception:
            scores['severity'] = SCORE_FAIL
        
        # Reasoning should mention history/context (40%)
        try:
            reasoning = str(prediction.get("reasoning", "")).lower()
            history_keywords = ["history", "prior", "violations", "previous", "record", "repeat", "offender"]
            history_mentioned = sum(1 for kw in history_keywords if kw in reasoning)
            
            if history_mentioned >= 2:
                scores['reasoning'] = SCORE_HIGH
            elif history_mentioned == 1:
                scores['reasoning'] = SCORE_MEDIUM
            else:
                scores['reasoning'] = SCORE_LOW
        except Exception:
            scores['reasoning'] = SCORE_FAIL
        
        return safe_clamp((scores['severity'] * 0.60) + (scores['reasoning'] * 0.40))
    
    @staticmethod
    def grade_task_5(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 5: Trending Topic Context (Medium) - Context-exception handling"""
        scores = {}
        
        # Category accuracy (30%)
        try:
            pred_cat = str(prediction.get("category", "")).lower().strip()
            true_cat = str(ground_truth.get("category", "")).lower().strip()
            scores['category'] = SCORE_HIGH if pred_cat == true_cat else SCORE_DEFAULT
        except Exception:
            scores['category'] = SCORE_FAIL
        
        # Policy exception detection (40%)
        try:
            pred_exc = str(prediction.get("policy_exception", "")).lower().strip()
            true_exc = str(ground_truth.get("policy_exception", "")).lower().strip()
            pred_exc_bool = pred_exc in ["true", "1", "yes", "enabled"]
            true_exc_bool = true_exc in ["true", "1", "yes", "enabled"] or ground_truth.get("policy_exception") is True
            
            scores['exception'] = SCORE_HIGH if pred_exc_bool == true_exc_bool else SCORE_LOW
        except Exception:
            scores['exception'] = SCORE_FAIL
        
        # Action correctness (30%)
        try:
            pred_act = str(prediction.get("action", "")).lower().strip()
            true_act = str(ground_truth.get("action", "")).lower().strip()
            expected_act = "label" if ground_truth.get("policy_exception") else true_act
            scores['action'] = SCORE_HIGH if pred_act == expected_act else SCORE_FAIL
        except Exception:
            scores['action'] = SCORE_FAIL
        
        return safe_clamp((scores['category'] * 0.30) + (scores['exception'] * 0.40) + (scores['action'] * 0.30))
    
    @staticmethod
    def grade_task_6(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 6: Appeal Case Review (Hard) - Appeal resolution accuracy"""
        scores = {}
        
        # Appeal verdict accuracy (60%)
        try:
            pred_verdict = str(prediction.get("verdict", "")).lower().strip()
            true_verdict = str(ground_truth.get("verdict", "")).lower().strip()
            scores['verdict'] = SCORE_HIGH if pred_verdict == true_verdict else SCORE_FAIL
        except Exception:
            scores['verdict'] = SCORE_FAIL
        
        # Reasoning quality (40%)
        try:
            reasoning = str(prediction.get("reasoning", "")).strip()
            reasoning_len = len(reasoning)
            
            if reasoning_len < 30:
                scores['reasoning'] = SCORE_LOW
            elif reasoning_len < 80:
                scores['reasoning'] = 0.6
            else:
                scores['reasoning'] = SCORE_HIGH
            
            if any(word in reasoning.lower() for word in ["original", "context", "policy", "evidence"]):
                scores['reasoning'] = min(0.98, scores['reasoning'] + 0.1)
        except Exception:
            scores['reasoning'] = SCORE_FAIL
        
        return safe_clamp((scores['verdict'] * 0.60) + (scores['reasoning'] * 0.40))
    
    # ============ DOMAIN 3: EDGE CASES ============
    
    @staticmethod
    def grade_task_7(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 7: False Positive Detection (Easy)"""
        scores = {}
        
        # False positive detection (70%)
        try:
            pred_fp = str(prediction.get("is_false_positive", "")).lower().strip()
            true_fp = str(ground_truth.get("is_false_positive", "")).lower().strip()
            pred_fp_bool = pred_fp in ["true", "1", "yes"]
            true_fp_bool = true_fp in ["true", "1", "yes"] or ground_truth.get("is_false_positive") is True
            
            scores['detection'] = SCORE_HIGH if pred_fp_bool == true_fp_bool else SCORE_FAIL
        except Exception:
            scores['detection'] = SCORE_FAIL
        
        # Category accuracy (30%)
        try:
            pred_cat = str(prediction.get("category", "")).lower().strip()
            true_cat = str(ground_truth.get("category", "")).lower().strip()
            scores['category'] = SCORE_HIGH if pred_cat == true_cat else SCORE_DEFAULT
        except Exception:
            scores['category'] = SCORE_FAIL
        
        return safe_clamp((scores['detection'] * 0.70) + (scores['category'] * 0.30))
    
    @staticmethod
    def grade_task_8(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 8: Sarcasm & Irony Detection (Medium)"""
        scores = {}
        
        # Tone classification (50%)
        try:
            pred_tone = str(prediction.get("tone", "")).lower().strip()
            true_tone = str(ground_truth.get("tone", "")).lower().strip()
            scores['tone'] = SCORE_HIGH if pred_tone == true_tone else SCORE_DEFAULT
        except Exception:
            scores['tone'] = SCORE_FAIL
        
        # Severity accuracy (50%)
        try:
            pred_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            sev_diff = abs(pred_sev - true_sev)
            
            if sev_diff == 0:
                scores['severity'] = SCORE_HIGH
            elif sev_diff == 1:
                scores['severity'] = SCORE_MEDIUM
            else:
                scores['severity'] = SCORE_FAIL
        except Exception:
            scores['severity'] = SCORE_FAIL
        
        return safe_clamp((scores['tone'] * 0.50) + (scores['severity'] * 0.50))
    
    @staticmethod
    def grade_task_9(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 9: Coordinated Inauthentic Behavior (Hard)"""
        scores = {}
        
        # Behavior detection (70%)
        try:
            pred_coord = str(prediction.get("is_coordinated", "")).lower().strip()
            true_coord = str(ground_truth.get("is_coordinated", "")).lower().strip()
            pred_coord_bool = pred_coord in ["true", "1", "yes"]
            true_coord_bool = true_coord in ["true", "1", "yes"] or ground_truth.get("is_coordinated") is True
            
            scores['detection'] = SCORE_HIGH if pred_coord_bool == true_coord_bool else SCORE_FAIL
        except Exception:
            scores['detection'] = SCORE_FAIL
        
        # Confidence level (30%)
        try:
            confidence = float(prediction.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
            
            if scores.get('detection', SCORE_FAIL) == SCORE_HIGH:
                # Correct detection: higher confidence = higher score
                scores['confidence'] = safe_clamp(0.05 + (confidence * 0.9))
            else:
                # Wrong detection: penalize high confidence
                scores['confidence'] = safe_clamp(0.95 - (confidence * 0.9))
        except Exception:
            scores['confidence'] = SCORE_DEFAULT
        
        return safe_clamp((scores['detection'] * 0.70) + (scores['confidence'] * 0.30))

    # ============ DOMAIN 4: IMAGE & MULTIMODAL (Tasks 10-14) ============

    @staticmethod
    def grade_task_10(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 10: Image Safety - Binary safe/explicit"""
        try:
            pred = str(prediction.get("safety", "")).lower().strip()
            true = str(ground_truth.get("safety", "")).lower().strip()
            return SCORE_HIGH if pred == true else SCORE_FAIL
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_11(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 11: Visual Toxicity - Graduated severity"""
        try:
            pred_tox = str(prediction.get("toxicity", "")).lower().strip()
            true_tox = str(ground_truth.get("toxicity", "")).lower().strip()
            return SCORE_HIGH if pred_tox == true_tox else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_12(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 12: Multimodal - Consider both image and text"""
        try:
            image_match = str(prediction.get("image_assessment", "")).lower().strip() == str(ground_truth.get("image_assessment", "")).lower().strip()
            text_match = str(prediction.get("text_assessment", "")).lower().strip() == str(ground_truth.get("text_assessment", "")).lower().strip()
            
            image_score = SCORE_HIGH if image_match else 0.15
            text_score = SCORE_HIGH if text_match else 0.15
            return safe_clamp((image_score + text_score) / 2.0)
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_13(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 13: Deepfake Detection - Authenticity judgment"""
        try:
            pred_auth = str(prediction.get("authenticity", "")).lower().strip()
            true_auth = str(ground_truth.get("authenticity", "")).lower().strip()
            return SCORE_HIGH if pred_auth == true_auth else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_14(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 14: Scene Safety - Context appropriateness"""
        try:
            contexts = ["workplace", "home", "public"]
            matches = sum(
                1 for ctx in contexts
                if str(prediction.get(ctx, "")).lower().strip() == str(ground_truth.get(ctx, "")).lower().strip()
                and prediction.get(ctx) is not None and ground_truth.get(ctx) is not None
            )
            # Map 0-3 matches to safe score range
            score = 0.1 + (matches / len(contexts)) * 0.85
            return safe_clamp(score)
        except Exception:
            return SCORE_FAIL

    # ============ DOMAIN 5: USER CONTEXT (Tasks 15-20) ============

    @staticmethod
    def grade_task_15(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 15: Author Credibility - Account legitimacy"""
        try:
            pred_cred = str(prediction.get("credibility", "")).lower().strip()
            true_cred = str(ground_truth.get("credibility", "")).lower().strip()
            return SCORE_HIGH if pred_cred == true_cred else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_16(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 16: Bot Detection - Classify as human/bot"""
        try:
            pred_bot = str(prediction.get("is_bot", "")).lower().strip()
            true_bot = str(ground_truth.get("is_bot", "")).lower().strip()
            pred_bot_bool = pred_bot in ["true", "1", "yes"]
            true_bot_bool = true_bot in ["true", "1", "yes"] or ground_truth.get("is_bot") is True
            return SCORE_HIGH if pred_bot_bool == true_bot_bool else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_17(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 17: Inauthentic Behavior Patterns - Network coordination"""
        try:
            pred_coord = str(prediction.get("coordination", "")).lower().strip()
            true_coord = str(ground_truth.get("coordination", "")).lower().strip()
            return SCORE_HIGH if pred_coord == true_coord else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_18(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 18: Misinformation Spread - Verify claim accuracy"""
        try:
            pred_vera = str(prediction.get("veracity", "")).lower().strip()
            true_vera = str(ground_truth.get("veracity", "")).lower().strip()
            return SCORE_HIGH if pred_vera == true_vera else SCORE_LOW
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_19(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 19: User Appeal Fairness - Judge appeal validity"""
        try:
            pred_appeal = str(prediction.get("appeal_validity", "")).lower().strip()
            true_appeal = str(ground_truth.get("appeal_validity", "")).lower().strip()
            return SCORE_HIGH if pred_appeal == true_appeal else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_20(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 20: User Trust Score - Build user reputation"""
        try:
            pred_trust = float(prediction.get("trust_score", 5)) / 10.0
            true_trust = float(ground_truth.get("trust_score", 5)) / 10.0
            diff = abs(pred_trust - true_trust)
            # Map diff [0, 1] to score [0.95, 0.1]
            score = 0.1 + (1.0 - min(diff, 1.0)) * 0.85
            return safe_clamp(score)
        except Exception:
            return SCORE_FAIL

    # ============ DOMAIN 6: CROSS-POST ANALYSIS (Tasks 21-25) ============

    @staticmethod
    def grade_task_21(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 21: Campaign Detection - Identify coordinated posts"""
        try:
            pred_camp = str(prediction.get("campaign_likelihood", "")).lower().strip()
            true_camp = str(ground_truth.get("campaign_likelihood", "")).lower().strip()
            return SCORE_HIGH if pred_camp == true_camp else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_22(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 22: Viral Misinformation - Track false claims"""
        try:
            pred_viral = str(prediction.get("spread_rate", "")).lower().strip()
            true_viral = str(ground_truth.get("spread_rate", "")).lower().strip()
            return SCORE_HIGH if pred_viral == true_viral else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_23(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 23: Harassment Network - Detect coordinated harassment"""
        try:
            pred_sever = str(prediction.get("severity", "")).lower().strip()
            true_sever = str(ground_truth.get("severity", "")).lower().strip()
            return SCORE_HIGH if pred_sever == true_sever else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_24(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 24: Context Collapse - Content appropriateness varies"""
        try:
            # Only compare keys that exist in ground_truth to avoid empty-dict issues
            gt_keys = list(ground_truth.keys())
            if not gt_keys:
                return SCORE_DEFAULT
            
            matches = sum(
                1 for ctx in gt_keys
                if str(prediction.get(ctx, "")).lower().strip() == str(ground_truth.get(ctx, "")).lower().strip()
            )
            score = 0.1 + (matches / len(gt_keys)) * 0.85
            return safe_clamp(score)
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_25(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 25: Cross-platform Consistency - Maintain consistency"""
        try:
            pred_cons = str(prediction.get("consistency", "")).lower().strip()
            true_cons = str(ground_truth.get("consistency", "")).lower().strip()
            return SCORE_HIGH if pred_cons == true_cons else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    # ============ DOMAIN 7: ADVANCED REASONING (Tasks 26-30) ============

    @staticmethod
    def grade_task_26(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 26: Satire vs Hate - Distinguish satire from genuine hate"""
        try:
            pred_sat = str(prediction.get("classification", "")).lower().strip()
            true_sat = str(ground_truth.get("classification", "")).lower().strip()
            return SCORE_HIGH if pred_sat == true_sat else SCORE_LOW
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_27(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 27: Cultural Sensitivity - Context-specific appropriateness"""
        try:
            pred_cult = str(prediction.get("appropriateness", "")).lower().strip()
            true_cult = str(ground_truth.get("appropriateness", "")).lower().strip()
            return SCORE_HIGH if pred_cult == true_cult else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_28(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 28: Policy Evolution - Apply updated policies"""
        try:
            pred_policy = str(prediction.get("action", "")).lower().strip()
            true_policy = str(ground_truth.get("action", "")).lower().strip()
            return SCORE_HIGH if pred_policy == true_policy else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_29(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 29: Multi-language - Consistent across languages"""
        try:
            pred_lang = str(prediction.get("category", "")).lower().strip()
            true_lang = str(ground_truth.get("category", "")).lower().strip()
            return SCORE_HIGH if pred_lang == true_lang else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL

    @staticmethod
    def grade_task_30(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 30: Accessibility - Accessibility-aware moderation"""
        try:
            pred_access = str(prediction.get("assessment", "")).lower().strip()
            true_access = str(ground_truth.get("assessment", "")).lower().strip()
            return SCORE_HIGH if pred_access == true_access else SCORE_DEFAULT
        except Exception:
            return SCORE_FAIL


# ============ BACKWARD COMPATIBILITY ============

# Keep old name for compatibility
ModeratorGrader = OptimizedModeratorGrader
