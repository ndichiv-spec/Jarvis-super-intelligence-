from __future__ import annotations

import asyncio

from conftest import StaticProvider, build_model, build_provider_metadata
from jarvis_ai.models import AICapability, ProviderKind, RuntimeRequest
from jarvis_ai.runtime_kernel import RuntimeKernel


def test_runtime_kernel_executes_and_falls_back_to_secondary_provider() -> None:
    kernel = RuntimeKernel()

    primary_provider = StaticProvider(
        build_provider_metadata(
            "openai",
            ProviderKind.OPENAI,
            (AICapability.CONVERSATION,),
            ("gpt-4o",),
        ),
        response_text="primary",
        fail_invocations=2,
    )
    fallback_provider = StaticProvider(
        build_provider_metadata(
            "google",
            ProviderKind.GOOGLE,
            (AICapability.CONVERSATION,),
            ("gemini-1.5",),
        ),
        response_text="fallback",
    )

    kernel.register_provider(
        primary_provider,
        (build_model("gpt-4o", "openai", (AICapability.CONVERSATION,), quality=0.95),),
    )
    kernel.register_provider(
        fallback_provider,
        (build_model("gemini-1.5", "google", (AICapability.CONVERSATION,), quality=0.90),),
    )

    request = RuntimeRequest.create(
        AICapability.CONVERSATION,
        "Respond clearly",
        "What is the deployment status?",
    )

    result = asyncio.run(kernel.execute(request))

    assert result.response.provider_id == "google"
    assert result.response.model_id == "gemini-1.5"
    assert result.response.text.startswith("fallback")
    assert result.response.usage.total_tokens == 15


def test_runtime_kernel_capability_discovery_reflects_registered_providers() -> None:
    kernel = RuntimeKernel()
    provider = StaticProvider(
        build_provider_metadata(
            "openai",
            ProviderKind.OPENAI,
            (AICapability.CONVERSATION, AICapability.SUMMARIZATION),
            ("gpt-4o",),
        )
    )
    kernel.register_provider(
        provider,
        (build_model("gpt-4o", "openai", (AICapability.CONVERSATION, AICapability.SUMMARIZATION)),),
    )

    discovered = kernel.discover_capabilities()

    assert discovered["conversation"] == ("openai",)
    assert discovered["summarization"] == ("openai",)
