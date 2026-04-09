"""FastAPI server for multi-domain RL environment (31 tasks across 5 domains)."""

import os
import sys
import asyncio
import traceback
import yaml
from typing import Optional, Any, Dict, List
from fastapi import FastAPI, HTTPException, Query, Body, Path
from pydantic import BaseModel, Field
import uvicorn

from .multi_domain_env import MultiDomainEnv
from .graders_comprehensive import get_grader_for_task
from .session_manager import SessionManager
from .task_config import (
    get_task_variants, 
    get_task_info, 
    is_valid_task, 
    get_all_domains,
    get_task_count,
    get_domain_count
)

app = FastAPI(
    title="Lunar: Multi-Domain Comprehensive Benchmark",
    version="2.0",
    description="31-task benchmark across 5 domains with comprehensive evaluation",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Session management
manager = SessionManager(max_sessions=1000, session_timeout_hours=24)


# ===== Request/Response Models =====

class ResetRequest(BaseModel):
    """Reset environment and create new session."""
    task: str = Field(
        default="warehouse_novice",
        description="Task ID from 31 available tasks"
    )
    session_id: Optional[str] = Field(None, description="Optional session ID to reuse")


class ResetResponse(BaseModel):
    """Response after environment reset."""
    session_id: str = Field(..., description="Unique session ID")
    task: str = Field(..., description="Selected task ID")
    state: Dict[str, Any] = Field(..., description="Initial environment state")
    max_steps: int = Field(..., description="Maximum steps for this task")


class StepRequest(BaseModel):
    """Step action request - domain-specific."""
    action: Dict[str, Any] = Field(..., description="Domain-specific action dictionary")


class StepResponse(BaseModel):
    """Response after environment step."""
    session_id: str = Field(..., description="Session ID")
    state: Dict[str, Any] = Field(..., description="Updated environment state")
    reward: float = Field(..., description="Step reward in [0, 1]")
    done: bool = Field(..., description="Episode done flag")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional info")


class ManifestResponse(BaseModel):
    """Environment specification."""
    version: str
    name: str
    description: str
    task_count: int
    domain_count: int
    domains: List[str]
    tasks: List[str]
    graders: List[str]
    features: Dict[str, Any]
    task_specs: Dict[str, Dict[str, Any]]


class TasksResponse(BaseModel):
    """All available tasks."""
    total: int = Field(..., description="Total number of tasks")
    tasks: Dict[str, Any] = Field(..., description="Task specifications")


class StateResponse(BaseModel):
    """Session state query response."""
    session_id: str
    task: str
    state: Dict[str, Any]
    steps: int
    cumulative_reward: float
    done: bool


class LeaderboardResponse(BaseModel):
    """Leaderboard rankings."""
    total_sessions: int
    leaderboard: List[Dict[str, Any]]


class SessionsListResponse(BaseModel):
    """Active sessions list."""
    active_sessions: int
    sessions: List[Dict[str, Any]]


# ===== Endpoints =====

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0",
        "tasks": get_task_count(),
        "domains": get_domain_count()
    }


@app.get("/manifest", response_model=ManifestResponse)
async def get_manifest():
    """Get environment specification."""
    try:
        # Load openenv.yaml for reference
        try:
            with open("openenv.yaml", "r") as f:
                yaml_spec = yaml.safe_load(f)
        except:
            yaml_spec = {}

        tasks = get_task_variants()
        domains = get_all_domains()

        # Build task specs with grader info
        task_specs = {}
        for task_id, task_info in tasks.items():
            task_specs[task_id] = {
                "name": task_info.get("name", task_id),
                "description": task_info.get("description", ""),
                "domain": task_info.get("domain", ""),
                "difficulty": task_info.get("difficulty", ""),
                "has_grader": True,
                "grader_type": task_info.get("grader_type", "ComprehensiveGrader"),
                "max_steps": task_info.get("max_steps", 100),
            }

        # Domain-level graders (not task-level)
        # One grader per domain handles multiple tasks
        domain_graders = [
            "warehouse_grader",
            "data_pipeline_grader",
            "code_review_grader",
            "resource_allocation_grader",
            "system_optimization_grader"
        ]

        return ManifestResponse(
            version="2.0",
            name="Lunar: Comprehensive Multi-Domain Benchmark",
            description="32 tasks across 5 domains with deterministic grading",
            task_count=len(tasks),
            domain_count=len(domains),
            domains=domains,
            tasks=list(tasks.keys()),
            graders=domain_graders,
            features={
                "tasks_with_graders": len(tasks),
                "multi_domain": True,
                "deterministic_grading": True,
                "episode_based_scoring": True,
                "session_management": True,
                "leaderboard": True
            },
            task_specs=task_specs
        )
    except Exception as e:
        print(f"ERROR in /manifest: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Manifest error: {str(e)}")


@app.get("/tasks", response_model=TasksResponse)
async def get_tasks():
    """Get all 31 available tasks."""
    try:
        tasks = get_task_variants()
        task_specs = {}

        for task_id, task_info in tasks.items():
            task_specs[task_id] = {
                "id": task_id,
                "name": task_info.get("name", task_id),
                "description": task_info.get("description", ""),
                "domain": task_info.get("domain", ""),
                "difficulty": task_info.get("difficulty", ""),
                "has_grader": True,
                "grader_type": task_info.get("grader_type", "ComprehensiveGrader"),
                "max_steps": task_info.get("max_steps", 100),
                "version": task_info.get("version", "1.0"),
            }

        return TasksResponse(
            total=len(tasks),
            tasks=task_specs
        )
    except Exception as e:
        print(f"ERROR in /tasks: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Tasks error: {str(e)}")


@app.post("/reset", response_model=ResetResponse)
async def reset_environment(
    req: Optional[ResetRequest] = Body(None),
    task: Optional[str] = Query(None, description="Task ID")
):
    """Initialize new environment episode."""
    try:
        # Determine task to use
        final_task = task or (req.task if req and req.task else "warehouse_novice")

        # Validate task
        if not is_valid_task(final_task):
            raise HTTPException(
                status_code=400,
                detail=f"Unknown task: {final_task}. Available tasks: {list(get_task_variants().keys())[:5]}..."
            )

        # Create session (creates MultiDomainEnv internally)
        session_id = manager.create_session(final_task)
        env = manager.get_session(session_id)
        
        # Initialize environment state
        initial_state = env.reset()

        return ResetResponse(
            session_id=session_id,
            task=final_task,
            state=initial_state,
            max_steps=env.max_steps
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in /reset: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")


@app.post("/step", response_model=StepResponse)
async def step_environment(
    session_id: str = Query(..., description="Session ID from /reset"),
    req: StepRequest = Body(..., description="Action")
):
    """Execute one environment step."""
    try:
        # Get environment from session
        env = manager.get_session(session_id)
        if not env:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

        # Handle warehouse-specific action conversion
        action = req.action

        # For warehouse domain, auto-convert reorder_quantities format
        if env.domain == "warehouse" and "reorder_quantities" in action:
            if isinstance(action["reorder_quantities"], (int, float)):
                action["reorder_quantities"] = [action["reorder_quantities"]]
            elif len(action.get("reorder_quantities", [])) == 1 and env.num_warehouses > 1:
                action["reorder_quantities"] = action["reorder_quantities"] * env.num_warehouses

        # Execute step
        next_state, reward = env.step(action)

        # Check if done
        is_done = env.is_done()

        # Get final reward using grader if done
        final_reward = reward
        if is_done:
            final_reward = env.get_episode_reward()

        # Record reward in session manager
        manager.record_reward(session_id, final_reward)

        # Calculate cumulative reward
        rewards = manager.session_rewards.get(session_id, [])
        cumulative_reward = sum(rewards) if rewards else 0.0
        
        return StepResponse(
            session_id=session_id,
            state=next_state,
            reward=final_reward,
            done=is_done,
            info={
                "current_step": env.current_step,
                "max_steps": env.max_steps,
                "cumulative_reward": cumulative_reward
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in /step with session {session_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Step error: {str(e)}")


@app.get("/state/{session_id}", response_model=StateResponse)
async def get_state(session_id: str = Path(..., description="Session ID")):
    """Get session state by path parameter."""
    try:
        env = manager.get_session(session_id)
        metadata = manager.get_metadata(session_id)
        rewards = manager.session_rewards.get(session_id, [])
        cumulative_reward = sum(rewards) if rewards else 0.0

        return StateResponse(
            session_id=session_id,
            task=metadata.get("task", "unknown"),
            state=env.state.copy() if env.state else {},
            steps=metadata.get("steps", 0),
            cumulative_reward=cumulative_reward,
            done=metadata.get("done", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in /state/{session_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"State error: {str(e)}")


# Support legacy query parameter style too
@app.get("/state", response_model=StateResponse)
async def get_state_query(session_id: str = Query(..., description="Session ID")):
    """Get session state by query parameter (legacy support)."""
    return await get_state(session_id)


@app.get("/sessions", response_model=SessionsListResponse)
async def get_active_sessions():
    """List all active sessions."""
    try:
        sessions_list = manager.list_sessions()
        return SessionsListResponse(
            active_sessions=len(sessions_list),
            sessions=sessions_list
        )
    except Exception as e:
        print(f"ERROR in /sessions: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Sessions error: {str(e)}")


@app.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(limit: int = Query(100, ge=1, le=1000)):
    """Get leaderboard rankings by cumulative reward."""
    try:
        leaderboard = manager.get_leaderboard(limit=limit)
        return LeaderboardResponse(
            total_sessions=len(manager.sessions),
            leaderboard=leaderboard
        )
    except Exception as e:
        print(f"ERROR in /leaderboard: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Leaderboard error: {str(e)}")


@app.get("/docs", include_in_schema=False)
async def swagger_docs():
    """Swagger documentation is handled automatically by FastAPI."""
    pass


@app.get("/openapi.json", include_in_schema=False)
async def openapi_spec():
    """OpenAPI specification is handled automatically by FastAPI."""
    pass


def start_server(host: str = "0.0.0.0", port: int = 7860, debug: bool = False):
    """Start the FastAPI server."""
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info" if debug else "warning"
    )


if __name__ == "__main__":
    start_server()
