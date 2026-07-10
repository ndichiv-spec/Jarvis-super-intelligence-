from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Session, SessionStatus


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    async def create(
        self,
        user_id: str,
        *,
        client_info: str = "",
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> Session:
        session = Session(
            user_id=user_id,
            client_info=client_info,
            metadata=metadata or {},
        )
        self._sessions[session.session_id] = session
        return session

    async def get(
        self,
        session_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Session | None:
        return self._sessions.get(session_id)

    async def list_by_user(
        self,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Session]:
        return [
            s for s in self._sessions.values()
            if s.user_id == user_id
        ]

    async def update_activity(
        self,
        session_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Session | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        updated = Session(
            session_id=session.session_id,
            user_id=session.user_id,
            status=SessionStatus.ACTIVE,
            started_at=session.started_at,
            last_activity_at=datetime.now(UTC),
            metadata=session.metadata,
            client_info=session.client_info,
        )
        self._sessions[session_id] = updated
        return updated

    async def set_status(
        self,
        session_id: str,
        status: SessionStatus,
        *,
        context: ExecutionContext | None = None,
    ) -> Session | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        updated = Session(
            session_id=session.session_id,
            user_id=session.user_id,
            status=status,
            started_at=session.started_at,
            last_activity_at=datetime.now(UTC),
            metadata=session.metadata,
            client_info=session.client_info,
        )
        self._sessions[session_id] = updated
        return updated

    async def close(
        self,
        session_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        session = self._sessions.get(session_id)
        if session is None:
            return False
        updated = Session(
            session_id=session.session_id,
            user_id=session.user_id,
            status=SessionStatus.CLOSED,
            started_at=session.started_at,
            last_activity_at=datetime.now(UTC),
            metadata=session.metadata,
            client_info=session.client_info,
        )
        self._sessions[session_id] = updated
        return True

    async def list_active(
        self,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Session]:
        return [
            s for s in self._sessions.values()
            if s.status == SessionStatus.ACTIVE
        ]

    async def cleanup_stale(
        self,
        max_idle: timedelta = timedelta(minutes=30),
        *,
        context: ExecutionContext | None = None,
    ) -> int:
        now = datetime.now(UTC)
        stale_count = 0
        for session_id, session in list(self._sessions.items()):
            if now - session.last_activity_at > max_idle:
                updated = Session(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    status=SessionStatus.CLOSED,
                    started_at=session.started_at,
                    last_activity_at=session.last_activity_at,
                    metadata=session.metadata,
                    client_info=session.client_info,
                )
                self._sessions[session_id] = updated
                stale_count += 1
        return stale_count

    @property
    def total_sessions(self) -> int:
        return len(self._sessions)

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if s.status == SessionStatus.ACTIVE)
