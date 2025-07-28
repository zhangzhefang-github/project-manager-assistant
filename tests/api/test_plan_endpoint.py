import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock

from app.api.main import app

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_task_queue():
    """Fixture to mock the task queue."""
    mock_job = MagicMock()
    mock_job.id = "mock_job_123"

    mock_queue = MagicMock()
    mock_queue.enqueue.return_value = mock_job
    return mock_queue

async def test_create_plan_endpoint(mocker, mock_task_queue):
    """
    Tests the POST /v1/plans endpoint to ensure it correctly
    handles file uploads and enqueues a job.
    """
    # Arrange
    # Patch the global `task_queue` instance in the task_queue service
    mocker.patch('app.services.task_queue.task_queue', mock_task_queue)

    # Mock file content
    team_csv_content = "Name,Profile Description\nAlice,Developer"
    files = {
        "team_file": ("team.csv", team_csv_content, "text/csv")
    }
    data = {
        "project_description": "Test project description"
    }

    # Act
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/v1/plans", data=data, files=files)

    # Assert
    assert response.status_code == 202  # Accepted
    
    # Check that enqueue was called once
    mock_task_queue.enqueue.assert_called_once()
    
    # Check the response body
    response_data = response.json()
    assert response_data["job_id"] == "mock_job_123"
    assert response_data["status"] == "queued" 