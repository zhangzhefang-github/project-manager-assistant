from fastapi import FastAPI
from app.api.routers import plan, health
from app.core.logging import setup_logging

app = FastAPI(
    title="Project Manager Assistant API",
    description="API for an AI agent that assists in project management.",
    version="1.0.0"
)

# Setup logging
setup_logging()

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(plan.router, prefix="/v1", tags=["Project Plan"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Project Manager Assistant API"} 