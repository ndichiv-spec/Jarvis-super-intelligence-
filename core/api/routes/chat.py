"""
Chat Endpoints.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from infrastructure.logsys.structured import get_logger

logger = get_logger(__name__)
router = APIRouter()


class Message(BaseModel):
    """Chat message model."""
    content: str
    session_id: str = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(message: Message):
    """Send a chat message."""
    return ChatResponse(
        response="Response placeholder - AI integration coming soon",
        session_id=message.session_id or "default",
    )
