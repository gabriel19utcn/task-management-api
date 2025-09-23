"""
API v1 module initialization.
Imports and exposes all v1 endpoints.
"""

from .router import v1_router

__all__ = ["v1_router"]