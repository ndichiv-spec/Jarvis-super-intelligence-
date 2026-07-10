from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_automation.models import (
    TriggerDefinition,
    TriggerEvent,
    TriggerType,
    WorkflowExecutionRequest,
)


@dataclass(slots=True)
class InMemoryTriggerEngine:
    _triggers: dict[str, TriggerDefinition] = field(default_factory=dict)

    def register_trigger(self, trigger: TriggerDefinition) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def unregister_trigger(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def get_trigger(self, trigger_id: str) -> TriggerDefinition | None:
        return self._triggers.get(trigger_id)

    def list_triggers(self) -> tuple[TriggerDefinition, ...]:
        return tuple(self._triggers.values())

    def list_by_type(self, trigger_type: TriggerType) -> tuple[TriggerDefinition, ...]:
        return tuple(
            t for t in self._triggers.values()
            if t.trigger_type == trigger_type and t.enabled
        )

    def fire(self, event: TriggerEvent) -> tuple[WorkflowExecutionRequest, ...]:
        requests: list[WorkflowExecutionRequest] = []
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            if trigger.trigger_type != event.trigger_type:
                continue
            if trigger.workflow_id != event.workflow_id:
                continue
            request = WorkflowExecutionRequest(
                execution_id=f"exec-{uuid4().hex[:8]}",
                workflow_id=trigger.workflow_id,
                trigger_type=event.trigger_type,
                correlation_id=event.correlation_id or trigger.trigger_id,
                inputs={
                    **trigger.parameters,
                    **event.payload,
                },
            )
            requests.append(request)
        return tuple(requests)
