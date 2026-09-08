"""
Health Check Endpoints.
"""

from fastapi import APIRouter, status
from infrastructure.logsys.structured import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "JARVIS"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness check endpoint."""
    return {"status": "ready", "message": "Service is ready"}


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive", "message": "Service is running"}
