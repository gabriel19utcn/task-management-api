"""
API v1 router that combines all v1 endpoints.
"""

from fastapi import APIRouter

from .health import router as health_router
from .tasks import router as tasks_router

# Create the main v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include all v1 sub-routers
v1_router.include_router(tasks_router)
v1_router.include_router(health_router)

__all__ = ["v1_router"]
