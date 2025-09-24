from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import v1_router  # Versioned API only
from app.core.config import get_settings
from app.exceptions import InvalidTaskStatusError, TaskError, TaskNotFoundError
from app.utils.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    description="Task Management API",
    version="1.0.0",
    lifespan=lifespan,
)


# Exception handlers
@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    """Handle task not found exceptions."""
    return JSONResponse(
        status_code=404, content={"detail": exc.message, "task_id": exc.task_id}
    )


@app.exception_handler(InvalidTaskStatusError)
async def invalid_task_status_handler(request: Request, exc: InvalidTaskStatusError):
    """Handle invalid task status exceptions."""
    return JSONResponse(
        status_code=400, content={"detail": exc.message, "task_id": exc.task_id}
    )


@app.exception_handler(TaskError)
async def task_error_handler(request: Request, exc: TaskError):
    """Handle general task exceptions."""
    return JSONResponse(
        status_code=400, content={"detail": exc.message, "task_id": exc.task_id}
    )


# Include versioned API router
app.include_router(v1_router)


@app.get("/")
async def root():
    """Get API information and available endpoints."""
    logger.debug("Root endpoint accessed")

    return {
        "app": settings.app_name,
        "message": "Task Scheduler API v1",
        "version": "1.0.0",
        "api_version": "v1",
        "base_url": "/api/v1",
        "endpoints": {
            "docs": "/docs",
            "tasks": "/api/v1/tasks",
            "health": "/api/v1/health",
        },
    }
