import pytest
from unittest.mock import MagicMock
import uuid

# Import schemas for type checking and mock data creation
from app.schemas.plan import TaskList, Schedule, TaskAllocationList, RiskList, DependencyList
from app.schemas.task import Task, TaskSchedule, Dependency, Risk
from app.schemas.team import TeamMember, TaskAllocation

# Import the entry point for the graph
from app.agent.graph import run_agent

@pytest.fixture
def mock_universal_llm():
    """
    A powerful mock LLM that returns different structured outputs
    based on the schema passed to `with_structured_output`.
    It also handles direct invokes for non-structured text generation.
    """
    # 1. Create all possible mock return objects
    mock_task = Task(id=uuid.uuid4(), task_name="Mock Task", task_description="A task from the universal mock.", estimated_day=3)
    mock_task_list = TaskList(tasks=[mock_task])

    mock_dependency_list = DependencyList(dependencies=[]) # Use Pydantic model

    mock_scheduled_task = TaskSchedule(task_id=mock_task.id, start_date="2024-01-01", end_date="2024-01-03", gantt_chart_format="...")
    mock_schedule = Schedule(schedule=[mock_scheduled_task])

    mock_team_member = TeamMember(name="Mock Developer", profile="A mock developer profile.")
    mock_task_allocation = TaskAllocation(task=mock_task, team_member=mock_team_member)
    mock_allocation_list = TaskAllocationList(task_allocations=[mock_task_allocation])

    mock_risk = Risk(risk_name="Mock Risk", score="5")
    mock_risk_list = RiskList(risks=[mock_risk])

    mock_insight_content = "This is a mock insight for the next iteration."
    
    # 2. Define the router logic
    def get_mock_output(schema_or_prompt):
        if schema_or_prompt == TaskList:
            return mock_task_list
        if schema_or_prompt == DependencyList: # Check for the correct list schema
            return mock_dependency_list
        if schema_or_prompt == Schedule:
            return mock_schedule
        if schema_or_prompt == TaskAllocationList:
            return mock_allocation_list
        if schema_or_prompt == RiskList:
            return mock_risk_list
        # For direct invoke (insights node)
        mock_insight_response = MagicMock()
        mock_insight_response.content = mock_insight_content
        return mock_insight_response

    # 3. Create the mock LLM instance with the router logic
    mock_llm = MagicMock()
    # The 'side_effect' allows the mock to return different values per call
    structured_output_mock = MagicMock()
    structured_output_mock.invoke.side_effect = lambda prompt: get_mock_output(structured_output_mock.schema)
    
    def with_structured_output_side_effect(schema):
        structured_output_mock.schema = schema
        return structured_output_mock

    mock_llm.with_structured_output.side_effect = with_structured_output_side_effect
    mock_llm.invoke.side_effect = lambda prompt: get_mock_output(prompt)

    return mock_llm

def test_agent_graph_full_run(mocker, mock_universal_llm):
    """
    Integration test for the full agent graph.
    Mocks all LLM calls and verifies the final state after one full loop.
    """
    # Arrange: Patch the LLM in all node modules
    nodes_to_patch = [
        "extract_tasks",
        "analyze_dependencies",
        "schedule_tasks",
        "allocate_team",
        "assess_risk",
        "generate_insights"
    ]
    for node_name in nodes_to_patch:
        try:
            mocker.patch(f'app.agent.nodes.{node_name}.llm', mock_universal_llm)
        except ModuleNotFoundError:
            # This allows the test to run even if a node file doesn't exist yet
            pass

    initial_state = {
        "project_description": "A test project for the full graph integration.",
        "team": [TeamMember(name="Mock Developer", profile="A mock developer profile.")],
        "max_iteration": 1, # Force the graph to stop after one loop
    }

    # Act
    final_state = run_agent(initial_state)

    # Assert: Check the final state for expected outputs from the mock LLM
    assert final_state is not None
    assert final_state.get("iteration_number") == 1
    
    # Verify outputs from each major step
    assert final_state.get("tasks") is not None
    assert final_state["tasks"].tasks[0].task_name == "Mock Task"

    assert final_state.get("schedule") is not None
    assert final_state["schedule"].schedule[0].task_id is not None

    assert final_state.get("task_allocations") is not None
    assert final_state["task_allocations"].task_allocations[0].team_member.name == "Mock Developer"

    assert final_state.get("risks") is not None
    assert final_state["risks"].risks[0].risk_name == "Mock Risk"

    # Since we set max_iteration=1, the router should END, not generate insights for a second loop
    assert final_state.get("insights") is None 