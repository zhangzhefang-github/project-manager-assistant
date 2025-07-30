from app.agent.state import AgentState
from app.schemas.simple import SimpleRiskList
from app.services.llm_service import llm
from app.services.model_adapter import model_adapter
from app.prompts.loader import get_prompt
from loguru import logger

def risk_assessment_node(state: AgentState) -> dict:
    """
    风险评估节点
    
    采用适配器模式（保持架构一致性）：
    1. 将完整的任务分配和调度信息转换为简化格式传递给AI
    2. AI 使用简化的 schema 生成风险评估
    3. 适配器将简化的风险评估转换为完整格式
    4. 保持迭代状态的处理逻辑
    """
    logger.info("Executing risk_assessment_node with adapter pattern...")
    
    # Step 1: 准备简化格式的数据（为了架构一致性，虽然Risk模型本身不包含task_id）
    # 由于任务分配和调度可能包含复杂的对象结构，我们可以将其传递给prompt的时候简化
    
    # Step 2: AI 使用简化的 schema 生成风险评估（Risk模型相对简单）
    prompt = get_prompt(
        "risk_assessor",
        task_allocations=state["task_allocations"],  # 保持原样，因为prompt需要完整信息
        schedule=state["schedule"],  # 保持原样，因为prompt需要完整信息
        risks_iteration=state.get("risks_iteration", [])
    )
    
    structure_llm = llm.with_structured_output(SimpleRiskList)
    simple_risks: SimpleRiskList = structure_llm.invoke(prompt)
    
    logger.info(f"AI generated {len(simple_risks.risks)} simple risks")
    
    # Step 3: 通过适配器转换为完整的风险评估
    risks = model_adapter.simple_to_full_risks(simple_risks)
    
    logger.info(f"Adapter converted to {len(risks.risks)} full risks")
    
    # Step 4: 保持原有的风险评分逻辑
    project_task_risk_scores = [int(risk.score) for risk in risks.risks]
    project_risk_score = sum(project_task_risk_scores)
    
    logger.info(f"Assessed project risk. Current Score: {project_risk_score}")
    
    # Step 5: 保持迭代状态的处理逻辑
    iteration = state.get("iteration_number", 0) + 1
    new_risk_scores = state.get("project_risk_score_iterations", []) + [project_risk_score]
    new_risks_iteration = state.get("risks_iteration", []) + [risks]

    return {
        "risks": risks,
        "iteration_number": iteration,
        "project_risk_score_iterations": new_risk_scores,
        "risks_iteration": new_risks_iteration
    } 