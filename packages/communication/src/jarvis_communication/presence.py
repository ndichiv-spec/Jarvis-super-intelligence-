from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import PresenceInfo, PresenceStatus


class PresenceService:
    def __init__(self) -> None:
        self._presence: dict[str, PresenceInfo] = {}

    async def set_presence(
        self,
        user_id: str,
        status: PresenceStatus,
        *,
        current_activity: str = "",
        connected_clients: int = 1,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> PresenceInfo:
        info = PresenceInfo(
            user_id=user_id,
            status=status,
            last_seen=datetime.now(UTC),
            current_activity=current_activity,
            connected_clients=connected_clients,
            metadata=metadata or {},
        )
        self._presence[user_id] = info
        return info

    async def get_presence(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> PresenceInfo | None:
        info = self._presence.get(user_id)
        if info is None:
            return None
        if info.status == PresenceStatus.ONLINE:
            if datetime.now(UTC) - (info.last_seen or datetime.now(UTC)) > timedelta(minutes=5):
                away = PresenceInfo(
                    user_id=info.user_id,
                    status=PresenceStatus.AWAY,
                    last_seen=info.last_seen,
                    current_activity=info.current_activity,
                    connected_clients=info.connected_clients,
                    metadata=info.metadata,
                )
                self._presence[user_id] = away
                return away
        return info

    async def set_online(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> PresenceInfo:
        return await self.set_presence(
            user_id,
            PresenceStatus.ONLINE,
            context=context,
        )

    async def set_away(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> PresenceInfo:
        return await self.set_presence(
            user_id,
            PresenceStatus.AWAY,
            current_activity="away",
            connected_clients=0,
            context=context,
        )

    async def set_busy(
        self,
        user_id: str,
        *,
        activity: str = "",
        context: ExecutionContext | None = None,
    ) -> PresenceInfo:
        return await self.set_presence(
            user_id,
            PresenceStatus.BUSY,
            current_activity=activity,
            context=context,
        )

    async def set_offline(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> PresenceInfo:
        return await self.set_presence(
            user_id,
            PresenceStatus.OFFLINE,
            current_activity="",
            connected_clients=0,
            context=context,
        )

    async def list_online(
        self,
        *,
        context: ExecutionContext | None = None,
    ) -> list[PresenceInfo]:
        return [
            info
            for info in self._presence.values()
            if info.status in (PresenceStatus.ONLINE, PresenceStatus.BUSY)
        ]

    async def list_all(
        self,
        *,
        context: ExecutionContext | None = None,
    ) -> list[PresenceInfo]:
        return list(self._presence.values())

    async def get_activity(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> str:
        info = self._presence.get(user_id)
        if info is None:
            return "unknown"
        return info.current_activity

    async def update_activity(
        self,
        user_id: str,
        activity: str,
        *,
        context: ExecutionContext | None = None,
    ) -> PresenceInfo | None:
        info = self._presence.get(user_id)
        if info is None:
            return None
        updated = PresenceInfo(
            user_id=info.user_id,
            status=info.status,
            last_seen=datetime.now(UTC),
            current_activity=activity,
            connected_clients=info.connected_clients,
            metadata=info.metadata,
        )
        self._presence[user_id] = updated
        return updated

    @property
    def online_count(self) -> int:
        return sum(
            1
            for info in self._presence.values()
            if info.status in (PresenceStatus.ONLINE, PresenceStatus.BUSY)
        )

    @property
    def total_users(self) -> int:
        return len(self._presence)
