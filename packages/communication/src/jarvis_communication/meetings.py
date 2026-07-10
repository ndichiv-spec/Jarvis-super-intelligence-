from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Meeting, MeetingStatus


class MeetingManager:
    def __init__(self) -> None:
        self._meetings: dict[str, Meeting] = {}

    async def schedule(
        self,
        title: str,
        organizer: str,
        participants: tuple[str, ...],
        scheduled_at: datetime | None = None,
        *,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> Meeting:
        meeting = Meeting(
            title=title,
            organizer=organizer,
            participants=participants,
            status=MeetingStatus.SCHEDULED,
            scheduled_at=scheduled_at,
            metadata=metadata or {},
        )
        self._meetings[meeting.meeting_id] = meeting
        return meeting

    async def get(
        self,
        meeting_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Meeting | None:
        return self._meetings.get(meeting_id)

    async def start(
        self,
        meeting_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Meeting | None:
        meeting = self._meetings.get(meeting_id)
        if meeting is None:
            return None
        updated = Meeting(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            organizer=meeting.organizer,
            participants=meeting.participants,
            status=MeetingStatus.ACTIVE,
            scheduled_at=meeting.scheduled_at,
            started_at=datetime.now(UTC),
            ended_at=None,
            metadata=meeting.metadata,
            transcript=meeting.transcript,
            summary=meeting.summary,
        )
        self._meetings[meeting_id] = updated
        return updated

    async def end(
        self,
        meeting_id: str,
        *,
        summary: str = "",
        context: ExecutionContext | None = None,
    ) -> Meeting | None:
        meeting = self._meetings.get(meeting_id)
        if meeting is None:
            return None
        updated = Meeting(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            organizer=meeting.organizer,
            participants=meeting.participants,
            status=MeetingStatus.ENDED,
            scheduled_at=meeting.scheduled_at,
            started_at=meeting.started_at,
            ended_at=datetime.now(UTC),
            metadata=meeting.metadata,
            transcript=meeting.transcript,
            summary=summary or meeting.summary,
        )
        self._meetings[meeting_id] = updated
        return updated

    async def cancel(
        self,
        meeting_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        meeting = self._meetings.get(meeting_id)
        if meeting is None:
            return False
        updated = Meeting(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            organizer=meeting.organizer,
            participants=meeting.participants,
            status=MeetingStatus.CANCELLED,
            scheduled_at=meeting.scheduled_at,
            started_at=None,
            ended_at=None,
            metadata=meeting.metadata,
            transcript=meeting.transcript,
            summary=meeting.summary,
        )
        self._meetings[meeting_id] = updated
        return True

    async def list_by_participant(
        self,
        user_id: str,
        *,
        status: MeetingStatus | None = None,
        context: ExecutionContext | None = None,
    ) -> list[Meeting]:
        meetings = [
            m
            for m in self._meetings.values()
            if user_id in m.participants or user_id == m.organizer
        ]
        if status:
            meetings = [m for m in meetings if m.status == status]
        meetings.sort(key=lambda m: m.scheduled_at or datetime.min.replace(tzinfo=UTC))
        return meetings

    async def add_participant(
        self,
        meeting_id: str,
        user_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Meeting | None:
        meeting = self._meetings.get(meeting_id)
        if meeting is None or user_id in meeting.participants:
            return meeting
        new_participants = (*meeting.participants, user_id)
        updated = Meeting(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            organizer=meeting.organizer,
            participants=new_participants,
            status=meeting.status,
            scheduled_at=meeting.scheduled_at,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            metadata=meeting.metadata,
            transcript=meeting.transcript,
            summary=meeting.summary,
        )
        self._meetings[meeting_id] = updated
        return updated

    async def update_transcript(
        self,
        meeting_id: str,
        transcript: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Meeting | None:
        meeting = self._meetings.get(meeting_id)
        if meeting is None:
            return None
        updated = Meeting(
            meeting_id=meeting.meeting_id,
            title=meeting.title,
            organizer=meeting.organizer,
            participants=meeting.participants,
            status=meeting.status,
            scheduled_at=meeting.scheduled_at,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            metadata=meeting.metadata,
            transcript=transcript,
            summary=meeting.summary,
        )
        self._meetings[meeting_id] = updated
        return updated

    @property
    def total_meetings(self) -> int:
        return len(self._meetings)
