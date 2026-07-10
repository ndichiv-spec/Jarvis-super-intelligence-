from __future__ import annotations

import pytest

from jarvis_communication.context import ExecutionContext
from jarvis_communication.meetings import MeetingManager
from jarvis_communication.models import MeetingStatus


@pytest.fixture
def manager() -> MeetingManager:
    return MeetingManager()


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext.new(source="test")


@pytest.mark.asyncio
async def test_schedule_and_get(manager: MeetingManager, context: ExecutionContext) -> None:
    meeting = await manager.schedule("Sprint Review", "user-1", ("user-2", "user-3"), context=context)
    retrieved = await manager.get(meeting.meeting_id, context=context)
    assert retrieved is not None
    assert retrieved.title == "Sprint Review"
    assert retrieved.organizer == "user-1"
    assert retrieved.status == MeetingStatus.SCHEDULED


@pytest.mark.asyncio
async def test_start_and_end(manager: MeetingManager, context: ExecutionContext) -> None:
    meeting = await manager.schedule("Standup", "user-1", ("user-2",), context=context)
    started = await manager.start(meeting.meeting_id, context=context)
    assert started is not None
    assert started.status == MeetingStatus.ACTIVE
    assert started.started_at is not None
    ended = await manager.end(meeting.meeting_id, summary="Done", context=context)
    assert ended is not None
    assert ended.status == MeetingStatus.ENDED
    assert ended.summary == "Done"


@pytest.mark.asyncio
async def test_cancel(manager: MeetingManager, context: ExecutionContext) -> None:
    meeting = await manager.schedule("Cancel meeting", "user-1", ("user-2",), context=context)
    assert await manager.cancel(meeting.meeting_id, context=context) is True
    cancelled = await manager.get(meeting.meeting_id, context=context)
    assert cancelled is not None
    assert cancelled.status == MeetingStatus.CANCELLED


@pytest.mark.asyncio
async def test_list_by_participant(manager: MeetingManager, context: ExecutionContext) -> None:
    await manager.schedule("Meeting A", "user-1", ("user-2",), context=context)
    await manager.schedule("Meeting B", "user-2", ("user-3",), context=context)
    user2_meetings = await manager.list_by_participant("user-2", context=context)
    assert len(user2_meetings) == 2


@pytest.mark.asyncio
async def test_add_participant(manager: MeetingManager, context: ExecutionContext) -> None:
    meeting = await manager.schedule("Team Sync", "user-1", ("user-2",), context=context)
    updated = await manager.add_participant(meeting.meeting_id, "user-3", context=context)
    assert updated is not None
    assert "user-3" in updated.participants


@pytest.mark.asyncio
async def test_update_transcript(manager: MeetingManager, context: ExecutionContext) -> None:
    meeting = await manager.schedule("Record", "user-1", ("user-2",), context=context)
    await manager.start(meeting.meeting_id, context=context)
    updated = await manager.update_transcript(meeting.meeting_id, "Full transcript here", context=context)
    assert updated is not None
    assert updated.transcript == "Full transcript here"
