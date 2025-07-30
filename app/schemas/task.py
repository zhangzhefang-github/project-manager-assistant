import uuid
from typing import List
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the task")
    task_name: str = Field(description="Name of the task")
    task_description: str = Field(description="Description of the task")
    estimated_day: int = Field(description="Estimated number of days to complete the task")

class Dependency(BaseModel):
    source: uuid.UUID = Field(description="The ID of the task that must be completed first")
    target: uuid.UUID = Field(description="The ID of the task that depends on the source task")

class TaskSchedule(BaseModel):
    task_id: uuid.UUID = Field(description="The ID of the task being scheduled")
    start_date: str = Field(description="Start date of the task in YYYY-MM-DD format")
    end_date: str = Field(description="End date of the task in YYYY-MM-DD format")
    gantt_chart_format: str = Field(description="Gantt chart format string, e.g., 'Task Name: 2024-01-01, 5d'")

class Risk(BaseModel):
    risk_name: str = Field(description="Name of the risk")
    score: str = Field(description="Risk associated with the task, a score from 0 to 10.") 