from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InMemoryCompensationEngine:
    _compensations: dict[str, list[str]] = field(default_factory=dict)

    def register_compensation(
        self, execution_id: str, step_id: str, action_id: str,
    ) -> None:
        if execution_id not in self._compensations:
            self._compensations[execution_id] = []
        self._compensations[execution_id].append(
            f"{action_id}:{step_id}",
        )

    def compensate(
        self, execution_id: str, failed_step_id: str,
    ) -> tuple[str, ...]:
        steps = self._compensations.get(execution_id, [])
        # Reverse order: undo most recent first
        reversed_steps = list(reversed(steps))
        compensated: list[str] = []
        for entry in reversed_steps:
            _action_id, step_id = entry.split(":", 1)
            if step_id == failed_step_id:
                continue
            compensated.append(step_id)
        return tuple(compensated)

    def get_compensation_order(self, execution_id: str) -> tuple[str, ...]:
        steps = self._compensations.get(execution_id, [])
        return tuple(reversed(steps))
