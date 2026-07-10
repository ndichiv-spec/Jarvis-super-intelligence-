from __future__ import annotations

from jarvis_ai.models import AICapability, ProviderResponse, RuntimeRequest, TokenUsage
from jarvis_ai.response_normalizer import ResponseNormalizer


def test_response_normalizer_builds_unified_response() -> None:
    normalizer = ResponseNormalizer()
    request = RuntimeRequest.create(
        AICapability.CONVERSATION,
        "Respond clearly",
        "What changed?",
    )
    provider_response = ProviderResponse.create(
        text="Runtime updated",
        provider_id="openai",
        model_id="gpt-4o",
        usage=TokenUsage(prompt_tokens=11, completion_tokens=7),
        metadata={"raw_finish": "stop"},
    )

    unified = normalizer.normalize(
        provider_response,
        request,
        latency_ms=55.0,
        duration_ms=60.0,
        estimated_cost=0.004,
        metadata={"route": "automatic"},
    )

    assert unified.provider_id == "openai"
    assert unified.model_id == "gpt-4o"
    assert unified.usage.total_tokens == 18
    assert unified.metadata["route"] == "automatic"
