import os
import time
from typing import Literal
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes.extract_tasks import task_generation_node
from app.agent.nodes.analyze_dependencies import task_dependency_node
from app.agent.nodes.schedule_tasks import task_scheduler_node
from app.agent.nodes.allocate_team import task_allocation_node
from app.agent.nodes.assess_risk import risk_assessment_node
from app.agent.nodes.generate_insights import insight_generation_node
from loguru import logger

def router(state: AgentState) -> str:
    """Router to decide the next node based on the current state"""
    logger.info(f"Router check: Iteration {state['iteration_number']}/{state['max_iteration']}")
    
    current_score = state.get('project_risk_score_iterations', [])
    
    if state['iteration_number'] >= state['max_iteration']:
        logger.info("Maximum iterations reached. Ending.")
        return END
    
    if len(current_score) > 1:
        # Check if risk score improved
        if current_score[-1] < current_score[-2]:
            logger.info("Risk improved. Ending optimization loop.")
            return END
        else:
            logger.info("Risk did not improve. Generating insights for next loop.")
            return "insight_generator"
    else:
        logger.info("First iteration completed. Moving to insight generation.")
        return "insight_generator"

def create_graph():
    """Create the agent graph with enhanced state tracking"""
    workflow = StateGraph(AgentState)
    
    # 定义增强版节点包装器
    def create_tracked_node(node_func, node_name: str, description: str):
        def tracked_node(state: AgentState) -> dict:
            job_id = state.get("job_id")
            
            # 标记节点开始
            state["current_node"] = node_name
            if "node_progress" not in state:
                state["node_progress"] = {}
            
            state["node_progress"][node_name] = {
                "status": "started",
                "start_time": time.time(),
                "description": description,
                "details": f"正在执行{description}..."
            }
            
            # 更新到Redis
            if job_id:
                from app.services.task_queue import update_job_progress
                update_job_progress(job_id, state)
            
            logger.info(f"🎯 开始执行节点: {node_name} - {description}")
            
            try:
                # 执行实际节点
                result = node_func(state)
                
                # 标记节点完成
                state["node_progress"][node_name].update({
                    "status": "completed",
                    "end_time": time.time(),
                    "details": f"✅ {description}已完成"
                })
                
                # 添加到已完成节点列表
                if "completed_nodes" not in state:
                    state["completed_nodes"] = []
                if node_name not in state["completed_nodes"]:
                    state["completed_nodes"].append(node_name)
                
                # 更新整体状态
                state.update(result)
                
                # 再次更新到Redis
                if job_id:
                    update_job_progress(job_id, state)
                
                logger.info(f"✅ 节点完成: {node_name}")
                return result
                
            except Exception as e:
                state["node_progress"][node_name].update({
                    "status": "failed",
                    "end_time": time.time(),
                    "details": f"❌ {description}执行失败: {str(e)}"
                })
                logger.error(f"❌ 节点执行失败: {node_name} - {e}")
                raise
                
        return tracked_node
    
    # 添加增强版节点
    workflow.add_node("task_generation", create_tracked_node(task_generation_node, "task_generation", "智能任务提取"))
    workflow.add_node("analyze_dependencies", create_tracked_node(task_dependency_node, "analyze_dependencies", "依赖关系分析"))
    workflow.add_node("schedule_tasks", create_tracked_node(task_scheduler_node, "schedule_tasks", "智能任务调度"))
    workflow.add_node("allocate_team", create_tracked_node(task_allocation_node, "allocate_team", "团队智能分配"))
    workflow.add_node("assess_risk", create_tracked_node(risk_assessment_node, "assess_risk", "风险评估分析"))
    workflow.add_node("insight_generator", create_tracked_node(insight_generation_node, "generate_insights", "洞察生成优化"))
    
    # Define edges
    workflow.set_entry_point("task_generation")
    workflow.add_edge("task_generation", "analyze_dependencies")
    workflow.add_edge("analyze_dependencies", "schedule_tasks")
    workflow.add_edge("schedule_tasks", "allocate_team")
    workflow.add_edge("allocate_team", "assess_risk")
    workflow.add_conditional_edges("assess_risk", router)
    workflow.add_edge("insight_generator", "schedule_tasks")
    
    # Compile the graph
    graph = workflow.compile()
    return graph

# Create the graph
agent_graph = create_graph()

def run_agent_with_job_tracking(initial_state: dict):
    """
    包装器函数：获取RQ真实job_id并启动智能体
    """
    # 获取当前RQ job的真实ID
    from rq import get_current_job
    current_job = get_current_job()
    
    if current_job:
        job_id = current_job.id
        logger.info(f"🚀 Starting agent with RQ job ID: {job_id}")
    else:
        # 如果不在RQ环境中运行，生成临时ID
        import uuid
        job_id = str(uuid.uuid4())
        logger.info(f"🚀 Starting agent with temp ID (not in RQ): {job_id}")
    
    try:
        return run_agent(initial_state, job_id)
    except Exception as e:
        logger.error(f"❌ Agent job {job_id} failed: {e}")
        raise

def run_agent(initial_state: dict, job_id: str = None):
    """
    主要智能体执行入口点
    
    Args:
        initial_state: 初始状态字典
        job_id: RQ任务ID，用于实时进度追踪
    """
    config = {"configurable": {"thread_id": "1"}}
    
    # 初始化追踪字段
    if job_id:
        initial_state.update({
            "job_id": job_id,
            "overall_status": "starting",
            "total_start_time": time.time(),
            "completed_nodes": [],
            "node_progress": {},
            "current_node": None
        })
    
    logger.info(f"🚀 开始智能体执行，任务ID: {job_id}")
    
    # 执行图形流，保存最终状态
    final_state = None
    for event in agent_graph.stream(initial_state, config, stream_mode="values"):
        logger.info(f"📊 智能体状态更新: 当前节点={event.get('current_node', 'unknown')}")
        final_state = event  # 保存最后一个事件作为最终状态
    
    # 确保有最终状态
    if final_state is None:
        final_state = initial_state
    
    # 标记任务完成
    if job_id:
        from app.services.task_queue import update_job_progress
        # 更新完成状态
        final_state["overall_status"] = "completed"
        final_state["current_node"] = "completed"
        final_state["total_end_time"] = time.time()
        if "total_start_time" in final_state:
            final_state["total_elapsed_time"] = final_state["total_end_time"] - final_state["total_start_time"]
        update_job_progress(job_id, final_state)
        logger.info(f"✅ 智能体执行完成，任务ID: {job_id}")
    
    # 返回最终状态
    return final_state 