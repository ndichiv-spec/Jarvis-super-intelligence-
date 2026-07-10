from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Channel, ChannelType


class ChannelManager:
    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}

    async def create(
        self,
        name: str,
        channel_type: ChannelType = ChannelType.INTERNAL,
        *,
        members: tuple[str, ...] = (),
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> Channel:
        channel = Channel(
            name=name,
            channel_type=channel_type,
            members=members,
            metadata=metadata or {},
        )
        self._channels[channel.channel_id] = channel
        return channel

    async def get(
        self,
        channel_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Channel | None:
        return self._channels.get(channel_id)

    async def list(
        self,
        *,
        channel_type: ChannelType | None = None,
        context: ExecutionContext | None = None,
    ) -> list[Channel]:
        channels = list(self._channels.values())
        if channel_type:
            channels = [c for c in channels if c.channel_type == channel_type]
        channels.sort(key=lambda c: c.created_at, reverse=True)
        return channels

    async def list_by_member(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Channel]:
        return [
            c for c in self._channels.values()
            if user_id in c.members and c.is_active
        ]

    async def add_member(
        self,
        channel_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Channel | None:
        channel = self._channels.get(channel_id)
        if channel is None:
            return None
        if user_id in channel.members:
            return channel
        new_members = (*channel.members, user_id)
        updated = Channel(
            channel_id=channel.channel_id,
            name=channel.name,
            channel_type=channel.channel_type,
            created_at=channel.created_at,
            members=new_members,
            metadata=channel.metadata,
            is_active=channel.is_active,
        )
        self._channels[channel_id] = updated
        return updated

    async def remove_member(
        self,
        channel_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Channel | None:
        channel = self._channels.get(channel_id)
        if channel is None or user_id not in channel.members:
            return None
        new_members = tuple(m for m in channel.members if m != user_id)
        updated = Channel(
            channel_id=channel.channel_id,
            name=channel.name,
            channel_type=channel.channel_type,
            created_at=channel.created_at,
            members=new_members,
            metadata=channel.metadata,
            is_active=channel.is_active,
        )
        self._channels[channel_id] = updated
        return updated

    async def deactivate(
        self,
        channel_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        channel = self._channels.get(channel_id)
        if channel is None:
            return False
        updated = Channel(
            channel_id=channel.channel_id,
            name=channel.name,
            channel_type=channel.channel_type,
            created_at=channel.created_at,
            members=channel.members,
            metadata=channel.metadata,
            is_active=False,
        )
        self._channels[channel_id] = updated
        return True

    async def search(
        self,
        query: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Channel]:
        query_lower = query.lower()
        return [
            c for c in self._channels.values()
            if query_lower in c.name.lower()
        ]
