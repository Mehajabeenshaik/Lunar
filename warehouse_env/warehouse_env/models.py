"""Typed models for Warehouse RL environment."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field, validator


class State(BaseModel):
    """Complete environment state."""
    
    warehouse_levels: List[float] = Field(..., description="Inventory at each warehouse")
    demand_forecast: List[float] = Field(..., description="Demand forecast for next step")
    supplier_status: List[float] = Field(..., description="Supplier availability (0-1)")
    day: int = Field(..., ge=0, le=365, description="Current simulation day")
    holding_costs: float = Field(default=0.0, description="Cumulative holding cost")
    shortage_penalty: float = Field(default=0.0, description="Cumulative shortage penalty")
    last_action_error: str | None = Field(default=None, description="Last action error if any")
    
    @validator("warehouse_levels", "demand_forecast", "supplier_status")
    def validate_ranges(cls, v):
        for val in v:
            if val < 0 or val > 1000:
                raise ValueError(f"Value {val} out of range [0, 1000]")
        return v


class Action(BaseModel):
    """Agent action specification."""
    
    reorder_quantities: List[float] = Field(..., description="Units to reorder at each warehouse (0-500)")
    transfers: List[List[float]] = Field(..., description="Inter-warehouse transfers (matrix)")
    
    @validator("reorder_quantities")
    def validate_reorder(cls, v):
        for val in v:
            if val < 0 or val > 500:
                raise ValueError(f"Reorder quantity {val} out of range [0, 500]")
        return v


class Observation(BaseModel):
    """Observable state returned to agent."""
    
    warehouse_levels: List[float]
    demand_forecast: List[float]
    supplier_status: List[float]
    day: int
    holding_costs: float
    shortage_penalty: float
    
    @classmethod
    def from_state(cls, state: State) -> "Observation":
        """Create observation from state."""
        return cls(
            warehouse_levels=state.warehouse_levels,
            demand_forecast=state.demand_forecast,
            supplier_status=state.supplier_status,
            day=state.day,
            holding_costs=state.holding_costs,
            shortage_penalty=state.shortage_penalty,
        )


class Reward(BaseModel):
    """Reward structure."""
    
    value: float = Field(..., ge=0.0, le=1.0, description="Reward in [0, 1]")
    done: bool = Field(default=False, description="Episode terminated")
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional info")
