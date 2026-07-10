from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from time import perf_counter

from jarvis_ai.capability_registry import CapabilityRegistry
from jarvis_ai.cost_monitor import CostMonitor
from jarvis_ai.interfaces import ProviderAdapter
from jarvis_ai.model_registry import ModelRegistry
from jarvis_ai.models import (
    ModelMetadata,
    ProviderResponse,
    RouteSelection,
    RoutingPolicy,
    RuntimeRequest,
    StreamEvent,
    TokenUsage,
    UnifiedResponse,
)
from jarvis_ai.prompt_assembly_engine import PromptAssemblyEngine
from jarvis_ai.provider_registry import ProviderRegistry
from jarvis_ai.response_normalizer import ResponseNormalizer
from jarvis_ai.retry_manager import RetryManager
from jarvis_ai.routing_engine import RoutingEngine
from jarvis_ai.streaming_engine import CancellationToken, StreamingEngine


class RuntimeKernelError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RuntimeKernelResult:
    response: UnifiedResponse
    route: RouteSelection


class RuntimeKernel:
    def __init__(
        self,
        *,
        provider_registry: ProviderRegistry | None = None,
        capability_registry: CapabilityRegistry | None = None,
        model_registry: ModelRegistry | None = None,
        routing_engine: RoutingEngine | None = None,
        prompt_assembly_engine: PromptAssemblyEngine | None = None,
        streaming_engine: StreamingEngine | None = None,
        response_normalizer: ResponseNormalizer | None = None,
        retry_manager: RetryManager | None = None,
        cost_monitor: CostMonitor | None = None,
    ) -> None:
        self.provider_registry = provider_registry or ProviderRegistry()
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.model_registry = model_registry or ModelRegistry()
        self.routing_engine = routing_engine or RoutingEngine(
            self.provider_registry,
            self.model_registry,
        )
        self.prompt_assembly_engine = prompt_assembly_engine or PromptAssemblyEngine()
        self.streaming_engine = streaming_engine or StreamingEngine()
        self.response_normalizer = response_normalizer or ResponseNormalizer()
        self.retry_manager = retry_manager or RetryManager()
        self.cost_monitor = cost_monitor or CostMonitor()

    def register_provider(
        self,
        provider: ProviderAdapter,
        models: tuple[ModelMetadata, ...],
    ) -> None:
        self.provider_registry.register(provider)
        self.capability_registry.register_provider(provider.metadata)
        for model in models:
            if model.provider_id != provider.metadata.provider_id:
                raise RuntimeKernelError(
                    "Model "
                    f"'{model.identifier}' belongs to '{model.provider_id}' "
                    "and cannot be registered "
                    f"to provider '{provider.metadata.provider_id}'."
                )
            self.model_registry.register(model)
            self.capability_registry.register_model(model)

    async def execute(
        self,
        request: RuntimeRequest,
        *,
        routing_policy: RoutingPolicy | None = None,
    ) -> RuntimeKernelResult:
        self._validate_request(request)
        initial_route = self.routing_engine.route(request, routing_policy)

        start = perf_counter()

        async def run_for_provider(
            provider_id: str,
        ) -> tuple[RouteSelection, ProviderResponse]:
            routed = self.routing_engine.route_for_provider(
                request,
                provider_id,
                routing_policy,
            )
            provider = self.provider_registry.get(provider_id)
            provider_request = self.prompt_assembly_engine.assemble(
                request,
                routed,
                provider.metadata,
            )
            provider_response = await provider.invoke(provider_request)
            return routed, provider_response

        retry_fallback = initial_route.fallback_provider_ids
        routed_selection, provider_response = await self.retry_manager.execute(
            initial_route.provider_id,
            run_for_provider,
            fallback_provider_ids=retry_fallback,
        )

        duration_ms = (perf_counter() - start) * 1000
        latency_ms = duration_ms
        model = self.model_registry.get(routed_selection.model_id)
        usage = provider_response.usage or TokenUsage(prompt_tokens=0, completion_tokens=0)
        estimated_cost = self.cost_monitor.estimate_cost(model, usage)
        response = self.response_normalizer.normalize(
            provider_response,
            request,
            latency_ms=latency_ms,
            duration_ms=duration_ms,
            estimated_cost=estimated_cost,
            metadata={"routing_reasons": routed_selection.reasons},
        )
        self.cost_monitor.record(response)
        return RuntimeKernelResult(response=response, route=routed_selection)

    async def stream(
        self,
        request: RuntimeRequest,
        *,
        routing_policy: RoutingPolicy | None = None,
        cancellation_token: CancellationToken | None = None,
    ) -> AsyncIterator[StreamEvent]:
        self._validate_request(request)
        route = self.routing_engine.route(request, routing_policy)
        provider = self.provider_registry.get(route.provider_id)
        provider_request = self.prompt_assembly_engine.assemble(
            request,
            route,
            provider.metadata,
        )
        async for event in self.streaming_engine.stream(
            provider,
            provider_request,
            cancellation_token,
        ):
            yield event

    def discover_capabilities(self) -> dict[str, tuple[str, ...]]:
        discovered = self.provider_registry.discover_capabilities()
        return {capability.value: providers for capability, providers in discovered.items()}

    def _validate_request(self, request: RuntimeRequest) -> None:
        if not request.instructions.strip():
            raise RuntimeKernelError("Runtime request instructions must not be empty.")
        if not request.user_input.strip():
            raise RuntimeKernelError("Runtime request user input must not be empty.")
