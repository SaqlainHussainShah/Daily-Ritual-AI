"""
routes package
---------------
Defines all API routes and endpoints for the Daily Ritual AI backend.

This package integrates different services such as location detection,
weather retrieval, and AI-based food recommendations.

Example:
    from routes.api import router
"""

from .recommend import router

__all__ = ["router"]
