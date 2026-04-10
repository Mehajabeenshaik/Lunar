"""
Task-Specific Graders for Content Moderation Environment
Handles reward calculation for all 9 tasks across 3 domains
"""

from typing import Dict, Any
from .tasks import ContentCategory, ModerationAction


class ModeratorGrader:
    """Central grading logic for all 9 tasks"""
    
    # Task 1-3: Current domain (Text Classification)
    
    @staticmethod
    def grade_task_1(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 1: Post Classification (Easy)
        
        Simple binary accuracy: correct category = 1.0, wrong = 0.0
        """
        try:
            predicted_cat = prediction.get("category", "").lower()
            true_cat = ground_truth.get("category", "").lower()
            return 1.0 if predicted_cat == true_cat else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def grade_task_2(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 2: Classification with Severity (Medium)
        
        Composite: 50% category accuracy + 50% severity accuracy
        Severity allows ±1 range for partial credit
        """
        scores = {}
        
        # Category accuracy (50%)
        try:
            predicted_cat = prediction.get("category", "").lower()
            true_cat = ground_truth.get("category", "").lower()
            scores['category'] = 1.0 if predicted_cat == true_cat else 0.0
        except Exception:
            scores['category'] = 0.0
        
        # Severity accuracy (50%) - partial credit for ±1
        try:
            predicted_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            severity_diff = abs(predicted_sev - true_sev)
            
            if severity_diff == 0:
                scores['severity'] = 1.0
            elif severity_diff == 1:
                scores['severity'] = 0.5
            else:
                scores['severity'] = 0.0
        except Exception:
            scores['severity'] = 0.0
        
        return (scores['category'] * 0.5) + (scores['severity'] * 0.5)
    
    @staticmethod
    def grade_task_3(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 3: Full Moderation Decision (Hard)
        
        Composite: 25% category + 25% severity + 25% action + 25% reasoning
        Most complex task: all 4 components matter equally
        """
        scores = {}
        
        # Category accuracy (25%)
        try:
            predicted_cat = prediction.get("category", "").lower()
            true_cat = ground_truth.get("category", "").lower()
            scores['category'] = 1.0 if predicted_cat == true_cat else 0.0
        except Exception:
            scores['category'] = 0.0
        
        # Severity accuracy (25%) - ±1 partial credit
        try:
            predicted_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            severity_diff = abs(predicted_sev - true_sev)
            
            if severity_diff == 0:
                scores['severity'] = 1.0
            elif severity_diff == 1:
                scores['severity'] = 0.5
            else:
                scores['severity'] = 0.0
        except Exception:
            scores['severity'] = 0.0
        
        # Action accuracy (25%)
        try:
            predicted_act = prediction.get("action", "").lower()
            true_act = ground_truth.get("action", "").lower()
            scores['action'] = 1.0 if predicted_act == true_act else 0.0
        except Exception:
            scores['action'] = 0.0
        
        # Reasoning quality (25%) - check if reasoning exists and is substantive
        try:
            reasoning = prediction.get("reasoning", "")
            # Bonus: longer reasoning (generally better quality)
            reasoning_length = len(str(reasoning).strip())
            scores['reasoning'] = min(1.0, reasoning_length / 100.0) if reasoning_length > 20 else 0.5
        except Exception:
            scores['reasoning'] = 0.0
        
        return sum(scores.values()) / 4.0
    
    # Task 4-6: Domain 2 (Context-Aware Moderation)
    
    @staticmethod
    def grade_task_4(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 4: Author History Context (Easy)
        
        Grade on:
        - Whether severity was adjusted for author history (60%)
        - Whether reasoning mentions history/prior violations (40%)
        """
        scores = {}
        
        # Primary: Severity should be higher due to prior violations
        try:
            predicted_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 3))
            severity_diff = abs(predicted_sev - true_sev)
            
            if severity_diff == 0:
                scores['severity'] = 1.0
            elif severity_diff == 1:
                scores['severity'] = 0.5
            else:
                scores['severity'] = 0.0
        except Exception:
            scores['severity'] = 0.0
        
        # Secondary: Reasoning should mention history
        try:
            reasoning = str(prediction.get("reasoning", "")).lower()
            history_mentioned = any(word in reasoning for word in 
                                   ["history", "prior", "violations", "previous", "record"])
            scores['reasoning'] = 1.0 if history_mentioned else 0.0
        except Exception:
            scores['reasoning'] = 0.0
        
        return (scores['severity'] * 0.6) + (scores['reasoning'] * 0.4)
    
    @staticmethod
    def grade_task_5(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 5: Trending Topic Context (Medium)
        
        Grade on:
        - Category accuracy (30%)
        - Correct policy exception detection (40%)
        - Appropriate action given exception (30%)
        """
        scores = {}
        
        # Category accuracy (30%)
        try:
            predicted_cat = prediction.get("category", "").lower()
            true_cat = ground_truth.get("category", "").lower()
            scores['category'] = 1.0 if predicted_cat == true_cat else 0.0
        except Exception:
            scores['category'] = 0.0
        
        # Policy exception detection (40%)
        try:
            predicted_exception = prediction.get("policy_exception", "").lower()
            true_exception = ground_truth.get("policy_exception", "").lower()
            scores['exception'] = 1.0 if predicted_exception == true_exception else 0.5 if predicted_exception else 0.0
        except Exception:
            scores['exception'] = 0.0
        
        # Action correctness given context (30%)
        try:
            predicted_act = prediction.get("action", "").lower()
            true_act = ground_truth.get("action", "").lower()
            
            # If exception exists, "label" is correct; otherwise "remove"
            if ground_truth.get("policy_exception"):
                correct_action = "label"
            else:
                correct_action = true_act
            
            scores['action'] = 1.0 if predicted_act == correct_action else 0.0
        except Exception:
            scores['action'] = 0.0
        
        return (scores['category'] * 0.3) + (scores['exception'] * 0.4) + (scores['action'] * 0.3)
    
    @staticmethod
    def grade_task_6(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 6: Appeal Case (Hard)
        
        Most complex task. Grade on:
        - Appeal verdict accuracy (50%)
        - New action appropriateness (30%)
        - Reasoning quality (20%)
        """
        scores = {}
        
        # Appeal verdict (50%)
        try:
            predicted_verdict = prediction.get("appeal_verdict", "").lower()
            true_verdict = ground_truth.get("appeal_verdict", "").lower()
            scores['verdict'] = 1.0 if predicted_verdict == true_verdict else 0.0
        except Exception:
            scores['verdict'] = 0.0
        
        # New action appropriateness (30%)
        try:
            predicted_act = prediction.get("new_action", "").lower()
            true_act = ground_truth.get("new_action", "").lower()
            scores['action'] = 1.0 if predicted_act == true_act else 0.5  # Partial credit for reasonable actions
        except Exception:
            scores['action'] = 0.0
        
        # Reasoning quality (20%)
        try:
            reasoning = str(prediction.get("reasoning", "")).lower()
            # Check if reasoning demonstrates understanding of appeal evidence
            good_reason = any(word in reasoning for word in 
                            ["context", "evidence", "similar", "precedent", "misclassification", "legitimate"])
            reasoning_length = len(reasoning.strip())
            scores['reasoning'] = 1.0 if (good_reason and reasoning_length > 30) else 0.5 if reasoning_length > 30 else 0.0
        except Exception:
            scores['reasoning'] = 0.0
        
        return (scores['verdict'] * 0.5) + (scores['action'] * 0.3) + (scores['reasoning'] * 0.2)
    
    # Task 7-9: Domain 3 (Edge Cases & Escalation)
    
    @staticmethod
    def grade_task_7(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 7: False Positive Detection (Easy)
        
        Simple but important: Correctly identify false positives
        Accuracy: correct call = 1.0, wrong call = 0.0
        """
        try:
            predicted = prediction.get("is_false_positive", False)
            true = ground_truth.get("is_false_positive", False)
            return 1.0 if predicted == true else 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def grade_task_8(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 8: Sarcasm & Irony (Medium)
        
        Grade on:
        - Tone detection (50%): sarcastic/constructive/neutral
        - Severity assigned appropriately for detected tone (30%)
        - Reasoning quality (20%)
        """
        scores = {}
        
        # Tone detection (50%)
        try:
            predicted_tone = prediction.get("tone", "").lower()
            true_tone = ground_truth.get("tone", "").lower()
            scores['tone'] = 1.0 if predicted_tone == true_tone else 0.0
        except Exception:
            scores['tone'] = 0.0
        
        # Severity appropriateness (30%)
        try:
            predicted_sev = int(prediction.get("severity", 0))
            true_sev = int(ground_truth.get("severity", 1))
            
            # For constructive criticism, low severity is correct
            if predicted_sev <= 2 and true_sev <= 2:
                scores['severity'] = 1.0
            else:
                severity_diff = abs(predicted_sev - true_sev)
                scores['severity'] = 1.0 if severity_diff == 0 else 0.5 if severity_diff == 1 else 0.0
        except Exception:
            scores['severity'] = 0.0
        
        # Reasoning about tone (20%)
        try:
            reasoning = str(prediction.get("reasoning", "")).lower()
            good_reasoning = any(word in reasoning for word in 
                               ["sarcasm", "irony", "tone", "context", "workplace"])
            scores['reasoning'] = 1.0 if good_reasoning else 0.5
        except Exception:
            scores['reasoning'] = 0.0
        
        return (scores['tone'] * 0.5) + (scores['severity'] * 0.3) + (scores['reasoning'] * 0.2)
    
    @staticmethod
    def grade_task_9(prediction: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Task 9: Coordinated Inauthentic Behavior (Hard)
        
        Most complex: Detect coordinated attacks across multiple accounts
        Grade on:
        - CIB detection accuracy (50%)
        - Individual action correctness (25%)
        - Network action appropriateness (25%)
        """
        scores = {}
        
        # CIB detection (50%)
        try:
            predicted_cib = prediction.get("coordinated_inauthentic", False)
            true_cib = ground_truth.get("coordinated_inauthentic", False)
            scores['cib'] = 1.0 if predicted_cib == true_cib else 0.0
        except Exception:
            scores['cib'] = 0.0
        
        # Individual action (25%)
        try:
            predicted_ind = prediction.get("individual_action", "").lower()
            true_ind = ground_truth.get("individual_action", "").lower()
            scores['individual'] = 1.0 if predicted_ind == true_ind else 0.5
        except Exception:
            scores['individual'] = 0.0
        
        # Network action (25%)
        try:
            predicted_net = prediction.get("network_action", "").lower()
            true_net = ground_truth.get("network_action", "").lower()
            
            # More flexible grading: escalation/investigation both reasonable
            if predicted_net in ["investigate_network", "escalate_to_team"]:
                scores['network'] = 1.0 if true_net in ["investigate_network", "escalate_to_team"] else 0.5
            else:
                scores['network'] = 1.0 if predicted_net == true_net else 0.0
        except Exception:
            scores['network'] = 0.0
        
        return (scores['cib'] * 0.5) + (scores['individual'] * 0.25) + (scores['network'] * 0.25)
    
    @staticmethod
    def get_grader_for_task(task_id: int):
        """Return the grader function for a specific task"""
        graders = {
            1: ModeratorGrader.grade_task_1,
            2: ModeratorGrader.grade_task_2,
            3: ModeratorGrader.grade_task_3,
            4: ModeratorGrader.grade_task_4,
            5: ModeratorGrader.grade_task_5,
            6: ModeratorGrader.grade_task_6,
            7: ModeratorGrader.grade_task_7,
            8: ModeratorGrader.grade_task_8,
            9: ModeratorGrader.grade_task_9,
        }
        return graders.get(task_id, ModeratorGrader.grade_task_1)
