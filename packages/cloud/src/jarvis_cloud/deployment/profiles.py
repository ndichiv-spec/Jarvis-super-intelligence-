"""Deployment profiles and environment definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class DeploymentEnvironment(StrEnum):
    development = "development"
    testing = "testing"
    staging = "staging"
    production = "production"


@dataclass(frozen=True)
class ServiceProfile:
    image: str
    tag: str
    replicas: int
    cpu_limit: str
    memory_limit: str
    cpu_request: str
    memory_request: str
    env: dict[str, str] = field(default_factory=dict)
    ports: list[int] = field(default_factory=list)
    health_check: dict[str, Any] = field(default_factory=lambda: {"path": "/health", "interval": 30, "timeout": 5})
    depends_on: list[str] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    config_refs: list[str] = field(default_factory=list)
    secret_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class InfrastructureProfile:
    postgres: dict[str, Any] | None = None
    redis: dict[str, Any] | None = None
    qdrant: dict[str, Any] | None = None
    minio: dict[str, Any] | None = None
    opentelemetry: dict[str, Any] | None = None
    prometheus: dict[str, Any] | None = None


@dataclass(frozen=True)
class DeploymentProfile:
    name: str
    environment: DeploymentEnvironment
    version: str
    services: dict[str, ServiceProfile] = field(default_factory=dict)
    infrastructure: InfrastructureProfile = field(default_factory=InfrastructureProfile)
    observability: dict[str, bool] = field(default_factory=lambda: {"metrics": True, "logs": True, "traces": False})
    scaling: dict[str, Any] = field(default_factory=dict)
    backup: dict[str, Any] = field(default_factory=lambda: {"enabled": False, "schedule": ""})
    network: dict[str, Any] = field(default_factory=lambda: {"ingress": False, "tls": False})
    labels: dict[str, str] = field(default_factory=dict)


PROFILES: dict[str, DeploymentProfile] = {}

_DEFAULT_SERVICES = {
    "api": ServiceProfile(
        image="jarvis/api",
        tag="latest",
        replicas=1,
        cpu_limit="500m",
        memory_limit="512Mi",
        cpu_request="250m",
        memory_request="256Mi",
        ports=[8000],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["postgres", "redis"],
        config_refs=["api-config"],
        secret_refs=["api-secrets"],
    ),
    "brain": ServiceProfile(
        image="jarvis/brain",
        tag="latest",
        replicas=1,
        cpu_limit="1000m",
        memory_limit="1Gi",
        cpu_request="500m",
        memory_request="512Mi",
        ports=[8100],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api", "redis"],
    ),
    "ai": ServiceProfile(
        image="jarvis/ai",
        tag="latest",
        replicas=1,
        cpu_limit="1000m",
        memory_limit="1Gi",
        cpu_request="500m",
        memory_request="512Mi",
        ports=[8200],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api"],
    ),
    "memory": ServiceProfile(
        image="jarvis/memory",
        tag="latest",
        replicas=1,
        cpu_limit="500m",
        memory_limit="512Mi",
        cpu_request="250m",
        memory_request="256Mi",
        ports=[8300],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api", "qdrant"],
    ),
    "knowledge": ServiceProfile(
        image="jarvis/knowledge",
        tag="latest",
        replicas=1,
        cpu_limit="500m",
        memory_limit="512Mi",
        cpu_request="250m",
        memory_request="256Mi",
        ports=[8400],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api", "qdrant"],
    ),
    "automation": ServiceProfile(
        image="jarvis/automation",
        tag="latest",
        replicas=1,
        cpu_limit="500m",
        memory_limit="512Mi",
        cpu_request="250m",
        memory_request="256Mi",
        ports=[8500],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api", "redis"],
    ),
    "agents": ServiceProfile(
        image="jarvis/agents",
        tag="latest",
        replicas=1,
        cpu_limit="500m",
        memory_limit="512Mi",
        cpu_request="250m",
        memory_request="256Mi",
        ports=[8600],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api"],
    ),
    "orchestration": ServiceProfile(
        image="jarvis/orchestration",
        tag="latest",
        replicas=1,
        cpu_limit="1000m",
        memory_limit="1Gi",
        cpu_request="500m",
        memory_request="512Mi",
        ports=[8700],
        health_check={"path": "/health", "interval": 15, "timeout": 5},
        depends_on=["api", "brain"],
    ),
}


def _build_profile(
    env: DeploymentEnvironment,
    version: str,
    replicas: int,
    cpu_limit: str,
    memory_limit: str,
) -> DeploymentProfile:
    services = {}
    for name, svc in _DEFAULT_SERVICES.items():
        services[name] = ServiceProfile(
            image=svc.image,
            tag=version,
            replicas=replicas,
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            cpu_request=svc.cpu_request,
            memory_request=svc.memory_request,
            env=svc.env,
            ports=svc.ports,
            health_check=svc.health_check,
            depends_on=svc.depends_on,
            volumes=svc.volumes,
            config_refs=svc.config_refs,
            secret_refs=svc.secret_refs,
        )
    return DeploymentProfile(name=env.value, environment=env, version=version, services=services)


PROFILES["development"] = _build_profile(
    DeploymentEnvironment.development, version="latest",
    replicas=1, cpu_limit="500m", memory_limit="512Mi",
)
PROFILES["testing"] = _build_profile(
    DeploymentEnvironment.testing, version="latest",
    replicas=1, cpu_limit="500m", memory_limit="512Mi",
)
PROFILES["staging"] = _build_profile(
    DeploymentEnvironment.staging, version="latest",
    replicas=2, cpu_limit="1000m", memory_limit="1Gi",
)
PROFILES["production"] = _build_profile(
    DeploymentEnvironment.production, version="latest",
    replicas=3, cpu_limit="1000m", memory_limit="1Gi",
)


class ProfileLoader:
    def load(self, name: str) -> DeploymentProfile:
        profile = PROFILES.get(name)
        if profile is None:
            raise ValueError(f"Unknown deployment profile: {name}")
        return profile

    def list_profiles(self) -> list[str]:
        return list(PROFILES.keys())

    def load_from_file(self, path: str) -> DeploymentProfile:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Profile file not found: {path}")
        data = json.loads(p.read_text()) if p.suffix == ".json" else _load_yaml(p)
        return _dict_to_profile(data)


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
        return yaml.safe_load(path.read_text())
    except ImportError:
        raise RuntimeError("PyYAML required for YAML profiles")


def _dict_to_profile(data: dict[str, Any]) -> DeploymentProfile:
    services = {}
    for name, svc in data.get("services", {}).items():
        services[name] = ServiceProfile(**svc)
    infra = InfrastructureProfile(**(data.get("infrastructure", {})))
    return DeploymentProfile(
        name=data["name"],
        environment=DeploymentEnvironment(data["environment"]),
        version=data.get("version", "latest"),
        services=services,
        infrastructure=infra,
        observability=data.get("observability", {}),
        scaling=data.get("scaling", {}),
        backup=data.get("backup", {}),
        network=data.get("network", {}),
        labels=data.get("labels", {}),
    )
