from typing import List
from pydantic import BaseModel, Field
from .task import Task, Dependency, TaskSchedule, Risk
from .team import TaskAllocation

class TaskList(BaseModel):
    tasks: List[Task] = Field(description="List of tasks")

class DependencyList(BaseModel):
    dependencies: List[Dependency] = Field(description="List of task dependencies")

class Schedule(BaseModel):
    schedule: List[TaskSchedule] = Field(description="List of task schedules")

class TaskAllocationList(BaseModel):
    task_allocations: List[TaskAllocation] = Field(description="List of task allocations")

class RiskList(BaseModel):
    risks: List[Risk] = Field(description="List of risks")

# For iterative results storage
class RiskListIteration(BaseModel):
    risks_iteration: List[RiskList] = Field(description="List of risks for each iteration") 