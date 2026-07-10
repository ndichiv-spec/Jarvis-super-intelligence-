from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_automation.models import RetryPolicy, RetryStrategy


@dataclass(slots=True)
class InMemoryRetryManager:
    _attempts: dict[str, dict[str, int]] = field(default_factory=dict)

    def should_retry(self, step_id: str, policy: RetryPolicy, attempts: int) -> bool:
        if attempts >= policy.max_retries:
            if (
                policy.strategy == RetryStrategy.ALTERNATIVE_PATH
                and policy.alternative_step_id is not None
            ):
                return True
            if (
                policy.strategy == RetryStrategy.ESCALATION
                and policy.escalation_after > 0
                and attempts >= policy.escalation_after
            ):
                return False
            return False
        return True

    def next_delay(self, policy: RetryPolicy, attempts: int) -> int:
        if attempts == 0:
            return 0
        if policy.strategy == RetryStrategy.IMMEDIATE:
            return 0
        if policy.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = policy.delay_seconds * (policy.backoff_multiplier ** (attempts - 1))
            raw: int = int(delay)
            return raw if raw < policy.max_delay_seconds else policy.max_delay_seconds
        if policy.strategy == RetryStrategy.ALTERNATIVE_PATH:
            return 0
        if policy.strategy == RetryStrategy.ESCALATION:
            esc_delay: int = int(policy.delay_seconds * (2 ** (attempts - 1)))
            return esc_delay if esc_delay < policy.max_delay_seconds else policy.max_delay_seconds
        return policy.delay_seconds

    def record_attempt(self, execution_id: str, step_id: str) -> int:
        if execution_id not in self._attempts:
            self._attempts[execution_id] = {}
        current = self._attempts[execution_id].get(step_id, 0) + 1
        self._attempts[execution_id][step_id] = current
        return current

    def get_attempts(self, execution_id: str, step_id: str) -> int:
        return self._attempts.get(execution_id, {}).get(step_id, 0)

    def reset(self, execution_id: str, step_id: str) -> None:
        self._attempts.get(execution_id, {}).pop(step_id, None)
