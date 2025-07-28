from app.agent.state import AgentState
from app.schemas.plan import TaskList
from app.services.llm_service import llm
from app.prompts.loader import get_prompt
from loguru import logger

def task_generation_node(state: AgentState) -> dict:
    """LangGraph node that will extract tasks from given project description."""
    logger.info("Executing task_generation_node...")
    prompt = get_prompt("task_generation", description=state["project_description"])
    
    structured_llm = llm.with_structured_output(TaskList)
    tasks: TaskList = structured_llm.invoke(prompt)
    
    logger.info(f"Generated {len(tasks.tasks)} tasks.")
    return {"tasks": tasks} 