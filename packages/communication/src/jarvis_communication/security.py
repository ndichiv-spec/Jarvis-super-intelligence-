from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from jarvis_communication.context import ExecutionContext, SecurityContext
from jarvis_communication.models import (
    Channel,
    ChannelType,
    CommunicationMessage,
    Conversation,
    NotificationLevel,
)


PermissionCheck = Callable[[str, str, str], bool]


class SecurityService:
    def __init__(self) -> None:
        self._permission_checks: dict[str, PermissionCheck] = {}
        self._rate_limits: dict[str, list[datetime]] = {}
        self._max_requests_per_minute: int = 60

    def set_rate_limit(self, max_requests: int) -> None:
        self._max_requests_per_minute = max_requests

    def register_permission_check(
        self,
        permission: str,
        check: PermissionCheck,
    ) -> None:
        self._permission_checks[permission] = check

    async def check_permission(
        self,
        user_id: str,
        permission: str,
        resource: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        check = self._permission_checks.get(permission)
        if check is None:
            return True
        return check(user_id, permission, resource)

    async def check_rate_limit(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        now = datetime.now(UTC)
        user_requests = self._rate_limits.setdefault(user_id, [])
        cutoff = now - timedelta(minutes=1)
        user_requests[:] = [t for t in user_requests if t > cutoff]
        if len(user_requests) >= self._max_requests_per_minute:
            return False
        user_requests.append(now)
        return True

    async def validate_message_access(
        self,
        user_id: str,
        message: CommunicationMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        if user_id == message.sender or user_id == message.receiver:
            return True
        return False

    async def validate_channel_access(
        self,
        user_id: str,
        channel: Channel,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        if channel.channel_type == ChannelType.SYSTEM:
            return False
        if user_id in channel.members:
            return True
        return False

    async def validate_conversation_access(
        self,
        user_id: str,
        conversation: Conversation,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        return user_id in conversation.participants

    async def encrypt_payload(
        self,
        payload: str,
        *,
        context: ExecutionContext | None = None,
    ) -> str:
        return f"encrypted:{payload}"

    async def decrypt_payload(
        self,
        payload: str,
        *,
        context: ExecutionContext | None = None,
    ) -> str:
        if payload.startswith("encrypted:"):
            return payload[10:]
        return payload

    async def get_rate_limit_status(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        user_requests = self._rate_limits.get(user_id, [])
        cutoff = now - timedelta(minutes=1)
        recent = [t for t in user_requests if t > cutoff]
        return {
            "current": len(recent),
            "limit": self._max_requests_per_minute,
            "remaining": max(0, self._max_requests_per_minute - len(recent)),
        }
