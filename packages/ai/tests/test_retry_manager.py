from __future__ import annotations

import asyncio

from jarvis_ai.models import RetryPolicy
from jarvis_ai.retry_manager import RetryExhaustedError, RetryManager


def test_retry_manager_uses_fallback_provider() -> None:
    attempts: dict[str, int] = {"openai": 0, "google": 0}

    async def run(provider_id: str) -> str:
        attempts[provider_id] += 1
        if provider_id == "openai":
            raise RuntimeError("temporary failure")
        return provider_id

    manager = RetryManager(default_policy=RetryPolicy(max_attempts=1, backoff_seconds=(0.0,)))
    result = asyncio.run(
        manager.execute(
            "openai",
            run,
            fallback_provider_ids=("google",),
        )
    )

    assert result == "google"
    assert attempts == {"openai": 1, "google": 1}


def test_retry_manager_raises_when_all_attempts_fail() -> None:
    async def run(_: str) -> str:
        raise RuntimeError("still failing")

    manager = RetryManager(default_policy=RetryPolicy(max_attempts=1, backoff_seconds=(0.0,)))

    try:
        asyncio.run(manager.execute("openai", run))
    except RetryExhaustedError:
        return
    raise AssertionError("RetryExhaustedError expected")
