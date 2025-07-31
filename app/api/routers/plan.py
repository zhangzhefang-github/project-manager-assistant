from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from io import StringIO
import pandas as pd
import json
import asyncio
import time
from typing import AsyncGenerator

from app.services.task_queue import task_queue
from app.agent.graph import run_agent_with_job_tracking
from app.schemas.responses import JobResponse
from app.schemas.team import TeamMember, Team

router = APIRouter()

@router.get("/plans/status/{job_id}")
async def get_plan_status(job_id: str):
    """
    Returns the status of a plan generation job.
    """
    job = task_queue.fetch_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # 获取详细状态信息
    status_info = {
        "job_id": job.id,
        "status": "queued" if job.is_queued else 
                 "started" if job.is_started else
                 "finished" if job.is_finished else
                 "failed" if job.is_failed else "unknown",
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        "position": job.get_position() if job.is_queued else None,
        "progress": 0
    }
    
    # 如果任务已开始，计算基于时间的进度估算
    if job.is_started and job.started_at:
        elapsed_time = (time.time() - job.started_at.timestamp())
        # 假设总任务时间为35秒（基于EXECUTION_PHASES）
        estimated_total_time = 35
        progress = min(int((elapsed_time / estimated_total_time) * 100), 95)
        status_info["progress"] = progress
        status_info["elapsed_time"] = int(elapsed_time)
        status_info["estimated_remaining"] = max(0, estimated_total_time - elapsed_time)
    elif job.is_finished:
        status_info["progress"] = 100
    
    return status_info

@router.get("/plans/{job_id}/stream")
async def stream_plan_progress(job_id: str):
    """
    SSE端点：实时推送任务进度更新
    直接使用task_queue.py中计算的真实进度数据
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        """生成SSE事件流 - 直接使用真实的LangGraph状态"""
        last_status = None
        connection_start = time.time()
        
        try:
            while True:
                job = task_queue.fetch_job(job_id)
                
                if job is None:
                    yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
                    break
                
                # === 直接使用task_queue.py中已计算的真实进度 ===
                current_status = {
                    "job_id": job.id,
                    "status": "queued" if job.is_queued else 
                             "started" if job.is_started else
                             "finished" if job.is_finished else
                             "failed" if job.is_failed else "unknown",
                    "timestamp": time.time(),
                    "connection_duration": time.time() - connection_start
                }
                
                # 获取task_queue.py中计算的完整agent_state
                if hasattr(job, 'meta') and job.meta and 'agent_state' in job.meta:
                    # 直接使用已经计算好的真实状态数据
                    agent_state = job.meta['agent_state']
                    current_status.update(agent_state)
                    
                    # 确保langgraph_flow标记存在（前端用来判断显示模式）
                    if 'langgraph_flow' not in current_status:
                        current_status['langgraph_flow'] = True
                else:
                    # 只有在完全无数据时才回退到简单模式
                    if job.is_started and job.started_at:
                        elapsed_time = time.time() - job.started_at.timestamp()
                        current_status.update({
                            "progress": min(int((elapsed_time / 35) * 100), 95),
                            "elapsed_time": int(elapsed_time),
                            "current_node": "unknown",
                            "current_node_display": "正在处理...",
                            "node_details": "正在处理中...",
                            "langgraph_flow": False  # 标记为简单模式
                        })
                    elif job.is_finished:
                        current_status.update({
                            "progress": 100,
                            "current_node": "completed",
                            "current_node_display": "🎉 处理完成",
                            "langgraph_flow": False
                        })
                    elif job.is_failed:
                        current_status.update({
                            "error": str(job.exc_info) if hasattr(job, 'exc_info') else "Unknown error",
                            "current_node": "failed",
                            "current_node_display": "❌ 处理失败",
                            "langgraph_flow": False
                        })
                    else:
                        current_status.update({
                            "progress": 0,
                            "current_node": "queued",
                            "current_node_display": "等待处理",
                            "langgraph_flow": False,
                            "position": job.get_position() if job.is_queued else None
                        })
                
                # 只在状态变化时发送更新
                if current_status != last_status:
                    yield f"event: progress\ndata: {json.dumps(current_status)}\n\n"
                    last_status = current_status.copy()
                
                # 任务完成或失败时结束流
                if job.is_finished or job.is_failed:
                    yield f"event: complete\ndata: {json.dumps(current_status)}\n\n"
                    break
                
                # 每500ms检查一次状态
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            yield f"event: disconnect\ndata: {json.dumps({'message': 'Connection closed'})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "Access-Control-Allow-Methods": "GET"
        }
    )


@router.post("/plans", response_model=JobResponse)
async def create_plan(
    project_description: str = Form(...),
    team_file: UploadFile = File(...)
):
    """
    Creates a new project plan based on the provided project description and team file.
    """
    try:
        # 读取并解析团队CSV文件
        content = await team_file.read()
        csv_data = StringIO(content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        # 验证CSV格式
        required_columns = ['name', 'profile']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV file must contain columns: {required_columns}"
            )
        
        # 创建团队成员对象
        team_members = []
        for _, row in df.iterrows():
            team_members.append(TeamMember(
                name=str(row['name']),
                profile=str(row['profile'])
            ))
        
        team = Team(team_members=team_members)
        
        # 准备初始状态
        initial_state = {
            "project_description": project_description,
            "team": team,
            "tasks": None,
            "dependencies": None,
            "schedule": None,
            "task_allocations": None,
            "risks": None,
            "iteration_number": 0,
            "max_iteration": 1,
            "insights": "",
            "schedule_iteration": [],
            "task_allocations_iteration": [],
            "risks_iteration": [],
            "project_risk_score_iterations": [],
            "id_mapping": {}
        }
        
        # 提交到队列
        job = task_queue.enqueue(run_agent_with_job_tracking, initial_state)
        
        return JobResponse(
            job_id=job.id,
            status="queued"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans/{job_id}")
async def get_plan(job_id: str):
    """
    Returns the result of a completed plan generation job.
    """
    job = task_queue.fetch_job(job_id)
    
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.is_finished:
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not completed yet. Current status: {'queued' if job.is_queued else 'started' if job.is_started else 'failed' if job.is_failed else 'unknown'}"
        )
    
    if job.result is None:
        raise HTTPException(status_code=500, detail="Job completed but no result available")
    
    return job.result 