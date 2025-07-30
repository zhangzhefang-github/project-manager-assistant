from app.agent.state import AgentState
from app.schemas.simple import SimpleDependencyList
from app.services.llm_service import llm
from app.services.model_adapter import model_adapter
from app.prompts.loader import get_prompt
from loguru import logger

def task_dependency_node(state: AgentState) -> dict:
    """
    依赖关系分析节点
    
    采用适配器模式：
    1. 将完整任务转换为简化格式传递给AI
    2. AI 使用简化的 schema 分析依赖关系
    3. 适配器将简化的依赖关系转换为完整格式
    """
    logger.info("Executing task_dependency_node with adapter pattern...")
    
    # Step 1: 将完整任务转换为简化格式，供AI使用
    simple_tasks = model_adapter.get_simple_task_list_for_prompt(state["tasks"])
    
    # Step 2: AI 使用简化的任务信息分析依赖关系
    prompt = get_prompt("task_dependency", tasks=simple_tasks)
    structured_llm = llm.with_structured_output(SimpleDependencyList)
    simple_dependencies: SimpleDependencyList = structured_llm.invoke(prompt)
    
    logger.info(f"AI generated {len(simple_dependencies.dependencies)} simple dependencies")
    
    # Step 3: 通过适配器转换为完整的依赖关系（包含UUID）
    dependencies = model_adapter.simple_to_full_dependencies(
        simple_dependencies, 
        state["id_mapping"]
    )
    
    logger.info(f"Adapter converted to {len(dependencies.dependencies)} dependencies with UUIDs")
    
    return {"dependencies": dependencies} 