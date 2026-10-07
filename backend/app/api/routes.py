"""API routes for A.D.A.N. backend."""

from fastapi import APIRouter
from app.services.health_service import HealthService

router = APIRouter()


@router.get("/health", tags=["System"])
def health_check() -> dict:
    """System health check endpoint.

    Returns the application status, current environment, and version.
    """
    return HealthService.get_health_status()
