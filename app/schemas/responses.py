"""
API 响应模型定义
"""
from pydantic import BaseModel

class JobResponse(BaseModel):
    """作业响应模型"""
    job_id: str
    status: str 