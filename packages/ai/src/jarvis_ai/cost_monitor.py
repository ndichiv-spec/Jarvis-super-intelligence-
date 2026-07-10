from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from jarvis_ai.models import ModelMetadata, TokenUsage, UnifiedResponse


@dataclass(slots=True)
class ProviderStats:
    provider_id: str
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost: float = 0.0
    total_duration_ms: float = 0.0
    total_latency_ms: float = 0.0


@dataclass(slots=True)
class ModelStats:
    model_id: str
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost: float = 0.0
    total_duration_ms: float = 0.0
    total_latency_ms: float = 0.0


@dataclass(frozen=True, slots=True)
class CostSnapshot:
    provider_stats: Mapping[str, ProviderStats]
    model_stats: Mapping[str, ModelStats]


class CostMonitor:
    def __init__(self) -> None:
        self._provider_stats: dict[str, ProviderStats] = {}
        self._model_stats: dict[str, ModelStats] = {}

    def estimate_cost(self, model: ModelMetadata, usage: TokenUsage) -> float:
        input_cost = (usage.prompt_tokens / 1000) * model.cost.input_per_1k_tokens
        output_cost = (usage.completion_tokens / 1000) * model.cost.output_per_1k_tokens
        return input_cost + output_cost

    def record(self, response: UnifiedResponse) -> None:
        provider_stat = self._provider_stats.setdefault(
            response.provider_id,
            ProviderStats(provider_id=response.provider_id),
        )
        provider_stat.calls += 1
        provider_stat.prompt_tokens += response.usage.prompt_tokens
        provider_stat.completion_tokens += response.usage.completion_tokens
        provider_stat.estimated_cost += response.estimated_cost
        provider_stat.total_duration_ms += response.duration_ms
        provider_stat.total_latency_ms += response.latency_ms

        model_stat = self._model_stats.setdefault(
            response.model_id,
            ModelStats(model_id=response.model_id),
        )
        model_stat.calls += 1
        model_stat.prompt_tokens += response.usage.prompt_tokens
        model_stat.completion_tokens += response.usage.completion_tokens
        model_stat.estimated_cost += response.estimated_cost
        model_stat.total_duration_ms += response.duration_ms
        model_stat.total_latency_ms += response.latency_ms

    def snapshot(self) -> CostSnapshot:
        return CostSnapshot(
            provider_stats=MappingProxyType(dict(self._provider_stats)),
            model_stats=MappingProxyType(dict(self._model_stats)),
        )
