from app.agent.state import AgentState
from app.schemas.plan import RiskList
from app.services.llm_service import llm
from app.prompts.loader import get_prompt
from loguru import logger

def risk_assessment_node(state: AgentState) -> dict:
    """LangGraph node that analyse risk associated with schedule and allocation of task."""
    logger.info("Executing risk_assessment_node...")
    prompt = get_prompt(
        "risk_assessor",
        task_allocations=state["task_allocations"],
        schedule=state["schedule"],
        risks_iteration=state["risks_iteration"]
    )
    
    structure_llm = llm.with_structured_output(RiskList)
    risks: RiskList = structure_llm.invoke(prompt)
    
    project_task_risk_scores = [int(risk.score) for risk in risks.risks]
    project_risk_score = sum(project_task_risk_scores)
    
    logger.info(f"Assessed project risk. Current Score: {project_risk_score}")
    
    # Update state
    state["risks"] = risks
    state["iteration_number"] += 1
    state["project_risk_score_iterations"].append(project_risk_score)
    state["risks_iteration"].append(risks)
    
    return {
        "risks": risks,
        "iteration_number": state["iteration_number"],
        "project_risk_score_iterations": state["project_risk_score_iterations"],
        "risks_iteration": state["risks_iteration"]
    } 