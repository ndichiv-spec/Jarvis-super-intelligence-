from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ExecutionContext:
    goal_id: str | None = None
    objective_id: str | None = None
    plan_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    workspace_id: str = "default"
    organization_id: str | None = None
    conversation_id: str | None = None
    reasoning_history: list[dict[str, Any]] = field(default_factory=list)
    memory_references: list[str] = field(default_factory=list)
    knowledge_references: list[str] = field(default_factory=list)
    agent_references: list[str] = field(default_factory=list)
    execution_history: list[dict[str, Any]] = field(default_factory=list)
    active_goals: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ContextManager:
    def __init__(self) -> None:
        self._contexts: dict[str, ExecutionContext] = {}

    def create(self, context: ExecutionContext | None = None) -> ExecutionContext:
        ctx = context or ExecutionContext()
        ctx_id = f"ctx-{id(ctx)}"
        self._contexts[ctx_id] = ctx
        return ctx

    def get(self, ctx_id: str) -> ExecutionContext | None:
        return self._contexts.get(ctx_id)

    def update(self, ctx: ExecutionContext) -> None:
        pass

    def push_reasoning(self, ctx: ExecutionContext, stage: str, reasoning: str, confidence: float = 1.0) -> None:
        ctx.reasoning_history.append({
            "stage": stage,
            "reasoning": reasoning,
            "confidence": confidence,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def push_execution(self, ctx: ExecutionContext, action: str, status: str, details: dict[str, Any] | None = None) -> None:
        ctx.execution_history.append({
            "action": action,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now(UTC).isoformat(),
        })
