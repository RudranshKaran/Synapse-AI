"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return service health status.

    Used by Docker orchestration and monitoring to verify
    the application is running and responsive.
    """
    return {"status": "healthy"}
