from __future__ import annotations

from conftest import build_model
from jarvis_ai.model_registry import ModelRegistry
from jarvis_ai.models import AICapability, RoutingPolicy, RuntimeRequest
from jarvis_ai.provider_registry import ProviderRegistry
from jarvis_ai.provider_sdk import GoogleAdapter, OpenAIAdapter
from jarvis_ai.routing_engine import RoutingEngine


def test_routing_engine_selects_model_by_capability_and_policy() -> None:
    provider_registry = ProviderRegistry()
    provider_registry.register(OpenAIAdapter(("gpt-4o",), (AICapability.CONVERSATION,)))
    provider_registry.register(GoogleAdapter(("gemini-1.5",), (AICapability.CONVERSATION,)))

    model_registry = ModelRegistry()
    model_registry.register(
        build_model(
            "gpt-4o",
            "openai",
            (AICapability.CONVERSATION,),
            quality=0.92,
            input_cost=0.9,
            output_cost=1.1,
            tags=frozenset({"premium"}),
        )
    )
    model_registry.register(
        build_model(
            "gemini-1.5",
            "google",
            (AICapability.CONVERSATION,),
            quality=0.88,
            input_cost=0.2,
            output_cost=0.3,
            tags=frozenset({"economy"}),
        )
    )

    router = RoutingEngine(provider_registry, model_registry)
    request = RuntimeRequest.create(
        AICapability.CONVERSATION,
        "Answer accurately",
        "Explain observability",
    )

    route_default = router.route(request)
    assert route_default.model_id == "gpt-4o"

    route_low_cost = router.route(request, RoutingPolicy(prefer_low_cost=True))
    assert route_low_cost.model_id == "gemini-1.5"


def test_routing_engine_honors_manual_provider_and_priority_order() -> None:
    provider_registry = ProviderRegistry()
    provider_registry.register(OpenAIAdapter(("gpt-4o",), (AICapability.CONVERSATION,)))
    provider_registry.register(GoogleAdapter(("gemini-1.5",), (AICapability.CONVERSATION,)))

    model_registry = ModelRegistry()
    model_registry.register(
        build_model("gpt-4o", "openai", (AICapability.CONVERSATION,), quality=0.95)
    )
    model_registry.register(
        build_model("gemini-1.5", "google", (AICapability.CONVERSATION,), quality=0.94)
    )

    router = RoutingEngine(provider_registry, model_registry)

    manual_request = RuntimeRequest.create(
        AICapability.CONVERSATION,
        "Answer accurately",
        "Manual provider",
        manual_provider_id="google",
    )
    manual_route = router.route(manual_request)
    assert manual_route.provider_id == "google"

    priority_request = RuntimeRequest.create(
        AICapability.CONVERSATION,
        "Answer accurately",
        "Priority provider",
        priority_provider_ids=("google", "openai"),
    )
    priority_route = router.route(priority_request)
    assert priority_route.provider_id == "google"
