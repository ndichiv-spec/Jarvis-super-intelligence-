from __future__ import annotations

from jarvis_ai.model_registry import ModelRegistry, ModelRegistryError
from jarvis_ai.models import (
    ModelMetadata,
    RouteSelection,
    RoutingMode,
    RoutingPolicy,
    RuntimeRequest,
)
from jarvis_ai.provider_registry import ProviderRegistry


class RoutingEngineError(ValueError):
    pass


class RoutingEngine:
    def __init__(self, provider_registry: ProviderRegistry, model_registry: ModelRegistry) -> None:
        self._provider_registry = provider_registry
        self._model_registry = model_registry

    def route(self, request: RuntimeRequest, policy: RoutingPolicy | None = None) -> RouteSelection:
        active_policy = policy or RoutingPolicy()
        candidates = self._candidate_models(request, active_policy)
        if not candidates:
            raise RoutingEngineError(
                "No model available for capability "
                f"'{request.capability.value}' and current routing constraints."
            )

        if request.manual_model_id is not None:
            model = self._manual_model(request, request.manual_model_id, active_policy)
            fallback = self._fallback_providers(candidates, model.provider_id)
            return RouteSelection(
                provider_id=model.provider_id,
                model_id=model.identifier,
                routing_mode=RoutingMode.MANUAL,
                fallback_provider_ids=fallback,
                reasons=("manual_model",),
            )

        if request.manual_provider_id is not None:
            model = self._best_model_for_provider(candidates, request.manual_provider_id)
            fallback = self._fallback_providers(candidates, model.provider_id)
            return RouteSelection(
                provider_id=model.provider_id,
                model_id=model.identifier,
                routing_mode=RoutingMode.MANUAL,
                fallback_provider_ids=fallback,
                reasons=("manual_provider",),
            )

        ranked_candidates = self._rank_models(candidates, request, active_policy)
        selected = ranked_candidates[0]
        fallback = self._fallback_providers(ranked_candidates, selected.provider_id)
        routing_mode = self._resolve_routing_mode(request, active_policy)
        reasons = self._selection_reasons(request, active_policy)
        return RouteSelection(
            provider_id=selected.provider_id,
            model_id=selected.identifier,
            routing_mode=routing_mode,
            fallback_provider_ids=fallback,
            reasons=reasons,
        )

    def route_for_provider(
        self,
        request: RuntimeRequest,
        provider_id: str,
        policy: RoutingPolicy | None = None,
    ) -> RouteSelection:
        active_policy = policy or RoutingPolicy()
        candidates = self._candidate_models(request, active_policy)
        model = self._best_model_for_provider(candidates, provider_id)
        return RouteSelection(
            provider_id=provider_id,
            model_id=model.identifier,
            routing_mode=RoutingMode.FALLBACK,
            fallback_provider_ids=(),
            reasons=("retry_fallback_provider",),
        )

    def _manual_model(
        self,
        request: RuntimeRequest,
        model_id: str,
        policy: RoutingPolicy,
    ) -> ModelMetadata:
        try:
            model = self._model_registry.get(model_id)
        except ModelRegistryError as exc:
            raise RoutingEngineError(str(exc)) from exc
        if request.capability not in model.capabilities:
            raise RoutingEngineError(
                f"Model '{model_id}' does not support capability '{request.capability.value}'."
            )
        if request.stream and not model.supports_streaming:
            raise RoutingEngineError(f"Model '{model_id}' does not support streaming.")
        if not model.available:
            raise RoutingEngineError(f"Model '{model_id}' is not available.")
        if not self._policy_allows_model(model, policy):
            raise RoutingEngineError(f"Model '{model_id}' violates routing policy constraints.")
        if not self._request_allows_provider(request, model.provider_id):
            raise RoutingEngineError(
                "Provider "
                f"'{model.provider_id}' for model '{model_id}' is blocked by request constraints."
            )
        return model

    def _candidate_models(
        self,
        request: RuntimeRequest,
        policy: RoutingPolicy,
    ) -> tuple[ModelMetadata, ...]:
        models = self._model_registry.list(
            capability=request.capability,
            streaming=True if request.stream else None,
            available_only=True,
        )
        return tuple(
            model
            for model in models
            if self._request_allows_provider(request, model.provider_id)
            and self._policy_allows_model(model, policy)
            and self._provider_available(model.provider_id)
        )

    def _provider_available(self, provider_id: str) -> bool:
        provider = self._provider_registry.get(provider_id)
        return provider.metadata.available

    def _policy_allows_model(
        self,
        model: ModelMetadata,
        policy: RoutingPolicy,
    ) -> bool:
        if (
            policy.minimum_quality is not None
            and model.performance.quality_score < policy.minimum_quality
        ):
            return False
        if policy.required_tags and not policy.required_tags.issubset(model.tags):
            return False
        if policy.disallowed_tags and policy.disallowed_tags.intersection(model.tags):
            return False
        return True

    def _request_allows_provider(self, request: RuntimeRequest, provider_id: str) -> bool:
        if request.allowed_provider_ids and provider_id not in request.allowed_provider_ids:
            return False
        return provider_id not in request.blocked_provider_ids

    def _best_model_for_provider(
        self,
        candidates: tuple[ModelMetadata, ...],
        provider_id: str,
    ) -> ModelMetadata:
        provider_candidates = tuple(
            model for model in candidates if model.provider_id == provider_id
        )
        if not provider_candidates:
            raise RoutingEngineError(f"No eligible model found for provider '{provider_id}'.")
        return provider_candidates[0]

    def _rank_models(
        self,
        models: tuple[ModelMetadata, ...],
        request: RuntimeRequest,
        policy: RoutingPolicy,
    ) -> tuple[ModelMetadata, ...]:
        priority_order = {
            provider: index for index, provider in enumerate(request.priority_provider_ids)
        }

        def score(model: ModelMetadata) -> tuple[float, float, float]:
            quality = model.performance.quality_score
            reliability = model.performance.reliability_score
            speed = model.performance.speed_score
            if policy.prefer_low_cost:
                quality -= model.cost.input_per_1k_tokens + model.cost.output_per_1k_tokens
            if policy.prefer_low_latency:
                quality += speed
            priority_penalty = float(priority_order.get(model.provider_id, len(priority_order)))
            return (quality - priority_penalty, reliability, speed)

        return tuple(sorted(models, key=score, reverse=True))

    def _fallback_providers(
        self,
        models: tuple[ModelMetadata, ...],
        primary_provider_id: str,
    ) -> tuple[str, ...]:
        providers: list[str] = []
        for model in models:
            provider_id = model.provider_id
            if provider_id == primary_provider_id or provider_id in providers:
                continue
            providers.append(provider_id)
        return tuple(providers)

    def _resolve_routing_mode(
        self,
        request: RuntimeRequest,
        policy: RoutingPolicy,
    ) -> RoutingMode:
        if request.priority_provider_ids:
            return RoutingMode.PRIORITY
        if policy != RoutingPolicy():
            return RoutingMode.POLICY
        return RoutingMode.AUTOMATIC

    def _selection_reasons(
        self,
        request: RuntimeRequest,
        policy: RoutingPolicy,
    ) -> tuple[str, ...]:
        reasons: list[str] = ["capability_match"]
        if request.priority_provider_ids:
            reasons.append("priority_provider")
        if policy.prefer_low_cost:
            reasons.append("prefer_low_cost")
        if policy.prefer_low_latency:
            reasons.append("prefer_low_latency")
        if policy.minimum_quality is not None:
            reasons.append("minimum_quality")
        if policy.required_tags:
            reasons.append("required_tags")
        if policy.disallowed_tags:
            reasons.append("disallowed_tags")
        return tuple(reasons)
