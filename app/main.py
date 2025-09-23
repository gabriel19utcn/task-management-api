from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import v1_router  # Versioned API only
from app.core.config import get_settings
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
    lifespan=lifespan
)

# Include versioned API router
app.include_router(v1_router)


@app.get("/")
async def root():
    """Root endpoint with basic application information."""
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
            "health": "/api/v1/health"
        }
    }
