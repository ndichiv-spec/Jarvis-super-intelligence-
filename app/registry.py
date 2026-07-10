"""Service Registry — register, discover, and query every platform component."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from app.health import HealthStatus


class ServiceStatus(StrEnum):
    registered = "registered"
    initializing = "initializing"
    running = "running"
    degraded = "degraded"
    stopped = "stopped"
    failed = "failed"


@dataclass(frozen=True, slots=True)
class ServiceHandle:
    id: str = ""
    name: str = ""
    version: str = "0.1.0"
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    status: ServiceStatus = ServiceStatus.registered
    health: HealthStatus = HealthStatus.unknown
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class ServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[str, ServiceHandle] = {}

    def register(self, handle: ServiceHandle) -> ServiceHandle:
        if handle.id in self._services:
            raise ValueError(f"Service '{handle.id}' already registered")
        self._services[handle.id] = handle
        return handle

    def get(self, service_id: str) -> ServiceHandle | None:
        return self._services.get(service_id)

    def list(self) -> list[ServiceHandle]:
        return list(self._services.values())

    def update_status(self, service_id: str, status: ServiceStatus) -> ServiceHandle | None:
        svc = self._services.get(service_id)
        if svc is None:
            raise ValueError(f"Service '{service_id}' not found")
        updated = ServiceHandle(
            id=svc.id, name=svc.name, version=svc.version,
            capabilities=svc.capabilities, dependencies=svc.dependencies,
            status=status, health=svc.health, metadata=svc.metadata,
            registered_at=svc.registered_at,
        )
        self._services[service_id] = updated
        return updated

    def update_health(self, service_id: str, health: HealthStatus) -> ServiceHandle | None:
        svc = self._services.get(service_id)
        if svc is None:
            return None
        updated = ServiceHandle(
            id=svc.id, name=svc.name, version=svc.version,
            capabilities=svc.capabilities, dependencies=svc.dependencies,
            status=svc.status, health=health, metadata=svc.metadata,
            registered_at=svc.registered_at,
        )
        self._services[service_id] = updated
        return updated

    def count(self) -> int:
        return len(self._services)

    def get_dependency_graph(self) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}
        for svc in self._services.values():
            graph[svc.id] = list(svc.dependencies)
        return graph

    def resolve_startup_order(self) -> list[str]:
        graph = self.get_dependency_graph()
        visited: set[str] = set()
        in_progress: set[str] = set()
        order: list[str] = []
        for node in list(graph.keys()):
            if node not in visited:
                self._topological_sort(node, graph, visited, in_progress, order)
        return order

    def _topological_sort(self, node: str, graph: dict[str, list[str]], visited: set[str], in_progress: set[str], order: list[str]) -> None:
        if node in in_progress:
            raise ValueError(f"Circular dependency detected involving '{node}'")
        if node in visited:
            return
        in_progress.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                self._topological_sort(dep, graph, visited, in_progress, order)
        in_progress.discard(node)
        visited.add(node)
        order.append(node)
