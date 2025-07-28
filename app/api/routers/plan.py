from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import pandas as pd
from io import StringIO

from app.schemas.team import Team, TeamMember
from app.services.task_queue import task_queue
from app.agent.graph import run_agent  # We will use this via RQ

router = APIRouter()

class PlanRequest(BaseModel):
    project_description: str
    team_members: list[dict]

class JobResponse(BaseModel):
    job_id: str
    status: str

@router.post("/plans", response_model=JobResponse, status_code=202)
async def create_plan(
    project_description: str = Form(...),
    team_file: UploadFile = File(...)
):
    """
    Accepts project description and a team CSV file to generate a project plan.
    This endpoint is asynchronous and returns a job ID.
    """
    try:
        # Read and parse the team CSV
        contents = await team_file.read()
        team_df = pd.read_csv(StringIO(contents.decode('utf-8')))
        team_members = [
            TeamMember(name=row['Name'], profile=row['Profile Description'])
            for _, row in team_df.iterrows()
        ]
        team = Team(team_members=team_members)
        
        # Define the initial state for the agent
        initial_state = {
            "project_description": project_description,
            "team": team,
            "insights": "",
            "iteration_number": 0,
            "max_iteration": 3,
            "schedule_iteration": [],
            "task_allocations_iteration": [],
            "risks_iteration": [],
            "project_risk_score_iterations": []
        }
        
        # Enqueue the agent execution task
        job = task_queue.enqueue(run_agent, initial_state, job_timeout=600)
        
        return {"job_id": job.id, "status": "queued"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plans/{job_id}", status_code=200)
async def get_plan_result(job_id: str):
    """
    Fetches the result of a plan generation job.
    """
    job = task_queue.fetch_job(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.is_finished:
        return {"job_id": job.id, "status": "finished", "result": job.result}
    elif job.is_failed:
        return {"job_id": job.id, "status": "failed"}
    else:
        return {"job_id": job.id, "status": "in_progress"} 