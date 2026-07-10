"""Application Kernel — central orchestrator with registry, lifecycle, health."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.configuration import AppConfig
from app.health import HealthMonitor, HealthReport, HealthStatus
from app.lifecycle import LifecycleManager, LifecycleState
from app.registry import ServiceHandle, ServiceRegistry


@dataclass(frozen=True, slots=True)
class KernelState:
    initialized: bool = False
    services_count: int = 0
    started_at: datetime | None = None
    version: str = "2.0.0"


class AppKernel:
    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or AppConfig()
        self._lifecycle = LifecycleManager()
        self._registry = ServiceRegistry()
        self._health = HealthMonitor()
        self._state = KernelState(version=self._config.extra.get("version", "2.0.0"))

    @property
    def config(self) -> AppConfig:
        return self._config

    @property
    def lifecycle(self) -> LifecycleManager:
        return self._lifecycle

    @property
    def registry(self) -> ServiceRegistry:
        return self._registry

    @property
    def health(self) -> HealthMonitor:
        return self._health

    @property
    def state(self) -> KernelState:
        return self._state

    def initialize(self) -> None:
        self._lifecycle.transition(LifecycleState.initializing, "Kernel initializing")
        self._register_platform_services()
        self._lifecycle.transition(LifecycleState.starting, "Platform services registered")

    def mark_ready(self) -> None:
        self._state = KernelState(
            initialized=True,
            services_count=self._registry.count(),
            started_at=datetime.now(UTC),
            version=self._state.version,
        )
        self._lifecycle.transition(LifecycleState.ready, "Platform ready")

    def mark_degraded(self, reason: str = "") -> None:
        self._lifecycle.transition(LifecycleState.degraded, reason or "Degraded state")

    def shutdown(self) -> None:
        self._lifecycle.transition(LifecycleState.stopping, "Shutdown requested")
        self._lifecycle.transition(LifecycleState.stopped, "Platform stopped")

    def fail(self, reason: str = "") -> None:
        self._lifecycle.transition(LifecycleState.failed, reason or "Failure")
        self._state = KernelState(
            initialized=self._state.initialized,
            services_count=self._state.services_count,
            started_at=self._state.started_at,
            version=self._state.version,
        )

    def get_health_report(self) -> HealthReport:
        return self._health.get_report()

    def _register_platform_services(self) -> None:
        platform_services: list[ServiceHandle] = [
            ServiceHandle(id="security", name="Security Platform", version="2.0.0", dependencies=(), capabilities=("authn", "authz", "rbac")),
            ServiceHandle(id="memory", name="Memory Platform", version="2.0.0", dependencies=("security",), capabilities=("store", "retrieve", "search")),
            ServiceHandle(id="knowledge", name="Knowledge Platform", version="2.0.0", dependencies=("security", "memory"), capabilities=("index", "search", "classify")),
            ServiceHandle(id="ai", name="AI Runtime", version="2.0.0", dependencies=("security",), capabilities=("inference", "embedding")),
            ServiceHandle(id="communication", name="Communication Platform", version="2.0.0", dependencies=("security",), capabilities=("events", "commands", "messaging")),
            ServiceHandle(id="automation", name="Automation Platform", version="2.0.0", dependencies=("security", "communication"), capabilities=("workflows", "triggers")),
            ServiceHandle(id="extensions", name="Extension Platform", version="2.0.0", dependencies=("security",), capabilities=("plugins", "lifecycle", "manifest")),
            ServiceHandle(id="infrastructure", name="Infrastructure Adapters", version="2.0.0", dependencies=(), capabilities=("database", "cache", "storage", "search")),
            ServiceHandle(id="gateway", name="Service Gateway", version="2.0.0", dependencies=("security", "infrastructure"), capabilities=("routing", "middleware", "protocols")),
            ServiceHandle(id="orchestration", name="Orchestration Engine", version="2.0.0", dependencies=("gateway", "automation"), capabilities=("coordination", "scheduling")),
            ServiceHandle(id="agents", name="Agents Platform", version="2.0.0", dependencies=("ai", "memory", "knowledge", "communication"), capabilities=("agent", "lifecycle", "tasks")),
            ServiceHandle(id="enterprise", name="Enterprise Platform", version="2.0.0", dependencies=("security", "gateway"), capabilities=("orgs", "workspaces", "governance")),
        ]
        for svc in platform_services:
            self._registry.register(svc)
            self._health.report(svc.id, HealthStatus.unknown, "Registered")
