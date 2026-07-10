from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from jarvis_ai.models import ProviderMetadata, ProviderRequest, ProviderResponse


class ProviderAdapter(Protocol):
    @property
    def metadata(self) -> ProviderMetadata: ...

    async def supports_model(self, model_id: str) -> bool: ...

    async def invoke(self, request: ProviderRequest) -> ProviderResponse: ...

    def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]: ...
