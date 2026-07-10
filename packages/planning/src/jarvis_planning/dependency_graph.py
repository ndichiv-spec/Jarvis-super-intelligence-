from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generator

from jarvis_planning.decomposer import Task


class CycleError(Exception):
    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        super().__init__(f"Dependency cycle detected: {' -> '.join(cycle)}")


@dataclass
class DependencyGraph:
    tasks: dict[str, Task] = field(default_factory=dict)
    edges: dict[str, list[str]] = field(default_factory=dict)

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task
        self.edges[task.id] = list(task.dependencies)

    def add_tasks(self, tasks: list[Task]) -> None:
        for t in tasks:
            self.add_task(t)

    def get_dependencies(self, task_id: str) -> list[str]:
        return self.edges.get(task_id, [])

    def get_dependents(self, task_id: str) -> list[str]:
        return [tid for tid, deps in self.edges.items() if task_id in deps]

    def get_all_dependencies(self, task_id: str) -> set[str]:
        result: set[str] = set()
        def _walk(tid: str) -> None:
            for dep in self.edges.get(tid, []):
                if dep not in result:
                    result.add(dep)
                    _walk(dep)
        _walk(task_id)
        return result

    def get_all_dependents(self, task_id: str) -> set[str]:
        result: set[str] = set()
        def _walk(tid: str) -> None:
            for dep in self.get_dependents(tid):
                if dep not in result:
                    result.add(dep)
                    _walk(dep)
        _walk(task_id)
        return result

    def topological_sort(self) -> list[str]:
        in_degree: dict[str, int] = {tid: 0 for tid in self.tasks}
        for tid, deps in self.edges.items():
            in_degree[tid] = len(deps)
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result: list[str] = []
        while queue:
            tid = queue.pop(0)
            result.append(tid)
            for dependent in self.get_dependents(tid):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        if len(result) != len(self.tasks):
            remaining = set(self.tasks) - set(result)
            raise CycleError(list(remaining))
        return result

    def get_levels(self) -> list[list[str]]:
        in_degree: dict[str, int] = {tid: len(self.edges.get(tid, [])) for tid in self.tasks}
        levels: list[list[str]] = []
        remaining = set(self.tasks)
        while remaining:
            current_level = [tid for tid in remaining if in_degree.get(tid, 0) == 0]
            if not current_level:
                raise CycleError(list(remaining))
            levels.append(current_level)
            for tid in current_level:
                remaining.remove(tid)
                for dependent in self.get_dependents(tid):
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
        return levels

    def critical_path(self) -> list[str]:
        earliest: dict[str, float] = {}
        for tid in self.topological_sort():
            task = self.tasks[tid]
            max_prev = 0.0
            for dep in self.edges.get(tid, []):
                max_prev = max(max_prev, earliest.get(dep, 0.0) + self.tasks[dep].estimated_effort_hours)
            earliest[tid] = max_prev

        latest: dict[str, float] = {}
        total_duration = max((earliest.get(tid, 0.0) + self.tasks[tid].estimated_effort_hours for tid in self.tasks), default=0.0)
        for tid in reversed(self.topological_sort()):
            task = self.tasks[tid]
            if not self.get_dependents(tid):
                latest[tid] = total_duration - task.estimated_effort_hours
            else:
                min_next = float("inf")
                for dep in self.get_dependents(tid):
                    min_next = min(min_next, latest.get(dep, total_duration) - self.tasks[tid].estimated_effort_hours)
                latest[tid] = min_next

        critical: list[str] = []
        for tid in self.topological_sort():
            if abs(earliest[tid] - latest[tid]) < 0.001:
                critical.append(tid)
        return critical

    def validate_no_cycles(self) -> None:
        self.topological_sort()

    def subgraph(self, task_ids: set[str]) -> DependencyGraph:
        sub = DependencyGraph()
        for tid in task_ids:
            if tid in self.tasks:
                sub.add_task(self.tasks[tid])
        return sub

    def merge(self, other: DependencyGraph) -> None:
        for tid, task in other.tasks.items():
            if tid not in self.tasks:
                self.add_task(task)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "edges": {tid: list(deps) for tid, deps in self.edges.items()},
            "levels": [[{"id": tid, "title": self.tasks[tid].title} for tid in level] for level in self.get_levels()],
            "critical_path": [{"id": tid, "title": self.tasks[tid].title} for tid in self.critical_path()],
            "total_tasks": len(self.tasks),
        }
