"""
System Status Endpoints.
"""

from fastapi import APIRouter, status
from infrastructure.logsys.structured import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/system/status", status_code=status.HTTP_200_OK)
async def system_status():
    """Get system status."""
    return {"status": "operational", "components": {}}


@router.get("/system/info", status_code=status.HTTP_200_OK)
async def system_info():
    """Get system information."""
    return {
        "name": "JARVIS Super Intelligence Platform",
        "version": "0.2.0",
        "environment": "development",
    }
