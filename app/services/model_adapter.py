"""
模型适配器服务
负责在简化的 AI 生成模型和完整的业务模型之间转换
实现关注点分离：AI 专注业务逻辑，适配器处理技术细节
"""
import uuid
from typing import Dict, List, Tuple
from loguru import logger

from app.schemas.simple import (
    SimpleTask, SimpleTaskList, SimpleDependency, SimpleDependencyList,
    SimpleTaskSchedule, SimpleSchedule, SimpleTaskAllocation, SimpleTaskAllocationList,
    SimpleRisk, SimpleRiskList
)
from app.schemas.task import Task, Dependency, TaskSchedule, Risk
from app.schemas.plan import TaskList, DependencyList, Schedule, RiskList, TaskAllocationList
from app.schemas.team import TaskAllocation, TeamMember

class ModelAdapter:
    """
    模型适配器：在简化模型和完整模型之间转换
    
    设计原则：
    - 单一职责：只负责数据转换
    - 无状态：不保存任何状态信息
    - 可测试：每个方法都可以独立测试
    """
    
    @staticmethod
    def simple_to_full_task_list(simple_tasks: SimpleTaskList) -> Tuple[TaskList, Dict[str, uuid.UUID]]:
        """
        将简化的任务列表转换为完整的任务列表
        
        Args:
            simple_tasks: AI 生成的简化任务列表
            
        Returns:
            Tuple[TaskList, Dict[str, uuid.UUID]]: (完整任务列表, ID映射字典)
        """
        tasks = []
        id_mapping = {}
        
        for simple_task in simple_tasks.tasks:
            task_uuid = uuid.uuid4()
            
            task = Task(
                id=task_uuid,
                task_name=simple_task.task_name,
                task_description=simple_task.task_description,
                estimated_day=simple_task.estimated_day
            )
            
            tasks.append(task)
            id_mapping[simple_task.id] = task_uuid
            
        logger.info(f"Converted {len(tasks)} simple tasks to full tasks with UUIDs")
        return TaskList(tasks=tasks), id_mapping
    
    @staticmethod
    def simple_to_full_dependencies(
        simple_deps: SimpleDependencyList, 
        id_mapping: Dict[str, uuid.UUID]
    ) -> DependencyList:
        """
        将简化的依赖关系转换为完整的依赖关系
        
        Args:
            simple_deps: AI 生成的简化依赖关系
            id_mapping: 简单ID到UUID的映射
            
        Returns:
            DependencyList: 完整的依赖关系列表
        """
        dependencies = []
        
        for simple_dep in simple_deps.dependencies:
            if simple_dep.source in id_mapping and simple_dep.target in id_mapping:
                dependency = Dependency(
                    source=id_mapping[simple_dep.source],
                    target=id_mapping[simple_dep.target]
                )
                dependencies.append(dependency)
            else:
                logger.warning(f"Missing ID mapping for dependency: {simple_dep.source} -> {simple_dep.target}")
        
        logger.info(f"Converted {len(dependencies)} simple dependencies to full dependencies")
        return DependencyList(dependencies=dependencies)
    
    @staticmethod
    def simple_to_full_schedule(
        simple_schedule: SimpleSchedule,
        id_mapping: Dict[str, uuid.UUID]
    ) -> Schedule:
        """
        将简化的调度转换为完整的调度
        
        Args:
            simple_schedule: AI 生成的简化调度
            id_mapping: 简单ID到UUID的映射
            
        Returns:
            Schedule: 完整的调度列表
        """
        schedules = []
        
        for simple_task_schedule in simple_schedule.schedule:
            if simple_task_schedule.task_id in id_mapping:
                task_schedule = TaskSchedule(
                    task_id=id_mapping[simple_task_schedule.task_id],
                    start_date=simple_task_schedule.start_date,
                    end_date=simple_task_schedule.end_date,
                    gantt_chart_format=simple_task_schedule.gantt_chart_format
                )
                schedules.append(task_schedule)
            else:
                logger.warning(f"Missing ID mapping for schedule task: {simple_task_schedule.task_id}")
        
        logger.info(f"Converted {len(schedules)} simple schedules to full schedules")
        return Schedule(schedule=schedules)
    
    @staticmethod
    def simple_to_full_task_allocations(
        simple_allocations: SimpleTaskAllocationList,
        tasks: TaskList,
        team_members: List[TeamMember],
        id_mapping: Dict[str, uuid.UUID]
    ) -> TaskAllocationList:
        """
        将简化的任务分配转换为完整的任务分配
        
        Args:
            simple_allocations: AI 生成的简化任务分配
            tasks: 完整的任务列表
            team_members: 团队成员列表
            id_mapping: 简单ID到UUID的映射
            
        Returns:
            TaskAllocationList: 完整的任务分配列表
        """
        allocations = []
        
        # 创建便于查找的映射
        task_by_uuid = {task.id: task for task in tasks.tasks}
        member_by_name = {member.name: member for member in team_members}
        
        for simple_allocation in simple_allocations.task_allocations:
            task_uuid = id_mapping.get(simple_allocation.task_id)
            
            if not task_uuid:
                logger.warning(f"Missing ID mapping for allocation task: {simple_allocation.task_id}")
                continue
                
            task = task_by_uuid.get(task_uuid)
            if not task:
                logger.warning(f"Task not found for UUID: {task_uuid}")
                continue
                
            team_member = member_by_name.get(simple_allocation.team_member_name)
            if not team_member:
                logger.warning(f"Team member not found: {simple_allocation.team_member_name}")
                continue
            
            allocation = TaskAllocation(
                task=task,
                team_member=team_member
            )
            allocations.append(allocation)
        
        logger.info(f"Converted {len(allocations)} simple allocations to full allocations")
        return TaskAllocationList(task_allocations=allocations)
    
    @staticmethod
    def simple_to_full_risks(
        simple_risks: SimpleRiskList,
        id_mapping: Dict[str, uuid.UUID] = None
    ) -> RiskList:
        """
        将简化的风险评估转换为完整的风险评估
        
        Args:
            simple_risks: AI 生成的简化风险列表
            id_mapping: 简单ID到UUID的映射（可选，因为Risk模型不包含task_id）
            
        Returns:
            RiskList: 完整的风险列表
        """
        risks = []
        
        for simple_risk in simple_risks.risks:
            risk = Risk(
                risk_name=simple_risk.risk_name,
                score=simple_risk.score
            )
            risks.append(risk)
        
        logger.info(f"Converted {len(risks)} simple risks to full risks")
        return RiskList(risks=risks)
    
    @staticmethod
    def get_simple_task_list_for_prompt(tasks: TaskList) -> List[Dict]:
        """
        将完整的任务列表转换为适合在 prompt 中使用的简化格式
        
        Args:
            tasks: 完整的任务列表
            
        Returns:
            List[Dict]: 简化的任务信息列表
        """
        simple_tasks = []
        for i, task in enumerate(tasks.tasks, 1):
            simple_tasks.append({
                "id": f"task-{i}",
                "task_name": task.task_name,
                "task_description": task.task_description,
                "estimated_day": task.estimated_day
            })
        
        return simple_tasks
    
    @staticmethod
    def get_simple_schedule_for_prompt(schedule: Schedule, reverse_mapping: Dict[uuid.UUID, str]) -> List[Dict]:
        """
        将完整的调度转换为适合在 prompt 中使用的简化格式
        
        Args:
            schedule: 完整的调度
            reverse_mapping: UUID到简单ID的映射
            
        Returns:
            List[Dict]: 简化的调度信息列表
        """
        simple_schedule = []
        for task_schedule in schedule.schedule:
            simple_id = reverse_mapping.get(task_schedule.task_id)
            if simple_id:
                simple_schedule.append({
                    "task_id": simple_id,
                    "start_date": task_schedule.start_date,
                    "end_date": task_schedule.end_date,
                    "gantt_chart_format": task_schedule.gantt_chart_format
                })
        
        return simple_schedule
    
    @staticmethod
    def create_reverse_id_mapping(id_mapping: Dict[str, uuid.UUID]) -> Dict[uuid.UUID, str]:
        """
        创建反向ID映射（UUID -> 简单ID）
        
        Args:
            id_mapping: 简单ID到UUID的映射
            
        Returns:
            Dict[uuid.UUID, str]: UUID到简单ID的映射
        """
        return {uuid_val: simple_id for simple_id, uuid_val in id_mapping.items()}

# 全局适配器实例
model_adapter = ModelAdapter() 