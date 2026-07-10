import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

from jarvis_api.gateway.sessions import SessionManager
from jarvis_api.gateway.streaming import StreamingEngine
from jarvis_api.gateway.types import Protocols


async def _source_stream() -> AsyncIterator[object]:
    yield {"chunk": 1}
    yield {"chunk": 2}


def test_streaming_engine_wraps_payloads_with_sequence_metadata() -> None:
    engine = StreamingEngine()

    async def _collect() -> list[dict[str, object]]:
        wrapped = engine.coordinate(_source_stream(), kind="token", channel_id="request-1")
        output: list[dict[str, object]] = []
        async for envelope in wrapped:
            output.append(envelope.to_event())
        return output

    events = asyncio.run(_collect())

    assert [event["sequence"] for event in events] == [1, 2]
    assert [event["payload"] for event in events] == [{"chunk": 1}, {"chunk": 2}]


def test_session_manager_lifecycle_and_expiry() -> None:
    manager = SessionManager(default_timeout=timedelta(seconds=1))

    session = manager.open_or_touch(
        session_id="session-1",
        identity_id="user-1",
        workspace_id="workspace-1",
        protocol=Protocols.REST,
        metadata={"client": "test"},
    )
    assert session.session_id == "session-1"
    assert manager.get("session-1") is not None

    manager.heartbeat("session-1")
    assert manager.get("session-1") is not None

    expired = manager.expire_stale(current_time=datetime.now(tz=UTC) + timedelta(seconds=2))
    assert expired == ("session-1",)
    assert manager.get("session-1") is None
