from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ExecutionPolicy(StrEnum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    EXPERIMENTAL = "experimental"


@dataclass
class PolicyConfig:
    max_concurrent_tasks: int
    max_retries: int
    timeout_seconds: float
    confidence_threshold: float
    allow_parallel: bool
    allow_agent_auto_selection: bool
    allow_replanning: bool
    require_approval: bool
    risk_tolerance: str


DEFAULT_POLICIES: dict[ExecutionPolicy, PolicyConfig] = {
    ExecutionPolicy.CONSERVATIVE: PolicyConfig(
        max_concurrent_tasks=2,
        max_retries=1,
        timeout_seconds=300.0,
        confidence_threshold=0.8,
        allow_parallel=False,
        allow_agent_auto_selection=False,
        allow_replanning=False,
        require_approval=True,
        risk_tolerance="low",
    ),
    ExecutionPolicy.BALANCED: PolicyConfig(
        max_concurrent_tasks=4,
        max_retries=3,
        timeout_seconds=600.0,
        confidence_threshold=0.6,
        allow_parallel=True,
        allow_agent_auto_selection=True,
        allow_replanning=True,
        require_approval=False,
        risk_tolerance="medium",
    ),
    ExecutionPolicy.AGGRESSIVE: PolicyConfig(
        max_concurrent_tasks=8,
        max_retries=5,
        timeout_seconds=1200.0,
        confidence_threshold=0.4,
        allow_parallel=True,
        allow_agent_auto_selection=True,
        allow_replanning=True,
        require_approval=False,
        risk_tolerance="high",
    ),
    ExecutionPolicy.EXPERIMENTAL: PolicyConfig(
        max_concurrent_tasks=16,
        max_retries=10,
        timeout_seconds=3600.0,
        confidence_threshold=0.2,
        allow_parallel=True,
        allow_agent_auto_selection=True,
        allow_replanning=True,
        require_approval=False,
        risk_tolerance="very_high",
    ),
}


class PolicyEngine:
    def __init__(self, policy: ExecutionPolicy = ExecutionPolicy.BALANCED) -> None:
        self._policy = policy
        self._config = DEFAULT_POLICIES[policy]

    def get_config(self) -> PolicyConfig:
        return self._config

    def set_policy(self, policy: ExecutionPolicy) -> None:
        self._policy = policy
        self._config = DEFAULT_POLICIES[policy]

    def get_current_policy(self) -> ExecutionPolicy:
        return self._policy

    def validate_parallel_execution(self, task_count: int) -> tuple[bool, str]:
        if task_count > self._config.max_concurrent_tasks:
            return False, f"max_concurrent_tasks={self._config.max_concurrent_tasks} exceeded ({task_count})"
        if not self._config.allow_parallel and task_count > 1:
            return False, "parallel execution disabled by policy"
        return True, "ok"

    def validate_retry(self, current_retries: int) -> tuple[bool, str]:
        if current_retries >= self._config.max_retries:
            return False, f"max_retries={self._config.max_retries} reached"
        return True, "ok"
