"""Session management for multi-agent support."""

from uuid import uuid4
from typing import Dict, Optional, List
from .env import WarehouseEnv


class SessionManager:
    """Manage multiple parallel environment sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, WarehouseEnv] = {}
        self.session_metadata: Dict[str, dict] = {}
        self.leaderboard: Dict[str, float] = {}
        self.session_rewards: Dict[str, List[float]] = {}
    
    def create_session(self, task: str) -> str:
        """Create new session with unique ID."""
        session_id = str(uuid4())
        self.sessions[session_id] = WarehouseEnv(task=task)
        self.session_metadata[session_id] = {
            "task": task,
            "created_at": str(__import__('datetime').datetime.now()),
            "steps": 0,
            "best_reward": 0.0,
        }
        self.session_rewards[session_id] = []
        return session_id
    
    def get_session(self, session_id: str) -> WarehouseEnv:
        """Get environment for session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]
    
    def get_metadata(self, session_id: str) -> dict:
        """Get session metadata."""
        if session_id not in self.session_metadata:
            raise ValueError(f"Session {session_id} not found")
        return self.session_metadata[session_id]
    
    def record_reward(self, session_id: str, reward: float):
        """Record reward for session."""
        if session_id not in self.session_rewards:
            self.session_rewards[session_id] = []
        
        self.session_rewards[session_id].append(reward)
        
        # Update metadata
        self.session_metadata[session_id]["steps"] += 1
        self.session_metadata[session_id]["best_reward"] = max(
            self.session_metadata[session_id]["best_reward"], 
            reward
        )
        
        # Update leaderboard (use best reward per session)
        self.leaderboard[session_id] = self.session_metadata[session_id]["best_reward"]
    
    def get_leaderboard(self, limit: int = 10) -> List[dict]:
        """Get top sessions by reward."""
        sorted_sessions = sorted(
            self.leaderboard.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        result = []
        for session_id, reward in sorted_sessions:
            meta = self.session_metadata.get(session_id, {})
            result.append({
                "session_id": session_id,
                "task": meta.get("task", "unknown"),
                "best_reward": reward,
                "steps": meta.get("steps", 0),
                "created_at": meta.get("created_at", ""),
            })
        
        return result
    
    def delete_session(self, session_id: str):
        """Clean up session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
        if session_id in self.session_rewards:
            del self.session_rewards[session_id]
    
    def list_sessions(self) -> List[dict]:
        """List all active sessions."""
        return [
            {
                "session_id": sid,
                **self.session_metadata[sid]
            }
            for sid in self.sessions.keys()
        ]
