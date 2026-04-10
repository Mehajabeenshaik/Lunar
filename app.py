"""
Content Moderation Benchmark - FastAPI Server
Meta's Real-World Problem: Moderating social media posts at billion-scale
"""

import os
import sys
import json
import traceback
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

print("[DEBUG] Starting Content Moderation app...")

try:
    from content_moderation_env import ContentModerationEnv
    print("[DEBUG] ContentModerationEnv imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import ContentModerationEnv: {e}")
    traceback.print_exc()
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Content Moderation Benchmark",
    description="Meta Content Moderation Agent Environment",
    version="1.0.0"
)

# Pydantic models for requests/responses
class StartSessionRequest(BaseModel):
    task_id: int = 1
    seed: Optional[int] = None


class StepRequest(BaseModel):
    session_id: str
    action: Dict


class SessionState:
    """In-memory session management"""
    def __init__(self):
        self.sessions: Dict[str, ContentModerationEnv] = {}
    
    def create_session(self, task_id: int = 1, seed: Optional[int] = None) -> str:
        env = ContentModerationEnv(task_id=task_id, seed=seed)
        session_id = env.current_session_id
        self.sessions[session_id] = env
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ContentModerationEnv]:
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


sessions = SessionState()


# ============ API Endpoints ============

@app.get("/health")
async def health():
    """Health check endpoint for validator"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Health check and welcome endpoint"""
    return {
        "name": "Content Moderation Benchmark",
        "version": "1.0.0",
        "status": "running",
        "description": "Meta Content Moderation Agent Environment for RL training",
        "tasks": {
            1: "Task 1 (Easy): Post Classification",
            2: "Task 2 (Medium): Classification with Reasoning & Severity",
            3: "Task 3 (Hard): Full Moderation Decision"
        }
    }


@app.get("/manifest")
async def get_manifest():
    """Return OpenEnv manifest"""
    return {
        "name": "content-moderation-benchmark",
        "version": "2.0",
        "spec_version": 2,
        "description": "Meta Content Moderation Agent Environment - 30 Tasks Enhanced",
        "type": "rl-environment",
        "tasks": 30,
        "reward_range": [0.0, 1.0],
        "observation_space": {
            "type": "json",
            "description": "JSON object with post content and task instructions"
        },
        "domains": [
            "domain_1_basic_classification",
            "domain_2_context_aware_moderation",
            "domain_3_edge_cases",
            "domain_4_image_multimodal",
            "domain_5_user_context_behavior",
            "domain_6_cross_post_analysis",
            "domain_7_advanced_reasoning"
        ]
    }


@app.post("/session/start")
async def start_session(request: StartSessionRequest):
    """
    Start a new session
    
    Args:
        task_id: 1 (Easy), 2 (Medium), 3 (Hard)
        seed: Optional random seed
    
    Returns:
        session_id and initial observation
    """
    try:
        if request.task_id not in range(1, 31):
            raise ValueError("task_id must be 1-30")
        
        session_id = sessions.create_session(
            task_id=request.task_id,
            seed=request.seed
        )
        
        env = sessions.get_session(session_id)
        observation = env.reset()
        
        return {
            "session_id": session_id,
            "task_id": request.task_id,
            "observation": observation,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/session/{session_id}/step")
async def step_session(session_id: str, request: StepRequest):
    """
    Execute one step in the environment
    
    Args:
        session_id: Session identifier
        action: Agent's moderation decision
    
    Returns:
        observation, reward, done, info
    """
    try:
        env = sessions.get_session(session_id)
        if not env:
            raise ValueError(f"Session {session_id} not found")
        
        observation, reward, done, info = env.step(request.action)
        
        # CRITICAL: Enforce strict boundaries before returning JSON
        # Must be strictly between 0 and 1 (not 0.0 or 1.0)
        reward = float(reward)
        if reward is None or reward <= 0.0 or reward == 0.0:
            reward = 0.001
        if reward >= 1.0 or reward == 1.0:
            reward = 0.999
        if not (0 < reward < 1):
            reward = 0.5  # Fallback to safe middle value
        
        reward = float(reward)  # Ensure it's a float, not Decimal or other type        
        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get episode summary for a session"""
    try:
        env = sessions.get_session(session_id)
        if not env:
            raise ValueError(f"Session {session_id} not found")
        
        summary = env.get_episode_summary()
        return {
            "session_id": session_id,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        if sessions.delete_session(session_id):
            return {"status": "deleted", "session_id": session_id}
        else:
            raise ValueError(f"Session {session_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks")
async def list_tasks():
    """List all available 30 tasks"""
    return {
        "total_tasks": 30,
        "tasks": [
            # Domain 1: Basic Classification (1-3)
            {"id": 1, "domain": "domain_1_basic_classification", "name": "Post Classification (Easy)", "difficulty": "easy"},
            {"id": 2, "domain": "domain_1_basic_classification", "name": "Classification with Reasoning (Medium)", "difficulty": "medium"},
            {"id": 3, "domain": "domain_1_basic_classification", "name": "Full Moderation Decision (Hard)", "difficulty": "hard"},
            # Domain 2: Context-Aware (4-6)
            {"id": 4, "domain": "domain_2_context_aware_moderation", "name": "Author History Context (Easy)", "difficulty": "easy"},
            {"id": 5, "domain": "domain_2_context_aware_moderation", "name": "Trending Topic Context (Medium)", "difficulty": "medium"},
            {"id": 6, "domain": "domain_2_context_aware_moderation", "name": "Appeal Case Handling (Hard)", "difficulty": "hard"},
            # Domain 3: Edge Cases (7-9)
            {"id": 7, "domain": "domain_3_edge_cases", "name": "False Positive Detection (Easy)", "difficulty": "easy"},
            {"id": 8, "domain": "domain_3_edge_cases", "name": "Sarcasm & Irony Detection (Medium)", "difficulty": "medium"},
            {"id": 9, "domain": "domain_3_edge_cases", "name": "Coordinated Inauthentic Behavior (Hard)", "difficulty": "hard"},
            # Domain 4: Image & Multimodal (10-14)
            {"id": 10, "domain": "domain_4_image_multimodal", "name": "Image Safety Classification (Easy)", "difficulty": "easy"},
            {"id": 11, "domain": "domain_4_image_multimodal", "name": "Visual Toxicity Detection (Medium)", "difficulty": "medium"},
            {"id": 12, "domain": "domain_4_image_multimodal", "name": "Multimodal Context (Hard)", "difficulty": "hard"},
            {"id": 13, "domain": "domain_4_image_multimodal", "name": "Deepfake Detection (Medium)", "difficulty": "medium"},
            {"id": 14, "domain": "domain_4_image_multimodal", "name": "Scene Safety (Easy)", "difficulty": "easy"},
            # Domain 5: User Context (15-20)
            {"id": 15, "domain": "domain_5_user_context_behavior", "name": "Author Credibility (Medium)", "difficulty": "medium"},
            {"id": 16, "domain": "domain_5_user_context_behavior", "name": "Bot Detection (Medium)", "difficulty": "medium"},
            {"id": 17, "domain": "domain_5_user_context_behavior", "name": "Inauthentic Behavior Patterns (Hard)", "difficulty": "hard"},
            {"id": 18, "domain": "domain_5_user_context_behavior", "name": "Misinformation Spread Tracking (Hard)", "difficulty": "hard"},
            {"id": 19, "domain": "domain_5_user_context_behavior", "name": "User Appeal Fairness (Medium)", "difficulty": "medium"},
            {"id": 20, "domain": "domain_5_user_context_behavior", "name": "User Trust Score (Hard)", "difficulty": "hard"},
            # Domain 6: Cross-Post (21-25)
            {"id": 21, "domain": "domain_6_cross_post_analysis", "name": "Campaign Detection (Hard)", "difficulty": "hard"},
            {"id": 22, "domain": "domain_6_cross_post_analysis", "name": "Viral Misinformation (Hard)", "difficulty": "hard"},
            {"id": 23, "domain": "domain_6_cross_post_analysis", "name": "Harassment Network (Hard)", "difficulty": "hard"},
            {"id": 24, "domain": "domain_6_cross_post_analysis", "name": "Context Collapse (Medium)", "difficulty": "medium"},
            {"id": 25, "domain": "domain_6_cross_post_analysis", "name": "Cross-platform Consistency (Medium)", "difficulty": "medium"},
            # Domain 7: Advanced Reasoning (26-30)
            {"id": 26, "domain": "domain_7_advanced_reasoning", "name": "Satire vs Hate (Hard)", "difficulty": "hard"},
            {"id": 27, "domain": "domain_7_advanced_reasoning", "name": "Cultural Sensitivity (Hard)", "difficulty": "hard"},
            {"id": 28, "domain": "domain_7_advanced_reasoning", "name": "Policy Evolution (Medium)", "difficulty": "medium"},
            {"id": 29, "domain": "domain_7_advanced_reasoning", "name": "Multi-language Moderation (Hard)", "difficulty": "hard"},
            {"id": 30, "domain": "domain_7_advanced_reasoning", "name": "Accessibility Considerations (Medium)", "difficulty": "medium"},
        ]
    }


@app.get("/stats")
async def get_stats():
    """Get benchmark statistics"""
    return {
        "active_sessions": len(sessions.sessions),
        "environment": "ContentModerationEnv",
        "tasks_available": 30,
        "tasks_completed": len([s for s in sessions.sessions.values() if s.get("done")]),
        "reward_range": [0.0, 1.0],
        "domains": [
            "domain_1_basic_classification",
            "domain_2_context_aware_moderation",
            "domain_3_edge_cases",
            "domain_4_image_multimodal",
            "domain_5_user_context_behavior",
            "domain_6_cross_post_analysis",
            "domain_7_advanced_reasoning"
        ],
        "task_structure": {
            "domain_1_basic_classification": 3,
            "domain_2_context_aware_moderation": 3,
            "domain_3_edge_cases": 3,
            "domain_4_image_multimodal": 5,
            "domain_5_user_context_behavior": 6,
            "domain_6_cross_post_analysis": 5,
            "domain_7_advanced_reasoning": 5
        },
        "timestamp": datetime.now().isoformat()
    }


# ============ OPENENV STANDARD ENDPOINTS ============

@app.post("/reset")
async def reset():
    """
    OpenEnv standard: Reset environment
    Creates new session with default task (task_id=1)
    
    Returns:
        observation: Initial observation
        session_id: Session identifier for subsequent /step calls
    """
    try:
        session_id = sessions.create_session(task_id=1, seed=None)
        env = sessions.get_session(session_id)
        observation = env.reset()
        
        return {
            "observation": observation,
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
async def step():
    """
    OpenEnv standard: Execute step
    NOTE: This endpoint requires session context via headers or query params
    For proper OpenEnv compliance, use /session/{session_id}/step instead
    
    Returns:
        observation, reward, done, info
    """
    raise HTTPException(
        status_code=400,
        detail="/step endpoint requires session_id. Use /session/{session_id}/step instead"
    )


@app.get("/state")
async def get_state():
    """
    OpenEnv standard: Get environment state
    Returns metadata about current environment configuration
    
    Returns:
        Environment state and configuration
    """
    return {
        "name": "content-moderation-benchmark",
        "version": "2.0",
        "tasks_available": 9,
        "active_sessions": len(sessions.sessions),
        "reward_range": [0.0, 1.0],
        "environment": "ContentModerationEnv",
        "status": "ready",
        "domains": 3,
        "tasks_per_domain": 3
    }


def main():
    """Entry point for [project.scripts] server command"""
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"[DEBUG] Starting uvicorn on {host}:{port}...")
    print(f"[DEBUG] Open http://localhost:{port}/docs for API documentation")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"[DEBUG] Starting uvicorn on {host}:{port}...")
    print(f"[DEBUG] Open http://localhost:{port}/docs for API documentation")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        traceback.print_exc()
        sys.exit(1)
