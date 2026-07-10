from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class Objective:
    id: str
    description: str
    goal_id: str | None = None
    constraints: tuple[str, ...] = ()
    priority: int = 50
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, description: str, goal_id: str | None = None, *, constraints: tuple[str, ...] | None = None, priority: int = 50) -> Objective:
        return cls(
            id=f"obj-{uuid4().hex[:12]}",
            description=description,
            goal_id=goal_id,
            constraints=constraints or (),
            priority=priority,
        )
