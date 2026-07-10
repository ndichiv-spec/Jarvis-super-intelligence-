from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_automation.models import VariableScope, VariableValue


@dataclass(slots=True)
class InMemoryVariableManager:
    _variables: dict[str, dict[str, VariableValue]] = field(default_factory=dict)

    def set(self, execution_id: str, variable: VariableValue) -> None:
        if execution_id not in self._variables:
            self._variables[execution_id] = {}
        existing = self._variables[execution_id].get(variable.name)
        if existing is not None and existing.immutable:
            msg = f"Variable '{variable.name}' is immutable"
            raise ValueError(msg)
        self._variables[execution_id][variable.name] = variable

    def get(self, execution_id: str, name: str) -> VariableValue | None:
        return self._variables.get(execution_id, {}).get(name)

    def list(self, execution_id: str) -> tuple[VariableValue, ...]:
        return tuple(self._variables.get(execution_id, {}).values())

    def list_by_scope(
        self, execution_id: str, scope: VariableScope,
    ) -> tuple[VariableValue, ...]:
        return tuple(
            v for v in self._variables.get(execution_id, {}).values()
            if v.scope == scope
        )

    def delete(self, execution_id: str, name: str) -> None:
        self._variables.get(execution_id, {}).pop(name, None)
