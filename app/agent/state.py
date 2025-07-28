from typing import List, TypedDict
from app.schemas.team import Team, TaskAllocationList
from app.schemas.plan import TaskList, DependencyList, Schedule, RiskList, RiskListIteration

class AgentState(TypedDict):
    """The project manager agent state."""
    project_description: str
    team: Team
    tasks: TaskList
    dependencies: DependencyList
    schedule: Schedule
    task_allocations: TaskAllocationList
    risks: RiskList
    iteration_number: int
    max_iteration: int
    insights: str  # Changed to single string for simplicity in passing
    schedule_iteration: List[Schedule]
    task_allocations_iteration: List[TaskAllocationList]
    risks_iteration: List[RiskList] # Corrected TypeHint
    project_risk_score_iterations: List[int] 