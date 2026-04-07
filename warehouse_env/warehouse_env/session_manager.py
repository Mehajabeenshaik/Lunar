"""Session management for multi-agent support."""

from uuid import uuid4
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from .env import WarehouseEnv


class SessionManager:
    """Manage multiple parallel environment sessions with automatic cleanup."""
    
    def __init__(self, max_sessions: int = 100, session_timeout_hours: int = 2):
        self.sessions: Dict[str, WarehouseEnv] = {}
        self.session_metadata: Dict[str, dict] = {}
        self.leaderboard: Dict[str, float] = {}
        self.session_rewards: Dict[str, List[float]] = {}
        self.max_sessions = max_sessions
        self.session_timeout = timedelta(hours=session_timeout_hours)
    
    def _cleanup_old_sessions(self):
        """Remove sessions older than timeout to prevent memory leaks."""
        now = datetime.now()
        expired = []
        
        for session_id, metadata in self.session_metadata.items():
            try:
                created_at = datetime.fromisoformat(metadata["created_at"])
                if now - created_at > self.session_timeout:
                    expired.append(session_id)
            except:
                pass  # Skip on parse error
        
        for session_id in expired:
            self.delete_session(session_id)
        
        return len(expired)
    
    def create_session(self, task: str) -> str:
        """Create new session with unique ID."""
        # Cleanup old sessions to manage memory
        self._cleanup_old_sessions()
        
        # If at capacity, cleanup oldest session
        if len(self.sessions) >= self.max_sessions:
            oldest = min(
                self.session_metadata.items(),
                key=lambda x: x[1]["created_at"]
            )[0]
            self.delete_session(oldest)
        
        session_id = str(uuid4())
        self.sessions[session_id] = WarehouseEnv(task=task)
        self.session_metadata[session_id] = {
            "task": task,
            "created_at": datetime.now().isoformat(),
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
        if session_id in self.leaderboard:
            del self.leaderboard[session_id]
    
    def list_sessions(self) -> List[dict]:
        """List all active sessions."""
        return [
            {
                "session_id": sid,
                **self.session_metadata[sid]
            }
            for sid in self.sessions.keys()
        ]
    
    def get_stats(self) -> dict:
        """Get session manager statistics."""
        return {
            "total_sessions": len(self.sessions),
            "total_leaderboard": len(self.leaderboard),
            "max_sessions": self.max_sessions,
            "memory_usage_mb": sum(
                len(str(self.session_metadata.get(sid, {})))
                for sid in self.sessions.keys()
            ) / 1024 / 1024,
        }
