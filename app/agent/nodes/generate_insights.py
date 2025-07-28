from app.agent.state import AgentState
from app.services.llm_service import llm
from app.prompts.loader import get_prompt
from loguru import logger

def insight_generation_node(state: AgentState) -> dict:
    """LangGraph node that generate insights from the schedule, task allocation, and risk associated."""
    logger.info("Executing insight_generation_node...")
    prompt = get_prompt(
        "insight_generator",
        task_allocations=state["task_allocations"],
        schedule=state["schedule"],
        risks=state["risks"]
    )
    
    insights = llm.invoke(prompt).content
    logger.info("Generated new insights for improvement.")
    return {"insights": insights} 