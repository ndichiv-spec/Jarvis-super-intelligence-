from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_agents.models import AgentTask, AgentTaskResult, TaskStatus


@dataclass(slots=True)
class InMemoryTaskManager:
    _tasks: dict[str, AgentTask] = field(default_factory=dict)

    def create_task(self, task: AgentTask) -> AgentTask:
        task_id = task.task_id or f"task-{uuid4().hex[:8]}"
        stored = AgentTask(
            task_id=task_id,
            description=task.description,
            assigned_agent_id=task.assigned_agent_id,
            priority=task.priority,
            status=TaskStatus.PENDING,
            max_retries=task.max_retries,
            dependencies=task.dependencies,
        )
        self._tasks[task_id] = stored
        return stored

    def assign_task(self, task_id: str, agent_id: str) -> AgentTask:
        task = self._tasks.get(task_id)
        if task is None:
            msg = f"Task not found: {task_id}"
            raise KeyError(msg)
        updated = AgentTask(
            task_id=task.task_id,
            description=task.description,
            assigned_agent_id=agent_id,
            priority=task.priority,
            status=TaskStatus.ASSIGNED,
            max_retries=task.max_retries,
            dependencies=task.dependencies,
            created_at=task.created_at,
        )
        self._tasks[task_id] = updated
        return updated

    def complete_task(self, task_id: str, result: AgentTaskResult) -> AgentTask:
        task = self._tasks.get(task_id)
        if task is None:
            msg = f"Task not found: {task_id}"
            raise KeyError(msg)
        updated = task.with_status(TaskStatus.COMPLETED).with_result(result)
        self._tasks[task_id] = updated
        return updated

    def fail_task(self, task_id: str, error: str) -> AgentTask:
        task = self._tasks.get(task_id)
        if task is None:
            msg = f"Task not found: {task_id}"
            raise KeyError(msg)
        result = AgentTaskResult(success=False, output="", error_message=error)
        if task.retry_count < task.max_retries:
            updated = task.increment_retry().with_status(TaskStatus.RETRY).with_result(result)
        else:
            updated = task.with_status(TaskStatus.FAILED).with_result(result)
        self._tasks[task_id] = updated
        return updated

    def retry_task(self, task_id: str) -> AgentTask:
        task = self._tasks.get(task_id)
        if task is None:
            msg = f"Task not found: {task_id}"
            raise KeyError(msg)
        updated = AgentTask(
            task_id=task.task_id,
            description=task.description,
            assigned_agent_id=task.assigned_agent_id,
            priority=task.priority,
            status=TaskStatus.PENDING,
            retry_count=task.retry_count + 1,
            max_retries=task.max_retries,
            dependencies=task.dependencies,
            result=task.result,
            created_at=task.created_at,
        )
        self._tasks[task_id] = updated
        return updated

    def get_task(self, task_id: str) -> AgentTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> tuple[AgentTask, ...]:
        return tuple(self._tasks.values())

    def list_tasks_by_agent(self, agent_id: str) -> tuple[AgentTask, ...]:
        return tuple(t for t in self._tasks.values() if t.assigned_agent_id == agent_id)

    def list_tasks_by_status(self, status: str) -> tuple[AgentTask, ...]:
        return tuple(t for t in self._tasks.values() if t.status.value == status)
