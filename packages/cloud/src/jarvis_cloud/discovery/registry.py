"""Service Discovery - abstract registry for distributed service resolution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class ServiceHealth(StrEnum):
    unknown = "unknown"
    healthy = "healthy"
    degraded = "degraded"
    unhealthy = "unhealthy"


@dataclass(frozen=True)
class ServiceInstance:
    service_name: str
    instance_id: str
    host: str
    port: int
    protocol: str = "http"
    health: ServiceHealth = ServiceHealth.unknown
    metadata: dict[str, str] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ServiceEndpoint:
    service_name: str
    url: str
    instance_id: str | None = None
    weight: int = 1
    tags: list[str] = field(default_factory=list)


class ServiceRegistryContract(ABC):
    @abstractmethod
    def register(self, instance: ServiceInstance) -> None: ...

    @abstractmethod
    def deregister(self, service_name: str, instance_id: str) -> None: ...

    @abstractmethod
    def resolve(self, service_name: str, tags: list[str] | None = None) -> list[ServiceEndpoint]: ...

    @abstractmethod
    def resolve_one(self, service_name: str, tags: list[str] | None = None) -> ServiceEndpoint | None: ...

    @abstractmethod
    def list_services(self) -> list[str]: ...

    @abstractmethod
    def health(self, service_name: str) -> dict[str, ServiceHealth]: ...


class InMemoryServiceRegistry(ServiceRegistryContract):
    def __init__(self) -> None:
        self._instances: dict[str, dict[str, ServiceInstance]] = {}

    def register(self, instance: ServiceInstance) -> None:
        self._instances.setdefault(instance.service_name, {})[instance.instance_id] = instance

    def deregister(self, service_name: str, instance_id: str) -> None:
        svc = self._instances.get(service_name)
        if svc:
            svc.pop(instance_id, None)

    def resolve(self, service_name: str, tags: list[str] | None = None) -> list[ServiceEndpoint]:
        svc = self._instances.get(service_name, {})
        instances = list(svc.values())
        if tags:
            instances = [i for i in instances if any(t in i.tags for t in tags)]
        return [
            ServiceEndpoint(
                service_name=service_name,
                url=f"{i.protocol}://{i.host}:{i.port}",
                instance_id=i.instance_id,
                tags=i.tags,
            )
            for i in instances
            if i.health != ServiceHealth.unhealthy
        ]

    def resolve_one(self, service_name: str, tags: list[str] | None = None) -> ServiceEndpoint | None:
        endpoints = self.resolve(service_name, tags)
        return endpoints[0] if endpoints else None

    def list_services(self) -> list[str]:
        return list(self._instances.keys())

    def health(self, service_name: str) -> dict[str, ServiceHealth]:
        svc = self._instances.get(service_name, {})
        return {iid: inst.health for iid, inst in svc.items()}


class DnsServiceRegistry(ServiceRegistryContract):
    """DNS-based service discovery abstraction.

    In production, this would resolve via DNS SRV records or a
    service mesh sidecar (e.g., Consul, Istio, CoreDNS).
    """

    def __init__(self, domain: str = "jarvis.svc.cluster.local") -> None:
        self._domain = domain
        self._instances: dict[str, list[ServiceInstance]] = {}

    def register(self, instance: ServiceInstance) -> None:
        self._instances.setdefault(instance.service_name, []).append(instance)

    def deregister(self, service_name: str, instance_id: str) -> None:
        svc = self._instances.get(service_name, [])
        self._instances[service_name] = [i for i in svc if i.instance_id != instance_id]

    def resolve(self, service_name: str, tags: list[str] | None = None) -> list[ServiceEndpoint]:
        svc = self._instances.get(service_name, [])
        if not svc:
            return [ServiceEndpoint(service_name=service_name, url=f"http://{service_name}.{self._domain}:8000")]
        return [
            ServiceEndpoint(
                service_name=service_name,
                url=f"{i.protocol}://{i.host}:{i.port}",
                instance_id=i.instance_id,
                tags=i.tags,
            )
            for i in svc
        ]

    def resolve_one(self, service_name: str, tags: list[str] | None = None) -> ServiceEndpoint | None:
        endpoints = self.resolve(service_name, tags)
        return endpoints[0] if endpoints else None

    def list_services(self) -> list[str]:
        return list(self._instances.keys())

    def health(self, service_name: str) -> dict[str, ServiceHealth]:
        return {}


class ServiceRegistry:
    def __init__(self, backend: ServiceRegistryContract | None = None) -> None:
        self._backend = backend or InMemoryServiceRegistry()

    @property
    def backend(self) -> ServiceRegistryContract:
        return self._backend

    def register(self, service: str, instance_id: str, host: str, port: int, **kwargs: Any) -> None:
        self._backend.register(
            ServiceInstance(service_name=service, instance_id=instance_id, host=host, port=port, **kwargs)
        )

    def resolve(self, service: str) -> list[ServiceEndpoint]:
        return self._backend.resolve(service)

    def resolve_url(self, service: str) -> str | None:
        ep = self._backend.resolve_one(service)
        return ep.url if ep else None
