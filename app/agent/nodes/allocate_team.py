from app.agent.state import AgentState
from app.schemas.plan import TaskAllocationList
from app.services.llm_service import llm
from app.prompts.loader import get_prompt
from loguru import logger

def task_allocation_node(state: AgentState) -> dict:
    """LangGraph node that will allocate tasks to team members."""
    logger.info("Executing task_allocation_node...")
    prompt = get_prompt(
        "task_allocator",
        tasks=state["tasks"],
        schedule=state["schedule"],
        team=state["team"],
        insights=state["insights"],
        task_allocations_iteration=state["task_allocations_iteration"]
    )
    
    structure_llm = llm.with_structured_output(TaskAllocationList)
    task_allocations: TaskAllocationList = structure_llm.invoke(prompt)
    
    # Append to iteration list
    state["task_allocations_iteration"].append(task_allocations)
    
    logger.info("Allocated tasks to team members.")
    return {"task_allocations": task_allocations, "task_allocations_iteration": state["task_allocations_iteration"]} 