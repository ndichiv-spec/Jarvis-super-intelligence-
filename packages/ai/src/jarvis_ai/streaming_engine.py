from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from jarvis_ai.interfaces import ProviderAdapter
from jarvis_ai.models import ProviderRequest, StreamEvent, StreamEventType


@dataclass(slots=True)
class CancellationToken:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self.cancelled


class StreamingEngine:
    async def stream(
        self,
        provider: ProviderAdapter,
        request: ProviderRequest,
        cancellation_token: CancellationToken | None = None,
    ) -> AsyncIterator[StreamEvent]:
        partial = ""
        try:
            async for chunk in provider.stream(request):
                if cancellation_token is not None and cancellation_token.is_cancelled:
                    yield StreamEvent.create(
                        event_type=StreamEventType.CANCELLED,
                        text=partial,
                        provider_id=provider.metadata.provider_id,
                        model_id=request.model_id,
                    )
                    return

                if chunk.text:
                    partial += chunk.text
                    yield StreamEvent.create(
                        event_type=StreamEventType.TOKEN,
                        text=chunk.text,
                        provider_id=chunk.provider_id,
                        model_id=chunk.model_id,
                        metadata=chunk.metadata,
                    )
                    yield StreamEvent.create(
                        event_type=StreamEventType.PARTIAL,
                        text=partial,
                        provider_id=chunk.provider_id,
                        model_id=chunk.model_id,
                    )

            yield StreamEvent.create(
                event_type=StreamEventType.COMPLETED,
                text=partial,
                provider_id=provider.metadata.provider_id,
                model_id=request.model_id,
            )
        except Exception as exc:
            yield StreamEvent.create(
                event_type=StreamEventType.ERROR,
                text=str(exc),
                provider_id=provider.metadata.provider_id,
                model_id=request.model_id,
            )
            raise
