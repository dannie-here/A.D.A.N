"""Health service module.

Handles system health status checks and diagnostic metadata reporting.
Encapsulates business logic away from HTTP routing.
"""

from datetime import datetime, timezone
from app.config import settings


class HealthService:
    """Service handling system health checks."""

    @staticmethod
    def get_health_status() -> dict:
        """Returns structured health status of the A.D.A.N. backend service."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "Phase 1 - Foundation",
        }
