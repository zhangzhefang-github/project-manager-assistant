"""
简化的数据模型，专门用于 AI 生成
这些模型使用简单的字符串 ID，避免让 AI 处理复杂的 UUID 格式
"""
from typing import List
from pydantic import BaseModel, Field

class SimpleTask(BaseModel):
    """简化的任务模型，供 AI 生成使用"""
    id: str = Field(description="Simple task identifier (e.g., 'task-1', 'task-2')")
    task_name: str = Field(description="Name of the task")
    task_description: str = Field(description="Description of the task")
    estimated_day: int = Field(description="Estimated number of days to complete the task")

class SimpleTaskList(BaseModel):
    """简化的任务列表模型"""
    tasks: List[SimpleTask] = Field(description="List of tasks")

class SimpleDependency(BaseModel):
    """简化的依赖关系模型"""
    source: str = Field(description="The ID of the task that must be completed first")
    target: str = Field(description="The ID of the task that depends on the source task")

class SimpleDependencyList(BaseModel):
    """简化的依赖关系列表"""
    dependencies: List[SimpleDependency] = Field(description="List of task dependencies")

class SimpleTaskSchedule(BaseModel):
    """简化的任务调度模型"""
    task_id: str = Field(description="The ID of the task being scheduled")
    start_date: str = Field(description="Start date of the task in YYYY-MM-DD format")
    end_date: str = Field(description="End date of the task in YYYY-MM-DD format")
    gantt_chart_format: str = Field(description="Gantt chart format string, e.g., 'Task Name: 2024-01-01, 5d'")

class SimpleSchedule(BaseModel):
    """简化的调度列表"""
    schedule: List[SimpleTaskSchedule] = Field(description="List of task schedules")

class SimpleTaskAllocation(BaseModel):
    """简化的任务分配模型"""
    task_id: str = Field(description="The ID of the task being allocated")
    team_member_name: str = Field(description="Name of the team member assigned to the task")

class SimpleTaskAllocationList(BaseModel):
    """简化的任务分配列表"""
    task_allocations: List[SimpleTaskAllocation] = Field(description="List of task allocations")

class SimpleRisk(BaseModel):
    """简化的风险模型（匹配现有的Risk schema，不包含task_id）"""
    risk_name: str = Field(description="Name of the risk")
    score: str = Field(description="Risk associated with the task, a score from 0 to 10.")

class SimpleRiskList(BaseModel):
    """简化的风险列表"""
    risks: List[SimpleRisk] = Field(description="List of risks") 