from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from jarvis_ai.models import ProviderResponse, RuntimeRequest, TokenUsage, UnifiedResponse


def _freeze(value: Mapping[str, object] | None) -> Mapping[str, object]:
    return MappingProxyType(dict(value or {}))


class ResponseNormalizer:
    def normalize(
        self,
        response: ProviderResponse,
        request: RuntimeRequest,
        *,
        latency_ms: float,
        duration_ms: float,
        estimated_cost: float,
        metadata: Mapping[str, object] | None = None,
    ) -> UnifiedResponse:
        usage = response.usage or TokenUsage(prompt_tokens=0, completion_tokens=0)
        normalized_metadata = dict(response.metadata)
        normalized_metadata.update(metadata or {})
        return UnifiedResponse(
            text=response.text,
            capability=request.capability,
            provider_id=response.provider_id,
            model_id=response.model_id,
            finish_reason=response.finish_reason,
            usage=usage,
            latency_ms=latency_ms,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            metadata=_freeze(normalized_metadata),
        )
