"""FastAPI server for warehouse environment."""

import os
import sys
import asyncio
import traceback
from typing import Optional, Any, Dict, List
from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field, field_validator, ValidationError
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
    """Reset request - supports both query params and body."""
    task: Optional[str] = Field(
        default="warehouse_easy",
        description="Task ID (warehouse_easy, warehouse_medium, supply_chain_basic, etc). Defaults to warehouse_easy."
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID to reuse"
    )


class ResetResponse(BaseModel):
    observation: Dict[str, Any] = Field(..., description="Initial observation state")
    task: str = Field(..., description="Selected task ID")
    session_id: Optional[str] = Field(None, description="Session ID for subsequent requests")


class StepRequest(BaseModel):
    action: Dict[str, Any] = Field(..., description="Action to execute in the environment")


class StepResponse(BaseModel):
    observation: Dict[str, Any] = Field(..., description="Updated observation state")
    reward: float = Field(..., description="Reward signal (0.0-1.0)")
    done: bool = Field(..., description="Episode termination flag")
    info: Dict[str, Any] = Field(..., description="Additional step information")


class StateResponse(BaseModel):
    state: Dict[str, Any] = Field(..., description="Complete environment state")
    task: str = Field(..., description="Current task ID")
    episode_rewards: List[float] = Field(..., description="Cumulative rewards per episode")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Server status")
    version: str = Field(..., description="API version")
    active_sessions: int = Field(..., description="Number of active sessions")
    max_sessions: int = Field(..., description="Maximum concurrent sessions")


class StatsResponse(BaseModel):
    server_stats: Dict[str, Any] = Field(..., description="Server statistics")
    available_tasks: int = Field(..., description="Number of available tasks")
    total_leaderboard_entries: int = Field(..., description="Total leaderboard entries")


class TasksListResponse(BaseModel):
    total: int = Field(..., description="Total number of tasks")
    tasks: Dict[str, Any] = Field(..., description="Task specifications")


class SessionsListResponse(BaseModel):
    active_sessions: int = Field(..., description="Number of active sessions")
    sessions: List[str] = Field(..., description="List of session IDs")


class LeaderboardResponse(BaseModel):
    total_sessions: int = Field(..., description="Total sessions recorded")
    leaderboard: List[Dict[str, Any]] = Field(..., description="Top sessions by reward")


class ManifestResponse(BaseModel):
    version: str = Field(..., description="API version")
    name: str = Field(..., description="Environment name")
    description: str = Field(..., description="Environment description")
    observation_space: Dict[str, Any] = Field(..., description="Observation space specification")
    action_space: Dict[str, Any] = Field(..., description="Action space specification")
    reward_space: Dict[str, Any] = Field(..., description="Reward space specification")
    tasks: List[str] = Field(..., description="Available tasks")
    domains: List[str] = Field(..., description="Domains covered")
    features: Dict[str, Any] = Field(..., description="Available features")


class RenderResponse(BaseModel):
    render: str = Field(..., description="Rendered environment visualization")


@app.post("/reset", response_model=ResetResponse)
async def reset(
    req: Optional[ResetRequest] = Body(None),
    task: Optional[str] = Query(None, description="Task ID (overrides body if provided)"),
    session_id: Optional[str] = Query(None, description="Session ID (overrides body if provided)")
):
    """Reset environment to initial state (create new session if needed).
    
    Accepts task and session_id via:
    - Query parameters: /reset?task=warehouse_easy&session_id=xyz
    - Request body: POST with {"task": "warehouse_easy", "session_id": "xyz"}
    - Mixed: /reset?session_id=xyz with body {"task": "warehouse_easy"}
    """
    try:
        # Use query params if provided, otherwise use body, otherwise use defaults
        final_task = task or (req.task if req else None) or "warehouse_easy"
        final_session_id = session_id or (req.session_id if req else None)
        
        # Validate task
        if not is_valid_task(final_task):
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task: {final_task}. Valid tasks: {list(get_task_variants().keys())}"
            )
        
        # Create or reuse session
        if not final_session_id:
            final_session_id = manager.create_session(final_task)
        
        env = manager.get_session(final_session_id)
        obs = env.reset()
        
        return ResetResponse(
            observation=obs.model_dump(),
            task=final_task,
            session_id=final_session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Reset failed: {str(e)}\n{traceback.format_exc()}"
        print(error_detail, file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
    except (ValueError, ValidationError) as e:
        error_msg = f"Invalid action: {str(e)}"
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = f"Action processing error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        raise HTTPException(status_code=400, detail=f"Invalid action format")
    
    try:
        obs, reward = env.step(action)
    except Exception as e:
        error_msg = f"Step execution failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Step execution failed: {str(e)}")
    
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
async def render(session_id: str = Query(None)) -> RenderResponse:
    """Render environment visualization."""
    
    if not session_id:
        return RenderResponse(render="No session provided")
    
    try:
        env = manager.get_session(session_id)
    except ValueError:
        return RenderResponse(render="Session not found")
    
    return RenderResponse(render=env.render())


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint with system stats."""
    stats = manager.get_stats()
    return HealthResponse(
        status="ok",
        version="3.0.0",
        active_sessions=stats["total_sessions"],
        max_sessions=stats["max_sessions"],
    )


@app.get("/stats", response_model=StatsResponse)
async def stats():
    """Get detailed server statistics."""
    return StatsResponse(
        server_stats=manager.get_stats(),
        available_tasks=len(get_task_variants()),
        total_leaderboard_entries=len(manager.leaderboard),
    )


@app.get("/manifest", response_model=ManifestResponse)
async def manifest():
    """Return OpenEnv specification for this environment."""
    return ManifestResponse(
        version="3.0.0",
        name="LUNAR: Multi-Domain RL Environment",
        description="Multi-domain optimization including warehouse management, supply chain, demand forecasting, production scheduling, and resource allocation",
        observation_space={
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
        action_space={
            "type": "object",
            "properties": {
                "reorder_quantities": {"type": "array", "items": {"type": "number"}},
                "transfers": {"type": "array", "items": {"type": "array"}},
            }
        },
        reward_space={
            "type": "object",
            "properties": {
                "value": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "done": {"type": "boolean"},
                "info": {"type": "object"},
            }
        },
        tasks=list(get_task_variants().keys()),
        domains=[
            "warehouse_management",
            "supply_chain_logistics",
            "demand_forecasting",
            "production_scheduling",
            "dynamic_resource_allocation"
        ],
        features={
            "multi_agent": True,
            "session_management": True,
            "automatic_cleanup": True,
            "leaderboard": True,
            "task_variants": len(get_task_variants()),
            "multi_domain": True,
        }
    )


@app.get("/tasks", response_model=TasksListResponse)
async def list_tasks():
    """List all available task variants."""
    return TasksListResponse(
        total=len(get_task_variants()),
        tasks=get_task_variants()
    )


@app.get("/sessions", response_model=SessionsListResponse)
async def list_sessions():
    """List all active sessions."""
    return SessionsListResponse(
        active_sessions=len(manager.sessions),
        sessions=list(manager.sessions.keys())
    )


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        manager.delete_session(session_id)
        return {"status": "ok", "message": f"Session {session_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/leaderboard", response_model=LeaderboardResponse)
async def leaderboard(limit: int = Query(10, ge=1, le=100)):
    """Get top sessions by reward."""
    return LeaderboardResponse(
        total_sessions=len(manager.leaderboard),
        leaderboard=manager.get_leaderboard(limit=limit)
    )


@app.get("/", response_model=Dict[str, Any])
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


def main():
    """Main entry point for the server."""
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
