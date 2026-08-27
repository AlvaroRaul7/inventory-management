"""
Tests for tasks (GET/POST/PATCH/DELETE) API endpoints.
"""
import pytest


class TestTasksEndpoints:
    """Test suite for /api/tasks CRUD endpoints."""

    def test_get_all_tasks(self, client):
        """Test getting all tasks returns a list."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_task(self, client):
        """Test creating a task returns the created task with expected fields."""
        payload = {
            "title": "Reconcile inbound shipment count",
            "priority": "high",
            "dueDate": "2025-11-01",
        }
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 201

        task = response.json()
        assert "id" in task
        assert task["title"] == payload["title"]
        assert task["priority"] == payload["priority"]
        assert task["dueDate"] == payload["dueDate"]
        assert task["status"] == "pending"

        list_response = client.get("/api/tasks")
        all_tasks = list_response.json()
        assert any(t["id"] == task["id"] for t in all_tasks)

    def test_create_task_respects_explicit_status(self, client):
        """Test that an explicitly provided status overrides the default."""
        payload = {
            "title": "Archive closed backlog item",
            "priority": "low",
            "dueDate": "2025-11-05",
            "status": "completed",
        }
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 201
        assert response.json()["status"] == "completed"

    def test_toggle_task_status(self, client):
        """Test that PATCH toggles a task between pending and completed."""
        create_response = client.post("/api/tasks", json={
            "title": "Verify supplier invoice",
            "priority": "medium",
            "dueDate": "2025-11-10",
        })
        task_id = create_response.json()["id"]
        assert create_response.json()["status"] == "pending"

        toggle_response = client.patch(f"/api/tasks/{task_id}")
        assert toggle_response.status_code == 200
        assert toggle_response.json()["status"] == "completed"

        toggle_again_response = client.patch(f"/api/tasks/{task_id}")
        assert toggle_again_response.status_code == 200
        assert toggle_again_response.json()["status"] == "pending"

    def test_toggle_nonexistent_task(self, client):
        """Test toggling a task that doesn't exist returns 404."""
        response = client.patch("/api/tasks/nonexistent-task-999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_delete_task(self, client):
        """Test that DELETE removes a task."""
        create_response = client.post("/api/tasks", json={
            "title": "Confirm reorder point for SKU",
            "priority": "low",
            "dueDate": "2025-11-15",
        })
        task_id = create_response.json()["id"]

        delete_response = client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 204

        list_response = client.get("/api/tasks")
        all_tasks = list_response.json()
        assert all(t["id"] != task_id for t in all_tasks)

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist returns 404."""
        response = client.delete("/api/tasks/nonexistent-task-999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
