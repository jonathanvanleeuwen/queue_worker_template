from unittest.mock import MagicMock, patch

from rq.job import Job


class TestJobsRouter:
    """Test jobs router endpoints."""

    def test_health_check_no_auth(self, client):
        """Health check should not require authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_root_no_auth(self, client):
        """Root endpoint should not require authentication."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_enqueue_without_auth(self, client):
        """Enqueue endpoint should require authentication."""
        response = client.post(
            "/api/jobs/enqueue",
            json={
                "task_name": "transform_data",
                "task_args": {"data": {"key": "value"}, "operation": "uppercase_keys"},
            },
        )
        # Auth failure redirects to /static/
        assert response.status_code == 307

    def test_enqueue_with_invalid_auth(self, client, invalid_headers):
        """Enqueue with invalid auth should fail."""
        response = client.post(
            "/api/jobs/enqueue",
            headers=invalid_headers,
            json={
                "task_name": "transform_data",
                "task_args": {"data": {"key": "value"}, "operation": "uppercase_keys"},
            },
        )
        # Auth failure redirects to /static/
        assert response.status_code == 307

    @patch("{{cookiecutter.project_name}}.routers.jobs.enqueue_job")
    def test_enqueue_with_valid_auth(self, mock_enqueue, client, user_headers):
        """Enqueue with valid auth should succeed."""
        # Mock the Job object returned by enqueue_job
        mock_job = MagicMock(spec=Job)
        mock_job.id = "test-job-id"
        mock_job.get_status.return_value = "queued"
        mock_job.enqueued_at = None
        mock_enqueue.return_value = mock_job

        response = client.post(
            "/api/jobs/enqueue",
            headers=user_headers,
            json={
                "task_name": "transform_data",
                "task_args": {"data": {"key": "value"}, "operation": "uppercase_keys"},
                "queue": "default",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["job_id"] == "test-job-id"
        assert data["queue"] == "default"
        assert data["task_name"] == "transform_data"

    def test_enqueue_unknown_task(self, client, user_headers):
        """Enqueue unknown task should fail with 400."""
        response = client.post(
            "/api/jobs/enqueue",
            headers=user_headers,
            json={
                "task_name": "unknown_task",
                "task_args": {},
            },
        )
        assert response.status_code == 400
        assert "Unknown task" in response.json()["detail"]

    @patch("{{cookiecutter.project_name}}.routers.jobs.get_job_status")
    def test_get_job_status(self, mock_get_status, client, user_headers):
        """Get job status should return status info."""
        mock_get_status.return_value = {
            "job_id": "test-job-id",
            "status": "finished",
            "created_at": "2024-01-01T00:00:00",
        }

        response = client.get("/api/jobs/test-job-id/status", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-id"
        assert data["status"] == "finished"

    @patch("{{cookiecutter.project_name}}.routers.jobs.get_job_status")
    def test_get_job_status_not_found(self, mock_get_status, client, user_headers):
        """Get status for non-existent job should return 404."""
        mock_get_status.return_value = {
            "status": "not_found",
            "error": "Job not found",
        }

        response = client.get("/api/jobs/invalid-id/status", headers=user_headers)
        assert response.status_code == 404

    @patch("{{cookiecutter.project_name}}.routers.jobs.get_job_result")
    def test_get_job_result(self, mock_get_result, client, user_headers):
        """Get job result should return result data."""
        mock_get_result.return_value = {
            "job_id": "test-job-id",
            "status": "finished",
            "result": {"status": "success", "data": "processed"},
        }

        response = client.get("/api/jobs/test-job-id/result", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-id"
        assert data["result"]["status"] == "success"

    @patch("{{cookiecutter.project_name}}.routers.jobs.cancel_job")
    def test_cancel_job(self, mock_cancel, client, user_headers):
        """Cancel job should return cancellation status."""
        mock_cancel.return_value = {
            "job_id": "test-job-id",
            "success": True,
            "message": "Job cancelled successfully",
        }

        response = client.delete("/api/jobs/test-job-id", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_available_tasks(self, client, user_headers):
        """Get available tasks should list all registered tasks."""
        response = client.get("/api/jobs/tasks/available", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 3
        task_names = [task["name"] for task in data["tasks"]]
        assert "transform_data" in task_names
        assert "process_csv" in task_names
        assert "long_running_task" in task_names

    @patch("{{cookiecutter.project_name}}.routers.jobs.get_queue")
    def test_get_queue_stats(self, mock_get_queue, client, user_headers):
        """Get queue stats should return queue information."""
        mock_queue = MagicMock()
        mock_queue.__len__ = MagicMock(return_value=5)
        mock_queue.jobs = []
        mock_get_queue.return_value = mock_queue

        response = client.get("/api/jobs/queues/default/stats", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["queue_name"] == "default"
        assert data["job_count"] == 5
