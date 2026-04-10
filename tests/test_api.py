import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Content Moderation Benchmark" in response.json()["name"]


def test_manifest():
    """Test manifest endpoint"""
    response = client.get("/manifest")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "content-moderation-benchmark"
    assert data["tasks"] == 3


def test_start_session_task1():
    """Test starting a Task 1 session"""
    response = client.post(
        "/session/start",
        json={"task_id": 1, "seed": 42}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["task_id"] == 1
    assert "observation" in data


def test_start_session_task2():
    """Test starting a Task 2 session"""
    response = client.post(
        "/session/start",
        json={"task_id": 2}
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == 2


def test_start_session_task3():
    """Test starting a Task 3 session"""
    response = client.post(
        "/session/start",
        json={"task_id": 3}
    )
    assert response.status_code == 200
    assert response.json()["task_id"] == 3


def test_invalid_task_id():
    """Test invalid task ID"""
    response = client.post(
        "/session/start",
        json={"task_id": 99}
    )
    assert response.status_code == 400


def test_step():
    """Test execution step"""
    # Start session
    start_response = client.post(
        "/session/start",
        json={"task_id": 1}
    )
    session_id = start_response.json()["session_id"]
    
    # Step
    step_response = client.post(
        f"/session/{session_id}/step",
        json={"action": {"category": "safe"}}
    )
    
    assert step_response.status_code == 200
    data = step_response.json()
    assert "reward" in data
    assert "observation" in data
    assert "done" in data
    assert 0.0 <= data["reward"] <= 1.0


def test_session_summary():
    """Test session summary"""
    # Start and step
    start_response = client.post(
        "/session/start",
        json={"task_id": 1}
    )
    session_id = start_response.json()["session_id"]
    
    # Take a few steps
    for _ in range(3):
        client.post(
            f"/session/{session_id}/step",
            json={"action": {"category": "safe"}}
        )
    
    # Get summary
    summary_response = client.get(f"/session/{session_id}/summary")
    assert summary_response.status_code == 200
    data = summary_response.json()
    assert "summary" in data
    assert data["summary"]["total_steps"] == 3


def test_delete_session():
    """Test session deletion"""
    # Create session
    start_response = client.post(
        "/session/start",
        json={"task_id": 1}
    )
    session_id = start_response.json()["session_id"]
    
    # Delete
    delete_response = client.delete(f"/session/{session_id}")
    assert delete_response.status_code == 200
    
    # Try to access deleted session
    summary_response = client.get(f"/session/{session_id}/summary")
    assert summary_response.status_code == 400


def test_list_tasks():
    """Test listing tasks"""
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 3
    assert data["tasks"][0]["difficulty"] == "easy"
    assert data["tasks"][1]["difficulty"] == "medium"
    assert data["tasks"][2]["difficulty"] == "hard"


def test_stats():
    """Test statistics endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "tasks_available" in data
    assert data["tasks_available"] == 3
    assert data["reward_range"] == [0.0, 1.0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
