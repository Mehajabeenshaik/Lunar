"""FastAPI server for warehouse environment."""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .env import WarehouseEnv
from .models import Action, Observation
from .graders import get_grader

app = FastAPI(title="Warehouse Environment", version="1.0.0")

# Global environment state
_env: Optional[WarehouseEnv] = None
_task: str = os.getenv("WAREHOUSE_TASK", "warehouse_easy")


class ResetRequest(BaseModel):
    task: Optional[str] = None


class ResetResponse(BaseModel):
    observation: dict
    task: str


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
async def reset(req: Optional[ResetRequest] = None):
    """Reset environment to initial state."""
    global _env, _task
    
    task = req.task if req and req.task else _task
    _task = task
    
    _env = WarehouseEnv(task=task)
    obs = _env.reset()
    
    return ResetResponse(observation=obs.model_dump(), task=task)


@app.post("/step", response_model=StepResponse)
async def step(req: StepRequest):
    """Execute one environment step."""
    global _env
    
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not reset. Call /reset first.")
    
    try:
        action = Action(**req.action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid action: {str(e)}")
    
    obs, reward = _env.step(action)
    
    return StepResponse(
        observation=obs.model_dump(),
        reward=reward.value,
        done=reward.done,
        info=reward.info,
    )


@app.get("/state", response_model=StateResponse)
async def state():
    """Get current environment state."""
    global _env
    
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not reset. Call /reset first.")
    
    return StateResponse(
        state=_env.state_dict(),
        task=_env.task,
        episode_rewards=_env.episode_rewards,
    )


@app.get("/render")
async def render():
    """Render environment visualization."""
    global _env
    
    if _env is None:
        return {"render": "Environment not initialized"}
    
    return {"render": _env.render()}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/manifest")
async def manifest():
    """Return OpenEnv specification for this environment."""
    return {
        "version": "1.0.0",
        "name": "Warehouse Inventory Management",
        "description": "Multi-warehouse inventory optimization RL environment",
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
        "tasks": [
            {"id": "warehouse_easy", "description": "1 warehouse, 30 steps"},
            {"id": "warehouse_medium", "description": "3 warehouses, 60 steps"},
            {"id": "warehouse_hard", "description": "5 warehouses, 90 steps"},
        ],
        "endpoints": {
            "/health": "GET - Health check",
            "/manifest": "GET - OpenEnv specification",
            "/reset": "POST - Initialize episode",
            "/step": "POST - Execute action",
            "/state": "GET - Current state",
            "/render": "GET - Visualization",
            "/docs": "GET - API documentation",
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
