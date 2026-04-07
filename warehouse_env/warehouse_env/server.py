"""FastAPI server for warehouse environment."""

import os
import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn

from .env import WarehouseEnv
from .models import Action, Observation
from .graders import get_grader
from .session_manager import SessionManager
from .task_config import get_task_variants, get_task_info, is_valid_task

app = FastAPI(
    title="LUNAR: Multi-Domain RL Environment",
    version="3.0.0",
    description="Multi-domain optimization with session management and leaderboard",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Session manager for multi-agent support with automatic cleanup
manager = SessionManager(max_sessions=100, session_timeout_hours=2)


class ResetRequest(BaseModel):
    task: Optional[str] = None


class ResetResponse(BaseModel):
    observation: dict
    task: str
    session_id: str = None


class StepRequest(BaseModel):
    action: dict


class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool
    info: dict


class StateResponse(BaseModel):
    state: dict
    task: str
    episode_rewards: list


@app.post("/reset", response_model=ResetResponse)
async def reset(req: Optional[ResetRequest] = None, session_id: str = Query(None)):
    """Reset environment to initial state (create new session if needed)."""
    
    # Determine task
    task = req.task if req and req.task else os.getenv("WAREHOUSE_TASK", "warehouse_easy")
    
    # Validate task
    if not is_valid_task(task):
        raise HTTPException(status_code=400, detail=f"Unknown task: {task}. Valid tasks: {list(get_task_variants().keys())}")
    
    # Create or reuse session
    if not session_id:
        session_id = manager.create_session(task)
    
    env = manager.get_session(session_id)
    obs = env.reset()
    
    return ResetResponse(
        observation=obs.model_dump(),
        task=task,
        session_id=session_id  # Return session ID for future requests
    )


@app.post("/step", response_model=StepResponse)
async def step(req: StepRequest, session_id: str = Query(...)):
    """Execute one environment step."""
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    try:
        env = manager.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        action = Action(**req.action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid action: {str(e)}")
    
    obs, reward = env.step(action)
    
    # Record reward for leaderboard
    manager.record_reward(session_id, reward.value)
    
    return StepResponse(
        observation=obs.model_dump(),
        reward=reward.value,
        done=reward.done,
        info=reward.info,
    )


@app.get("/state", response_model=StateResponse)
async def state(session_id: str = Query(...)):
    """Get current environment state."""
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    try:
        env = manager.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return StateResponse(
        state=env.state_dict(),
        task=env.task,
        episode_rewards=env.episode_rewards,
    )


@app.get("/render")
async def render(session_id: str = Query(None)):
    """Render environment visualization."""
    
    if not session_id:
        return {"render": "No session provided"}
    
    try:
        env = manager.get_session(session_id)
    except ValueError:
        return {"render": "Session not found"}
    
    return {"render": env.render()}


@app.get("/health")
async def health():
    """Health check endpoint with system stats."""
    stats = manager.get_stats()
    return {
        "status": "ok",
        "version": "3.0.0",
        "active_sessions": stats["total_sessions"],
        "max_sessions": stats["max_sessions"],
    }


@app.get("/stats")
async def stats():
    """Get detailed server statistics."""
    return {
        "server_stats": manager.get_stats(),
        "available_tasks": len(get_task_variants()),
        "total_leaderboard_entries": len(manager.leaderboard),
    }


@app.get("/manifest")
async def manifest():
    """Return OpenEnv specification for this environment."""
    return {
        "version": "3.0.0",
        "name": "LUNAR: Multi-Domain RL Environment",
        "description": "Multi-domain optimization including warehouse management, supply chain, demand forecasting, production scheduling, and resource allocation",
        "observation_space": {
            "type": "object",
            "properties": {
                "warehouse_levels": {"type": "array", "items": {"type": "number"}},
                "demand_forecast": {"type": "array", "items": {"type": "number"}},
                "supplier_status": {"type": "array", "items": {"type": "number"}},
                "day": {"type": "integer"},
                "holding_costs": {"type": "number"},
                "shortage_penalty": {"type": "number"},
            }
        },
        "action_space": {
            "type": "object",
            "properties": {
                "reorder_quantities": {"type": "array", "items": {"type": "number"}},
                "transfers": {"type": "array", "items": {"type": "array"}},
            }
        },
        "reward_space": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "done": {"type": "boolean"},
                "info": {"type": "object"},
            }
        },
        "tasks": list(get_task_variants().keys()),
        "domains": [
            "warehouse_management",
            "supply_chain_logistics",
            "demand_forecasting",
            "production_scheduling",
            "dynamic_resource_allocation"
        ],
        "features": {
            "multi_agent": True,
            "session_management": True,
            "automatic_cleanup": True,
            "leaderboard": True,
            "task_variants": 21,
            "multi_domain": True,
        }
    }


@app.get("/tasks")
async def list_tasks():
    """List all available task variants."""
    return {
        "total": len(get_task_variants()),
        "tasks": get_task_variants()
    }


@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return {
        "active_sessions": len(manager.sessions),
        "sessions": manager.list_sessions()
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        manager.delete_session(session_id)
        return {"status": "ok", "message": f"Session {session_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/leaderboard")
async def leaderboard(limit: int = Query(10, ge=1, le=100)):
    """Get top sessions by reward."""
    return {
        "total_sessions": len(manager.leaderboard),
        "leaderboard": manager.get_leaderboard(limit=limit)
    }


@app.get("/")
async def root():
    """Welcome endpoint - redirects to API documentation."""
    return {
        "message": "Welcome to LUNAR: Multi-Domain RL Environment",
        "version": "3.0.0",
        "documentation": "http://localhost:7860/docs",
        "endpoints": {
            "health": "/health",
            "tasks": "/tasks",
            "manifest": "/manifest",
            "reset": "/reset (POST)",
            "step": "/step (POST)",
            "state": "/state",
            "sessions": "/sessions",
            "leaderboard": "/leaderboard",
            "stats": "/stats"
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
