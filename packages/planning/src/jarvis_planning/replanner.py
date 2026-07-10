from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.events import Event, EventBus, EventType
from jarvis_planning.executor import Executor
from jarvis_planning.monitor import ProgressMonitor
from jarvis_planning.scheduler import Scheduler
from jarvis_planning.state_machine import TaskState


@dataclass
class ReplanResult:
    changed_tasks: list[str] = field(default_factory=list)
    new_tasks: list[str] = field(default_factory=list)
    removed_tasks: list[str] = field(default_factory=list)
    reassigned_tasks: list[str] = field(default_factory=list)
    dependency_changes: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_tasks or self.new_tasks or self.removed_tasks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "changed_tasks": self.changed_tasks,
            "new_tasks": self.new_tasks,
            "removed_tasks": self.removed_tasks,
            "reassigned_tasks": self.reassigned_tasks,
            "dependency_changes": self.dependency_changes,
            "reason": self.reason,
            "has_changes": self.has_changes,
        }


_REPLAN_TRIGGERS: list[str] = [
    "task_failure",
    "dependency_change",
    "agent_unavailable",
    "requirement_change",
    "timeout",
    "resource_constraint",
    "priority_change",
]


class Replanner:
    def __init__(self, scheduler: Scheduler, executor: Executor, monitor: ProgressMonitor, event_bus: EventBus) -> None:
        self._scheduler = scheduler
        self._executor = executor
        self._monitor = monitor
        self._event_bus = event_bus
        self._plan_id: str = ""

    def set_plan_id(self, plan_id: str) -> None:
        self._plan_id = plan_id

    def replan(self, reason: str, context: dict[str, Any] | None = None) -> ReplanResult:
        result = ReplanResult(reason=reason)
        schedule = self._scheduler.schedule()
        task_states = self._scheduler.get_task_summary()

        if reason == "task_failure":
            self._handle_task_failure(result, context or {})
        elif reason == "dependency_change":
            self._handle_dependency_change(result, context or {})
        elif reason == "agent_unavailable":
            self._handle_agent_unavailable(result, context or {})
        elif reason == "requirement_change":
            self._handle_requirement_change(result, context or {})
        elif reason == "timeout":
            self._handle_timeout(result, context or {})
        else:
            self._handle_generic(result, context or {})

        if result.has_changes:
            self._event_bus.emit(Event(
                EventType.PLAN_REPLANNED, self._plan_id,
                result.to_dict(),
            ))

        return result

    def _handle_task_failure(self, result: ReplanResult, context: dict[str, Any]) -> None:
        failed_task_id = context.get("task_id", "")
        if not failed_task_id:
            return
        result.changed_tasks.append(failed_task_id)
        dependents = self._scheduler.graph.get_all_dependents(failed_task_id)
        for dep_id in dependents:
            state = self._scheduler.get_state(dep_id)
            if state in (TaskState.PLANNED, TaskState.WAITING, TaskState.READY):
                self._scheduler.mark_blocked(dep_id)
                result.changed_tasks.append(dep_id)
        alternative = context.get("alternative")
        if alternative:
            result.new_tasks.append("replacement-" + failed_task_id)

    def _handle_dependency_change(self, result: ReplanResult, context: dict[str, Any]) -> None:
        affected = context.get("affected_tasks", [])
        for task_id in affected:
            state = self._scheduler.get_state(task_id)
            if state in (TaskState.PLANNED, TaskState.WAITING):
                if context.get("dependency_removed"):
                    self._scheduler.mark_ready(task_id)
                    result.changed_tasks.append(task_id)
                else:
                    self._scheduler.mark_blocked(task_id)
                    result.changed_tasks.append(task_id)

    def _handle_agent_unavailable(self, result: ReplanResult, context: dict[str, Any]) -> None:
        task_id = context.get("task_id", "")
        if task_id and task_id in self._scheduler.graph.tasks:
            state = self._scheduler.get_state(task_id)
            if state != TaskState.RUNNING:
                result.changed_tasks.append(task_id)
                result.reassigned_tasks.append(task_id)

    def _handle_requirement_change(self, result: ReplanResult, context: dict[str, Any]) -> None:
        changed_areas = context.get("changed_areas", [])
        for area in changed_areas:
            for tid, task in self._scheduler.graph.tasks.items():
                if area.lower() in task.title.lower() or area.lower() in task.description.lower():
                    state = self._scheduler.get_state(tid)
                    if state in (TaskState.PLANNED, TaskState.WAITING, TaskState.READY):
                        result.changed_tasks.append(tid)

    def _handle_timeout(self, result: ReplanResult, context: dict[str, Any]) -> None:
        task_id = context.get("task_id", "")
        if task_id:
            result.changed_tasks.append(task_id)
            schedule = self._scheduler.schedule()
            waiting = schedule.waiting_tasks
            for tid in waiting:
                task = self._scheduler.graph.tasks.get(tid)
                if task and task.priority > 0:
                    result.changed_tasks.append(tid)

    def _handle_generic(self, result: ReplanResult, context: dict[str, Any]) -> None:
        pass

    def get_triggers(self) -> list[str]:
        return list(_REPLAN_TRIGGERS)
