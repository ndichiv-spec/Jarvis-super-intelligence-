from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import monotonic
from typing import TypeVar

from jarvis_ai.models import RetryPolicy

T = TypeVar("T")


class RetryManagerError(RuntimeError):
    pass


class CircuitOpenError(RetryManagerError):
    pass


class RetryExhaustedError(RetryManagerError):
    pass


@dataclass(slots=True)
class CircuitState:
    failure_count: int = 0
    open_until: float = 0.0


class RetryManager:
    def __init__(
        self,
        default_policy: RetryPolicy | None = None,
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._default_policy = default_policy or RetryPolicy()
        self._sleep = sleep
        self._clock = clock
        self._circuits: dict[str, CircuitState] = {}

    async def execute(
        self,
        primary_provider_id: str,
        run_with_provider: Callable[[str], Awaitable[T]],
        *,
        fallback_provider_ids: tuple[str, ...] = (),
        policy: RetryPolicy | None = None,
    ) -> T:
        active_policy = policy or self._default_policy
        provider_chain = self._provider_chain(primary_provider_id, fallback_provider_ids)
        last_error: Exception | None = None

        for provider_id in provider_chain:
            if self._is_circuit_open(provider_id):
                last_error = CircuitOpenError(f"Circuit breaker open for provider '{provider_id}'.")
                continue

            for attempt in range(active_policy.max_attempts):
                try:
                    async with asyncio.timeout(active_policy.timeout_seconds):
                        result = await run_with_provider(provider_id)
                    self._reset_circuit(provider_id)
                    return result
                except TimeoutError:
                    last_error = RetryManagerError(
                        "Provider "
                        f"'{provider_id}' timed out after {active_policy.timeout_seconds} seconds."
                    )
                    self._record_failure(provider_id, active_policy)
                    if attempt < active_policy.max_attempts - 1:
                        await self._backoff(attempt, active_policy)
                except Exception as exc:
                    last_error = exc
                    self._record_failure(provider_id, active_policy)
                    if attempt < active_policy.max_attempts - 1:
                        await self._backoff(attempt, active_policy)

        raise RetryExhaustedError("All providers exhausted for request execution.") from last_error

    def _provider_chain(
        self,
        primary_provider_id: str,
        fallback_provider_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        providers: list[str] = [primary_provider_id]
        for provider_id in fallback_provider_ids:
            if provider_id not in providers:
                providers.append(provider_id)
        return tuple(providers)

    def _is_circuit_open(self, provider_id: str) -> bool:
        state = self._circuits.get(provider_id)
        if state is None:
            return False
        return state.open_until > self._clock()

    def _reset_circuit(self, provider_id: str) -> None:
        self._circuits[provider_id] = CircuitState()

    def _record_failure(self, provider_id: str, policy: RetryPolicy) -> None:
        state = self._circuits.setdefault(provider_id, CircuitState())
        state.failure_count += 1
        if state.failure_count >= policy.circuit_breaker_failures:
            state.open_until = self._clock() + policy.circuit_breaker_reset_seconds

    async def _backoff(self, attempt: int, policy: RetryPolicy) -> None:
        backoff_index = min(attempt, len(policy.backoff_seconds) - 1)
        delay = policy.backoff_seconds[backoff_index]
        if delay > 0:
            await self._sleep(delay)
