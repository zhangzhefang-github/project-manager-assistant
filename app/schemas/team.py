from typing import List
from pydantic import BaseModel, Field
from .task import Task

class TeamMember(BaseModel):
    name: str = Field(description="Name of the team member")
    profile: str = Field(description="Profile of the team member")

class Team(BaseModel):
    team_members: List[TeamMember] = Field(description="List of team members")

class TaskAllocation(BaseModel):
    task: Task = Field(description="Task")
    team_member: TeamMember = Field(description="Team members assigned to the task") 