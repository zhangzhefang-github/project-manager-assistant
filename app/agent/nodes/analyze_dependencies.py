from app.agent.state import AgentState
from app.schemas.plan import DependencyList
from app.services.llm_service import llm
from app.prompts.loader import get_prompt
from loguru import logger

def task_dependency_node(state: AgentState) -> dict:
    """Evaluate the dependencies between the tasks."""
    logger.info("Executing task_dependency_node...")
    prompt = get_prompt("task_dependency", tasks=state["tasks"])
    
    structured_llm = llm.with_structured_output(DependencyList)
    dependencies: DependencyList = structured_llm.invoke(prompt)
    
    logger.info(f"Identified {len(dependencies.dependencies)} dependency sets.")
    return {"dependencies": dependencies} 