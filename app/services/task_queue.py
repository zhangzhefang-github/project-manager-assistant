from redis import Redis
from rq import Queue
from rq.job import Job
from typing import Optional, Dict, Any
import time
import json

from app.core.config import settings

# Global Redis connection and RQ Queue
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
task_queue = Queue(connection=redis_conn)

def update_job_progress(job_id: str, agent_state: Dict[str, Any]) -> bool:
    """
    更新任务的实时进度信息到job.meta
    
    Args:
        job_id: 任务ID
        agent_state: AgentState字典，包含真实的执行状态
        
    Returns:
        更新是否成功
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if job is None:
            return False
        
        # === 计算真实的进度百分比 ===
        completed_nodes = agent_state.get("completed_nodes", [])
        current_node = agent_state.get("current_node")
        
        # 定义所有LangGraph节点（必须与实际执行顺序一致）
        all_nodes = [
            "task_generation",     # 任务生成
            "analyze_dependencies", # 依赖分析  
            "schedule_tasks",      # 任务调度
            "allocate_team",       # 团队分配
            "assess_risk",         # 风险评估
            "generate_insights"    # 洞察生成
        ]
        
        # 计算进度百分比
        if agent_state.get("overall_status") == "completed":
            progress = 100
        elif not completed_nodes and not current_node:
            progress = 0
        else:
            # 基于完成的节点数量计算进度
            completed_count = len([node for node in completed_nodes if node in all_nodes])
            
            # 如果当前节点正在执行且不在已完成列表中，给它50%的权重
            if current_node and current_node in all_nodes and current_node not in completed_nodes:
                current_node_progress = 0.5  # 正在执行的节点算50%完成
            else:
                current_node_progress = 0
                
            # 计算总进度 = (已完成节点数 + 当前节点进度) / 总节点数 * 100
            total_progress = (completed_count + current_node_progress) / len(all_nodes)
            progress = min(int(total_progress * 100), 95)  # 最多95%，100%留给真正完成
        
        # === 生成用户友好的显示信息 ===
        node_display_map = {
            "task_generation": "🧠 智能任务提取",
            "analyze_dependencies": "🔗 依赖关系分析", 
            "schedule_tasks": "📅 智能任务调度",
            "allocate_team": "👥 团队智能分配",
            "assess_risk": "⚠️ 风险评估分析",
            "generate_insights": "✨ 方案优化洞察"
        }
        
        current_node_display = node_display_map.get(current_node, current_node) if current_node else "处理中"
        
        # 提取关键的状态信息（避免存储过多数据）
        progress_info = {
            "current_node": current_node,
            "current_node_display": current_node_display,
            "node_start_time": agent_state.get("node_start_time"),
            "total_start_time": agent_state.get("total_start_time"),
            "completed_nodes": completed_nodes,
            "node_progress": agent_state.get("node_progress", {}),
            "overall_status": agent_state.get("overall_status", "unknown"),
            "iteration_number": agent_state.get("iteration_number", 1),
            "last_updated": time.time(),
            
            # === 新增：真实进度信息 ===
            "progress": progress,  # 真实进度百分比
            "total_nodes": len(all_nodes),  # 总节点数
            "completed_count": len(completed_nodes),  # 已完成节点数
            "langgraph_flow": True,  # 标记这是真实的LangGraph流程
            
            # 计算执行时间
            "total_elapsed_time": int(time.time() - agent_state.get("total_start_time", time.time())) if agent_state.get("total_start_time") else 0,
            
            # 节点详细信息
            "node_details": f"正在执行: {current_node_display}" if current_node else "准备中...",
            
            # 迭代信息（如果有多轮迭代）
            "iteration_info": f"第 {agent_state.get('iteration_number', 1)} 轮迭代" if agent_state.get("iteration_number", 1) > 1 else ""
        }
        
        # 更新job.meta
        if not hasattr(job, 'meta') or job.meta is None:
            job.meta = {}
        
        job.meta["agent_state"] = progress_info
        job.save_meta()
        
        return True
        
    except Exception as e:
        print(f"Failed to update job progress: {e}")
        return False

def get_job_agent_state(job_id: str) -> Optional[Dict[str, Any]]:
    """
    获取任务的AgentState信息
    
    Args:
        job_id: 任务ID
        
    Returns:
        AgentState信息字典，如果不存在则返回None
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if job is None or not hasattr(job, 'meta') or job.meta is None:
            return None
            
        return job.meta.get("agent_state")
        
    except Exception as e:
        print(f"Failed to get job agent state: {e}")
        return None

def get_job_detailed_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    获取任务的详细状态信息
    
    Args:
        job_id: 任务ID
        
    Returns:
        包含详细状态信息的字典，如果任务不存在则返回None
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        if job is None:
            return None
        
        # 构建详细状态信息
        status_info = {
            "job_id": job.id,
            "status": "queued" if job.is_queued else 
                     "started" if job.is_started else
                     "finished" if job.is_finished else
                     "failed" if job.is_failed else "unknown",
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "function_name": job.func_name if hasattr(job, 'func_name') else None,
            "description": job.description if hasattr(job, 'description') else None,
            "timeout": job.timeout if hasattr(job, 'timeout') else None,
        }
        
        # 添加队列位置信息
        if job.is_queued:
            status_info["position"] = job.get_position()
            
        # 添加进度信息（基于时间估算）
        if job.is_started and job.started_at:
            elapsed_time = time.time() - job.started_at.timestamp()
            status_info["elapsed_time"] = elapsed_time
            
        # 添加错误信息
        if job.is_failed:
            status_info["error"] = str(job.exc_info) if hasattr(job, 'exc_info') else "Unknown error"
            
        # 添加结果信息
        if job.is_finished and hasattr(job, 'result'):
            status_info["has_result"] = True
            # 不直接返回结果以避免数据过大，通过专门的端点获取
            
        return status_info
        
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "error",
            "error": f"Failed to fetch job status: {str(e)}"
        }

def get_queue_info() -> Dict[str, Any]:
    """
    获取队列的整体信息
    
    Returns:
        包含队列统计信息的字典
    """
    try:
        return {
            "queue_length": len(task_queue),
            "started_jobs": len(task_queue.started_job_registry),
            "finished_jobs": len(task_queue.finished_job_registry),
            "failed_jobs": len(task_queue.failed_job_registry),
            "deferred_jobs": len(task_queue.deferred_job_registry),
            "scheduled_jobs": len(task_queue.scheduled_job_registry),
        }
    except Exception:
        return {"error": "Failed to get queue info"} 