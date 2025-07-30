from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routers import plan, health
from app.core.logging import setup_logging
from loguru import logger

app = FastAPI(
    title="Project Manager Assistant API",
    description="API for an AI agent that assists in project management.",
    version="1.0.0"
)

# --- Middleware for Global Exception Handling ---
@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    """
    Catches any unhandled exceptions that occur during request processing
    and logs the full traceback before returning a 500 response.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"An unhandled exception occurred during request to {request.url.path}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )

# Setup logging
setup_logging()

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(plan.router, prefix="/v1", tags=["Project Plan"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Project Manager Assistant API"} 