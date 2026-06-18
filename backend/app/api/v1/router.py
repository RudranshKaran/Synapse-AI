"""API v1 router — aggregates all v1 route modules."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.debates import router as debates_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["health"])
api_v1_router.include_router(debates_router, prefix="/debates", tags=["debates"])
