from typing import List, TypedDict, Dict, Optional
import uuid
from app.schemas.team import Team
from app.schemas.plan import TaskList, DependencyList, Schedule, RiskList, RiskListIteration, TaskAllocationList

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
    # 适配器模式新增字段
    id_mapping: Optional[Dict[str, uuid.UUID]]  # 简单ID到UUID的映射，支持适配器模式
    
    # === 新增：实时进度追踪字段 ===
    job_id: Optional[str]  # RQ任务ID，用于更新进度
    current_node: Optional[str]  # 当前执行的节点名称
    node_start_time: Optional[float]  # 当前节点开始时间
    total_start_time: Optional[float]  # 整个流程开始时间
    completed_nodes: List[str]  # 已完成的节点列表
    node_progress: Dict[str, dict]  # 每个节点的详细进度信息
    overall_status: str  # 整体状态：starting, processing, iterating, completed, failed 