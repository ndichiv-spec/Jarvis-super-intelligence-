from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class RetryPolicy:
    max_retries: int = 3
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 60.0
    retryable_on: set[str] | None = None

    def next_delay(self, attempt: int) -> float:
        delay = self.delay_seconds * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay_seconds)

    def should_retry(self, attempt: int, error_type: str = "") -> bool:
        if attempt >= self.max_retries:
            return False
        if self.retryable_on is not None and error_type and error_type not in self.retryable_on:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "delay_seconds": self.delay_seconds,
            "backoff_multiplier": self.backoff_multiplier,
            "max_delay_seconds": self.max_delay_seconds,
            "retryable_on": list(self.retryable_on) if self.retryable_on else None,
        }


DEFAULT_RETRY_POLICY = RetryPolicy()


@dataclass
class CompletionCriteria:
    require_all_outputs: bool = True
    require_verification: bool = False
    min_confidence: float = 0.0
    custom_check: Callable[[dict[str, Any]], bool] | None = None

    def is_satisfied(self, task_outputs: dict[str, Any], task_state: dict[str, Any]) -> bool:
        if self.require_all_outputs and not task_outputs:
            return False
        if self.min_confidence > 0.0:
            confidence = task_state.get("confidence", 0.0)
            if confidence < self.min_confidence:
                return False
        if self.custom_check is not None:
            return self.custom_check({**task_outputs, **task_state})
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "require_all_outputs": self.require_all_outputs,
            "require_verification": self.require_verification,
            "min_confidence": self.min_confidence,
        }


@dataclass
class ExecutionPolicy:
    max_concurrent_tasks: int = 5
    allow_parallel: bool = True
    require_agent_approval: bool = False
    timeout_seconds: float | None = None
    retry_policy: RetryPolicy = field(default_factory=lambda: DEFAULT_RETRY_POLICY)
    completion_criteria: CompletionCriteria = field(default_factory=lambda: CompletionCriteria())

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "allow_parallel": self.allow_parallel,
            "require_agent_approval": self.require_agent_approval,
            "timeout_seconds": self.timeout_seconds,
            "retry_policy": self.retry_policy.to_dict(),
            "completion_criteria": self.completion_criteria.to_dict(),
        }


DEFAULT_EXECUTION_POLICY = ExecutionPolicy()
