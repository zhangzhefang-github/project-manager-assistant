import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.api.main import app

# Create a single TestClient instance for all tests in this module
client = TestClient(app)

# NOTE: Switched to synchronous testing due to persistent issues with the
# async test runner configuration in the current environment.
# This approach still validates the core API logic effectively.

@pytest.fixture
def mock_task_queue():
    """Fixture to mock the task queue."""
    mock_job = MagicMock()
    mock_job.id = "mock_job_123"

    mock_queue = MagicMock()
    mock_queue.enqueue.return_value = mock_job
    return mock_queue

def test_create_plan_endpoint(mocker, mock_task_queue):
    """
    Tests the POST /v1/plans endpoint to ensure it correctly
    handles file uploads and enqueues a job.
    """
    # Arrange
    # Patch the `task_queue` object *where it is used*, inside the `plan` router module.
    mocker.patch('app.api.routers.plan.task_queue', mock_task_queue)

    # Mock file content
    team_csv_content = "Name,Profile Description\nAlice,Developer"
    files = {
        "team_file": ("team.csv", team_csv_content, "text/csv")
    }
    data = {
        "project_description": "Test project description"
    }

    # Act
    response = client.post("/v1/plans", data=data, files=files)

    # Assert
    assert response.status_code == 202  # Accepted
    
    mock_task_queue.enqueue.assert_called_once()
    
    response_data = response.json()
    assert response_data["job_id"] == "mock_job_123"
    assert response_data["status"] == "queued"


@pytest.mark.parametrize(
    "job_status, mock_job_properties, expected_status_code, expected_response_status",
    [
        (
            "finished",
            {"is_finished": True, "is_failed": False, "result": {"data": "some_result"}},
            200,
            "finished",
        ),
        (
            "failed",
            {"is_finished": True, "is_failed": True, "result": None},
            200,
            "failed",
        ),
        (
            "in_progress",
            {"is_finished": False, "is_failed": False, "result": None},
            200,
            "in_progress",
        ),
        ("not_found", None, 404, "Job not found"),
    ],
)
def test_get_plan_result_endpoint(
    mocker,
    mock_task_queue,
    job_status,
    mock_job_properties,
    expected_status_code,
    expected_response_status,
):
    """
    Tests the GET /v1/plans/{job_id} endpoint for various job statuses.
    """
    # Arrange
    job_id = "test_job_123"

    if job_status == "not_found":
        mock_task_queue.fetch_job.return_value = None
    else:
        mock_job = MagicMock(**mock_job_properties)
        # The mock job must also have an 'id' attribute to match the real object
        mock_job.id = job_id
        mock_task_queue.fetch_job.return_value = mock_job
    
    # Patch the `task_queue` object *where it is used*, inside the `plan` router module.
    mocker.patch('app.api.routers.plan.task_queue', mock_task_queue)

    # Act
    response = client.get(f"/v1/plans/{job_id}")

    # Assert
    assert response.status_code == expected_status_code
    response_data = response.json()

    if expected_status_code == 200:
        assert response_data["job_id"] == job_id
        assert response_data["status"] == expected_response_status
        if job_status == "finished":
            assert response_data["result"] == mock_job_properties["result"]
    else:
        assert expected_response_status in response_data["detail"] 