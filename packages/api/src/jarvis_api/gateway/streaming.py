from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator, Mapping
from datetime import UTC, datetime
from typing import Any

from jarvis_api.gateway.types import StreamEnvelope


class StreamingEngine:
    def coordinate(
        self,
        stream: AsyncIterable[object],
        *,
        kind: str,
        channel_id: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> AsyncIterator[StreamEnvelope]:
        async def _iterator() -> AsyncIterator[StreamEnvelope]:
            sequence = 0
            async for payload in stream:
                sequence += 1
                yield StreamEnvelope(
                    sequence=sequence,
                    channel_id=channel_id,
                    kind=kind,
                    timestamp=datetime.now(tz=UTC),
                    payload=payload,
                    metadata=metadata or {},
                )

        return _iterator()
