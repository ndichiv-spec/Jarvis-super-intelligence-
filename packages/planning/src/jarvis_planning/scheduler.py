from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.policies import ExecutionPolicy
from jarvis_planning.state_machine import TaskState


@dataclass
class ScheduleResult:
    ready_queue: list[str] = field(default_factory=list)
    running_tasks: list[str] = field(default_factory=list)
    blocked_tasks: list[str] = field(default_factory=list)
    waiting_tasks: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    failed_tasks: list[str] = field(default_factory=list)

    @property
    def active_count(self) -> int:
        return len(self.running_tasks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ready_queue": self.ready_queue,
            "running_tasks": self.running_tasks,
            "blocked_tasks": self.blocked_tasks,
            "waiting_tasks": self.waiting_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "active_count": self.active_count,
        }


class Scheduler:
    def __init__(self, graph: DependencyGraph, policy: ExecutionPolicy | None = None) -> None:
        self._graph = graph
        self._policy = policy or ExecutionPolicy()
        self._task_states: dict[str, TaskState] = {}
        self._priorities: dict[str, int] = {}
        for tid, task in graph.tasks.items():
            self._task_states[tid] = TaskState.PLANNED
            self._priorities[tid] = task.priority

    @property
    def graph(self) -> DependencyGraph:
        return self._graph

    def schedule(self) -> ScheduleResult:
        result = ScheduleResult()
        for tid in self._graph.topological_sort():
            state = self._task_states.get(tid, TaskState.PLANNED)
            task = self._graph.tasks[tid]
            if state == TaskState.COMPLETED:
                result.completed_tasks.append(tid)
                continue
            if state == TaskState.FAILED:
                result.failed_tasks.append(tid)
                continue
            if state == TaskState.RUNNING:
                result.running_tasks.append(tid)
                continue
            if state == TaskState.WAITING:
                deps = self._graph.get_dependencies(tid)
                if any(self._task_states.get(d) in (TaskState.FAILED, TaskState.CANCELLED) for d in deps):
                    result.blocked_tasks.append(tid)
                    self._task_states[tid] = TaskState.BLOCKED
                    continue
                if any(self._task_states.get(d) != TaskState.COMPLETED for d in deps):
                    result.waiting_tasks.append(tid)
                    continue
                self._task_states[tid] = TaskState.READY
                result.ready_queue.append(tid)
                continue
            deps = self._graph.get_dependencies(tid)
            if any(self._task_states.get(d) in (TaskState.FAILED, TaskState.CANCELLED) for d in deps):
                result.blocked_tasks.append(tid)
                self._task_states[tid] = TaskState.BLOCKED
                continue
            if any(self._task_states.get(d) != TaskState.COMPLETED for d in deps):
                result.waiting_tasks.append(tid)
                self._task_states[tid] = TaskState.WAITING
                continue
            if self._policy.max_concurrent_tasks > 0 and result.active_count >= self._policy.max_concurrent_tasks:
                result.ready_queue.append(tid)
                continue
            result.ready_queue.append(tid)
        result.ready_queue.sort(key=lambda tid: self._priorities.get(tid, 0), reverse=True)
        return result

    def mark_running(self, task_id: str) -> None:
        self._task_states[task_id] = TaskState.RUNNING

    def mark_completed(self, task_id: str) -> None:
        self._task_states[task_id] = TaskState.COMPLETED

    def mark_failed(self, task_id: str) -> None:
        self._task_states[task_id] = TaskState.FAILED

    def mark_cancelled(self, task_id: str) -> None:
        self._task_states[task_id] = TaskState.CANCELLED

    def mark_ready(self, task_id: str) -> None:
        self._task_states[task_id] = TaskState.READY

    def mark_blocked(self, task_id: str) -> None:
        self._task_states[task_id] = TaskState.BLOCKED

    def get_state(self, task_id: str) -> TaskState | None:
        return self._task_states.get(task_id)

    def get_ready_tasks(self, max_tasks: int = 0) -> list[str]:
        result = self.schedule()
        ready = result.ready_queue
        if max_tasks > 0:
            ready = ready[:max_tasks]
        return ready

    def get_task_summary(self) -> dict[str, str]:
        return {tid: state.value for tid, state in self._task_states.items()}

    def get_available_capacity(self) -> int:
        if self._policy.max_concurrent_tasks <= 0:
            return 999
        running = sum(1 for s in self._task_states.values() if s == TaskState.RUNNING)
        return max(0, self._policy.max_concurrent_tasks - running)

    def to_dict(self) -> dict[str, Any]:
        schedule = self.schedule()
        return {
            "task_states": self.get_task_summary(),
            "schedule": schedule.to_dict(),
            "policy": self._policy.to_dict(),
            "available_capacity": self.get_available_capacity(),
        }
