from app.agent.state import AgentState
from app.schemas.simple import SimpleSchedule
from app.services.llm_service import llm
from app.services.model_adapter import model_adapter
from app.prompts.loader import get_prompt
from loguru import logger

def task_scheduler_node(state: AgentState) -> dict:
    """
    任务调度节点
    
    采用适配器模式：
    1. 将完整的任务和依赖关系转换为简化格式传递给AI
    2. AI 使用简化的 schema 生成调度
    3. 适配器将简化的调度转换为完整格式
    4. 保持迭代状态的处理逻辑
    """
    logger.info("Executing task_scheduler_node with adapter pattern...")
    
    # Step 1: 将完整数据转换为简化格式，供AI使用
    simple_tasks = model_adapter.get_simple_task_list_for_prompt(state["tasks"])
    
    # 处理依赖关系：将UUID转换为简化ID
    simple_dependencies = []
    if state["dependencies"]:
        reverse_mapping = model_adapter.create_reverse_id_mapping(state["id_mapping"])
        for dep in state["dependencies"].dependencies:
            source_simple_id = reverse_mapping.get(dep.source)
            target_simple_id = reverse_mapping.get(dep.target)
            if source_simple_id and target_simple_id:
                simple_dependencies.append({
                    "source": source_simple_id,
                    "target": target_simple_id
                })
    
    # Step 2: AI 使用简化的数据生成调度
    prompt = get_prompt(
        "task_scheduler",
        tasks=simple_tasks,
        dependencies=simple_dependencies,
        insights=state.get("insights"), 
        schedule_iteration=state.get("schedule_iteration", [])
    )
    
    schedule_llm = llm.with_structured_output(SimpleSchedule)
    simple_schedule: SimpleSchedule = schedule_llm.invoke(prompt)
    
    logger.info(f"AI generated schedule for {len(simple_schedule.schedule)} tasks")
    
    # Step 3: 通过适配器转换为完整的调度（包含UUID）
    schedule = model_adapter.simple_to_full_schedule(simple_schedule, state["id_mapping"])
    
    logger.info(f"Adapter converted to schedule with {len(schedule.schedule)} tasks with UUIDs")
    
    # Step 4: 保持迭代状态的处理逻辑
    new_schedule_iteration = state.get("schedule_iteration", []) + [schedule]
    
    logger.info("Generated a new task schedule.")
    return {"schedule": schedule, "schedule_iteration": new_schedule_iteration} 