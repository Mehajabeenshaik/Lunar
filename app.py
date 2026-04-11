"""
Lunar Content Moderation Benchmark — FastAPI Server
Multi-turn RL environment for training content moderation agents.

OpenEnv v1 compliant:  POST /reset  |  POST /step  |  GET /state
"""

import os
import sys
import traceback
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent))

from content_moderation_env import ContentModerationEnv
from content_moderation_env.graders import safe_clamp, TASK_DOMAINS, TASK_DIFFICULTIES
from models import (
    ResetRequest, ResetResponse, StepRequest, StepResponse,
    StateResponse, Observation, Action, RewardInfo,
)

# ─── FastAPI App ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Lunar Content Moderation Benchmark",
    description="Multi-turn RL environment for content moderation. 30 tasks across 3 domains.",
    version="3.0.0",
)

# ─── Session Management ─────────────────────────────────────────────────

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ContentModerationEnv] = {}

    def create(self, task_id: int = 1, seed: Optional[int] = None) -> str:
        env = ContentModerationEnv(task_id=task_id, seed=seed)
        self.sessions[env.current_session_id] = env
        return env.current_session_id

    def get(self, session_id: str) -> Optional[ContentModerationEnv]:
        return self.sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        return self.sessions.pop(session_id, None) is not None

sessions = SessionManager()


# ═══════════════════════════════════════════════════════════════════════════
# OPENENV STANDARD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Welcome and health check."""
    return {
        "name": "Lunar Content Moderation Benchmark",
        "version": "3.0.0",
        "status": "running",
        "spec": "OpenEnv v1",
        "tasks": 30,
        "domains": {
            "text_classification": "Tasks 1-10: Classify posts by category, severity, and reasoning",
            "contextual_policy": "Tasks 11-20: Enforce policies with author history, cultural context, and exceptions",
            "threat_assessment": "Tasks 21-30: Detect coordinated threats, misinformation cascades, harassment networks",
        },
        "reward_range": "(0, 1) exclusive",
        "multi_turn": True,
        "max_steps_per_episode": 5,
    }


@app.get("/health")
async def health():
    """Health check endpoint for validator."""
    try:
        from content_moderation_env.graders import ModeratorGrader
        grader = ModeratorGrader()

        # Verify all 30 tasks produce valid scores
        test_pred = {"category": "safe", "severity": 1, "action": "keep", "reasoning": "test"}
        test_gt = {"category": "safe", "severity": 1, "action": "keep"}

        for tid in [1, 10, 15, 20, 25, 30]:
            score = grader.grade(tid, test_pred, test_gt)
            if score <= 0.0 or score >= 1.0:
                return {"status": "error", "task": tid, "score": score}

        return {
            "status": "ok",
            "version": "3.0.0",
            "active_sessions": len(sessions.sessions),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:100]}


@app.get("/manifest")
async def get_manifest():
    """Return OpenEnv manifest."""
    return {
        "name": "lunar-content-moderation-benchmark",
        "version": "3.0.0",
        "spec_version": 1,
        "description": "Multi-turn RL benchmark for content moderation. 3 domains, 30 tasks, progressive context reveal.",
        "type": "rl-environment",
        "tasks": 30,
        "reward_range": [0.01, 0.99],
        "multi_turn": True,
        "max_steps": 5,
        "domains": ["text_classification", "contextual_policy", "threat_assessment"],
        "tagline": "Train agents to moderate content like Meta engineers — with context, nuance, and accountability.",
    }


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()):
    """OpenEnv standard: Reset environment and start new episode."""
    try:
        session_id = sessions.create(task_id=request.task_id, seed=request.seed)
        env = sessions.get(session_id)
        observation = env.reset()

        return ResetResponse(
            session_id=session_id,
            task_id=request.task_id,
            observation=Observation(**observation),
        ).model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/session/start")
async def start_session(request: ResetRequest):
    """Start a new moderation session (alias for /reset)."""
    return await reset(request)


@app.post("/step")
async def step_global(request: StepRequest):
    """OpenEnv standard: Execute step using session_id from request body."""
    return await _do_step(request.session_id, request.action)


@app.post("/session/{session_id}/step")
async def step_session(session_id: str, request: StepRequest):
    """Execute one step in the environment."""
    return await _do_step(session_id, request.action)


async def _do_step(session_id: str, action: Dict) -> Dict:
    """Core step logic shared by both endpoints."""
    env = sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    try:
        observation, reward, done, info = env.step(action)
        reward = safe_clamp(reward)

        return StepResponse(
            observation=Observation(**observation),
            reward=reward,
            done=done,
            info=info,
            feedback=info.get("feedback", ""),
            step_scores=env.rewards_history,
        ).model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
async def get_state():
    """OpenEnv standard: Get environment state."""
    return {
        "name": "lunar-content-moderation-benchmark",
        "version": "3.0.0",
        "tasks_available": 30,
        "active_sessions": len(sessions.sessions),
        "domains": 3,
        "reward_range": [0.01, 0.99],
        "multi_turn": True,
        "max_steps": 5,
        "status": "ready",
    }


@app.get("/state/{session_id}")
async def get_session_state(session_id: str):
    """Get specific session state."""
    env = sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return StateResponse(
        session_id=session_id,
        task_id=env.task_id,
        domain=env.domain,
        difficulty=env.difficulty,
        step=env.steps,
        rewards=env.rewards_history,
        done=env.done,
        history=env.feedback_history,
    ).model_dump()


@app.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get episode summary for a session."""
    env = sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return {
        "session_id": session_id,
        "summary": env.get_episode_summary(),
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if sessions.delete(session_id):
        return {"status": "deleted", "session_id": session_id}
    raise HTTPException(status_code=404, detail=f"Session {session_id} not found")


@app.get("/tasks")
async def list_tasks():
    """List all 30 tasks with metadata."""
    from content_moderation_env.environment import TASK_METADATA
    tasks = []
    for tid in range(1, 31):
        meta = TASK_METADATA.get(tid, {})
        tasks.append({
            "id": tid,
            "name": meta.get("name", f"Task {tid}"),
            "description": meta.get("desc", ""),
            "domain": TASK_DOMAINS.get(tid, "unknown"),
            "difficulty": TASK_DIFFICULTIES.get(tid, "unknown"),
        })
    return {"total_tasks": 30, "tasks": tasks}


@app.get("/stats")
async def get_stats():
    """Get benchmark statistics."""
    return {
        "active_sessions": len(sessions.sessions),
        "tasks_available": 30,
        "domains": {
            "text_classification": {"tasks": 10, "range": "1-10"},
            "contextual_policy": {"tasks": 10, "range": "11-20"},
            "threat_assessment": {"tasks": 10, "range": "21-30"},
        },
        "reward_range": [0.01, 0.99],
        "multi_turn": True,
        "max_steps": 5,
    }


# ─── Entry Points ───────────────────────────────────────────────────────

def main():
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting Lunar Benchmark on {host}:{port}...")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
