from __future__ import annotations

import pytest
from conftest import build_provider_metadata
from jarvis_ai.models import (
    AICapability,
    Message,
    ProviderKind,
    RouteSelection,
    RoutingMode,
    RuntimeRequest,
)
from jarvis_ai.prompt_assembly_engine import PromptAssemblyEngine, PromptAssemblyError


def test_prompt_assembly_builds_provider_specific_payload() -> None:
    engine = PromptAssemblyEngine()
    request = RuntimeRequest.create(
        AICapability.CONVERSATION,
        "You are a helpful runtime assistant.",
        "Summarize the latest deployment.",
        history=(Message(role="assistant", content="Previous turn"),),
        context={"project": "jarvis", "environment": "staging"},
        metadata={
            "structured_output_schema": {
                "type": "object",
                "properties": {"summary": "string"},
            }
        },
    )
    route = RouteSelection(
        provider_id="google",
        model_id="gemini-1.5",
        routing_mode=RoutingMode.AUTOMATIC,
        fallback_provider_ids=(),
        reasons=("capability_match",),
    )
    provider = build_provider_metadata(
        "google",
        ProviderKind.GOOGLE,
        (AICapability.CONVERSATION,),
        ("gemini-1.5",),
    )

    provider_request = engine.assemble(request, route, provider)

    assert provider_request.model_id == "gemini-1.5"
    assert "Context:" in provider_request.system_instruction
    assert provider_request.messages[0].role == "model"
    assert provider_request.structured_output_schema["type"] == "object"


def test_prompt_assembly_validates_empty_inputs() -> None:
    engine = PromptAssemblyEngine()
    request = RuntimeRequest.create(AICapability.CONVERSATION, " ", "hello")
    route = RouteSelection(
        provider_id="openai",
        model_id="gpt-4o",
        routing_mode=RoutingMode.AUTOMATIC,
        fallback_provider_ids=(),
        reasons=("capability_match",),
    )
    provider = build_provider_metadata(
        "openai",
        ProviderKind.OPENAI,
        (AICapability.CONVERSATION,),
        ("gpt-4o",),
    )

    with pytest.raises(PromptAssemblyError):
        engine.assemble(request, route, provider)
