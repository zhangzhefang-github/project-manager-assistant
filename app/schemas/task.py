import uuid
from typing import List
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the task")
    task_name: str = Field(description="Name of the task")
    task_description: str = Field(description="Description of the task")
    estimated_day: int = Field(description="Estimated number of days to complete the task")

class TaskDependency(BaseModel):
    task: Task = Field(description="Task")
    dependent_tasks: List[Task] = Field(description="List of dependent tasks")

class TaskSchedule(BaseModel):
    task: Task = Field(description="Task")
    start_day: int = Field(description="Start day of the task")
    end_day: int = Field(description="End day of the task")

class Risk(BaseModel):
    task: Task = Field(description="Task")
    score: str = Field(description="Risk associated with the task, a score from 0 to 10.") 