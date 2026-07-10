from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable

from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.events import Event, EventBus, EventType
from jarvis_planning.policies import ExecutionPolicy, RetryPolicy
from jarvis_planning.scheduler import Scheduler
from jarvis_planning.state_machine import TaskState, TaskStateMachine


TaskExecutorFunc = Callable[[Task, dict[str, Any]], dict[str, Any]]


@dataclass
class ExecutionResult:
    task_id: str
    success: bool
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    attempts: int = 1
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "success": self.success,
            "outputs": self.outputs,
            "error": self.error,
            "attempts": self.attempts,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }


class Executor:
    def __init__(
        self,
        scheduler: Scheduler,
        event_bus: EventBus,
        executors: dict[str, TaskExecutorFunc] | None = None,
    ) -> None:
        self._scheduler = scheduler
        self._event_bus = event_bus
        self._executors: dict[str, TaskExecutorFunc] = executors or {}
        self._results: dict[str, ExecutionResult] = {}
        self._task_outputs: dict[str, dict[str, Any]] = {}
        self._state_machines: dict[str, TaskStateMachine] = {}
        self._plan_id: str = ""

    def set_plan_id(self, plan_id: str) -> None:
        self._plan_id = plan_id

    def register_executor(self, task_type: str, func: TaskExecutorFunc) -> None:
        self._executors[task_type] = func

    def execute_next(self) -> ExecutionResult | None:
        schedule = self._scheduler.schedule()
        if not schedule.ready_queue:
            return None
        task_id = schedule.ready_queue[0]
        return self.execute_task(task_id)

    def execute_task(self, task_id: str) -> ExecutionResult:
        task = self._scheduler.graph.tasks.get(task_id)
        if task is None:
            return ExecutionResult(task_id, False, error=f"Task {task_id} not found")

        sm = self._get_state_machine(task_id)

        try:
            sm.transition_to(TaskState.RUNNING)
        except Exception:
            return ExecutionResult(task_id, False, error="Task cannot start")

        self._scheduler.mark_running(task_id)
        started_at = datetime.now(UTC)

        self._event_bus.emit(Event(
            EventType.TASK_STARTED, self._plan_id,
            {"task_id": task_id, "title": task.title},
        ))

        result = self._execute_with_retry(task)
        completed_at = datetime.now(UTC)
        duration = (completed_at - started_at).total_seconds()
        result.started_at = started_at
        result.completed_at = completed_at
        result.duration_seconds = duration

        if result.success:
            try:
                sm.transition_to(TaskState.COMPLETED)
            except Exception:
                pass
            self._scheduler.mark_completed(task_id)
            self._task_outputs[task_id] = result.outputs
            self._event_bus.emit(Event(
                EventType.TASK_COMPLETED, self._plan_id,
                {"task_id": task_id, "outputs": result.outputs, "duration": duration},
            ))
        else:
            try:
                sm.transition_to(TaskState.FAILED)
            except Exception:
                pass
            self._scheduler.mark_failed(task_id)
            self._event_bus.emit(Event(
                EventType.TASK_FAILED, self._plan_id,
                {"task_id": task_id, "error": result.error, "attempts": result.attempts},
            ))

        self._results[task_id] = result
        return result

    def _execute_with_retry(self, task: Task) -> ExecutionResult:
        last_error = ""
        for attempt in range(task.retry_policy.max_retries):
            try:
                executor = self._executors.get(task.task_type.value if hasattr(task.task_type, 'value') else task.task_type)
                if executor is None:
                    executor = self._executors.get("__default__")
                if executor:
                    outputs = executor(task, self._task_outputs)
                else:
                    outputs = {"status": f"simulated_success_{task.id}"}
                return ExecutionResult(task.id, True, outputs=outputs, attempts=attempt + 1)
            except Exception as e:
                last_error = str(e)
                if attempt < task.retry_policy.max_retries - 1 and task.retry_policy.should_retry(attempt):
                    import time
                    delay = task.retry_policy.next_delay(attempt)
                    time.sleep(delay)
                continue
        return ExecutionResult(task.id, False, error=last_error, attempts=task.retry_policy.max_retries)

    def get_result(self, task_id: str) -> ExecutionResult | None:
        return self._results.get(task_id)

    def get_all_results(self) -> dict[str, ExecutionResult]:
        return dict(self._results)

    def get_task_outputs(self) -> dict[str, dict[str, Any]]:
        return dict(self._task_outputs)

    def is_complete(self) -> bool:
        schedule = self._scheduler.schedule()
        total = len(self._scheduler.graph.tasks)
        completed = len(schedule.completed_tasks)
        failed = len(schedule.failed_tasks)
        return completed + failed == total

    def _get_state_machine(self, task_id: str) -> TaskStateMachine:
        if task_id not in self._state_machines:
            state = self._scheduler.get_state(task_id) or TaskState.PLANNED
            self._state_machines[task_id] = TaskStateMachine(task_id, state)
        return self._state_machines[task_id]
