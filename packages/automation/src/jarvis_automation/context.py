from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_automation.models import ExecutionContextData


@dataclass(slots=True)
class InMemoryExecutionContext:
    _contexts: dict[str, ExecutionContextData] = field(default_factory=dict)

    def create(
        self,
        workflow_id: str,
        execution_id: str,
        correlation_id: str,
        workspace: str = "*",
        project: str = "*",
    ) -> ExecutionContextData:
        context = ExecutionContextData(
            workflow_id=workflow_id,
            execution_id=execution_id,
            correlation_id=correlation_id,
            workspace=workspace,
            project=project,
        )
        self._contexts[execution_id] = context
        return context

    def get(self, execution_id: str) -> ExecutionContextData | None:
        return self._contexts.get(execution_id)

    def advance_step(self, execution_id: str, step_id: str) -> ExecutionContextData:
        context = self._contexts.get(execution_id)
        if context is None:
            msg = f"Context not found: {execution_id}"
            raise KeyError(msg)
        updated = context.with_current_step(step_id)
        self._contexts[execution_id] = updated
        return updated

    def get_history(self, execution_id: str) -> tuple[str, ...]:
        context = self._contexts.get(execution_id)
        if context is None:
            return ()
        return context.history
