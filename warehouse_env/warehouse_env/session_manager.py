"""Hybrid session management: in-memory cache + SQLite persistence for multi-worker support."""

from uuid import uuid4
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import json
import sqlite3
from pathlib import Path
from .multi_domain_env import MultiDomainEnv


class SessionManager:
    """Hybrid session manager for HuggingFace Spaces multi-worker compatibility.
    
    Uses:
    - In-memory cache for fast access (local worker)
    - SQLite persistence for cross-worker state sharing
    """
    
    def __init__(self, max_sessions: int = 100, session_timeout_hours: int = 2, 
                 db_path: str = ".sessions/lunar.db"):
        self.sessions: Dict[str, MultiDomainEnv] = {}
        self.session_metadata: Dict[str, dict] = {}
        self.leaderboard: Dict[str, float] = {}
        self.session_rewards: Dict[str, List[float]] = {}
        self.max_sessions = max_sessions
        self.session_timeout = timedelta(hours=session_timeout_hours)
        
        # SQLite persistence for cross-worker support
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        task TEXT NOT NULL,
                        state_json TEXT,
                        rewards_json TEXT,
                        step_count INTEGER DEFAULT 0,
                        best_reward REAL DEFAULT 0.0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        done BOOLEAN DEFAULT 0
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not initialize SQLite DB: {e}")
    
    def _persist_session(self, session_id: str):
        """Persist session state to SQLite."""
        try:
            if session_id not in self.session_metadata:
                return
            
            meta = self.session_metadata[session_id]
            rewards = self.session_rewards.get(session_id, [])
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sessions 
                    (session_id, task, rewards_json, step_count, best_reward, 
                     created_at, updated_at, done)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    meta.get("task", ""),
                    json.dumps(rewards),
                    meta.get("steps", 0),
                    meta.get("best_reward", 0.0),
                    meta.get("created_at", datetime.now().isoformat()),
                    datetime.now().isoformat(),
                    meta.get("done", False),
                ))
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not persist session {session_id}: {e}")
    
    def _load_session_from_db(self, session_id: str) -> Optional[Dict]:
        """Load session from SQLite if not in memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'session_id': row[0],
                        'task': row[1],
                        'rewards': json.loads(row[3] or '[]'),
                        'steps': row[4],
                        'best_reward': row[5],
                        'created_at': row[6],
                    }
        except Exception as e:
            print(f"Warning: Could not load session from DB: {e}")
        return None
    
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
        self.sessions[session_id] = MultiDomainEnv(task_id=task)
        self.session_metadata[session_id] = {
            "task": task,
            "created_at": datetime.now().isoformat(),
            "steps": 0,
            "best_reward": 0.0,
        }
        self.session_rewards[session_id] = []
        return session_id
    
    def get_session(self, session_id: str) -> MultiDomainEnv:
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
