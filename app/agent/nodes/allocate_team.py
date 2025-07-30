from app.agent.state import AgentState
from app.schemas.simple import SimpleTaskAllocationList
from app.services.llm_service import llm
from app.services.model_adapter import model_adapter
from app.prompts.loader import get_prompt
from loguru import logger

def task_allocation_node(state: AgentState) -> dict:
    """
    任务分配节点
    
    采用适配器模式：
    1. 将完整的任务、调度和团队信息转换为简化格式传递给AI
    2. AI 使用简化的 schema 生成任务分配
    3. 适配器将简化的任务分配转换为完整格式
    4. 保持迭代状态的处理逻辑
    """
    logger.info("Executing task_allocation_node with adapter pattern...")
    
    # Step 1: 将完整数据转换为简化格式，供AI使用
    simple_tasks = model_adapter.get_simple_task_list_for_prompt(state["tasks"])
    
    # 将调度转换为简化格式
    reverse_mapping = model_adapter.create_reverse_id_mapping(state["id_mapping"])
    simple_schedule = model_adapter.get_simple_schedule_for_prompt(state["schedule"], reverse_mapping)
    
    # Step 2: AI 使用简化的数据生成任务分配
    prompt = get_prompt(
        "task_allocator",
        tasks=simple_tasks,
        schedule=simple_schedule,
        team=state["team"]["team_members"] if isinstance(state["team"], dict) else state["team"].team_members,  # 兼容字典和对象
        insights=state.get("insights"),
        task_allocations_iteration=state.get("task_allocations_iteration", [])
    )
    
    structure_llm = llm.with_structured_output(SimpleTaskAllocationList)
    simple_allocations: SimpleTaskAllocationList = structure_llm.invoke(prompt)
    
    logger.info(f"AI generated {len(simple_allocations.task_allocations)} simple allocations")
    
    # Step 3: 通过适配器转换为完整的任务分配（包含完整的Task和TeamMember对象）
    task_allocations = model_adapter.simple_to_full_task_allocations(
        simple_allocations,
        state["tasks"],
        state["team"]["team_members"] if isinstance(state["team"], dict) else state["team"].team_members,
        state["id_mapping"]
    )
    
    logger.info(f"Adapter converted to {len(task_allocations.task_allocations)} full allocations")
    
    # Step 4: 保持迭代状态的处理逻辑
    new_allocations_iteration = state.get("task_allocations_iteration", []) + [task_allocations]
    
    logger.info("Allocated tasks to team members.")
    return {"task_allocations": task_allocations, "task_allocations_iteration": new_allocations_iteration} 