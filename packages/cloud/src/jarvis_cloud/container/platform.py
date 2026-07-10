"""Container Platform - production containerization definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImageBuildConfig:
    service_name: str
    dockerfile: str
    context: str
    target: str | None = None
    build_args: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=lambda: ["linux/amd64"])


BUILD_CONFIGS: dict[str, ImageBuildConfig] = {
    "api": ImageBuildConfig(
        service_name="api",
        dockerfile="docker/images/api.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/api:latest"],
    ),
    "brain": ImageBuildConfig(
        service_name="brain",
        dockerfile="docker/images/brain.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/brain:latest"],
    ),
    "ai": ImageBuildConfig(
        service_name="ai",
        dockerfile="docker/images/ai.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/ai:latest"],
    ),
    "memory": ImageBuildConfig(
        service_name="memory",
        dockerfile="docker/images/memory.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/memory:latest"],
    ),
    "knowledge": ImageBuildConfig(
        service_name="knowledge",
        dockerfile="docker/images/knowledge.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/knowledge:latest"],
    ),
    "automation": ImageBuildConfig(
        service_name="automation",
        dockerfile="docker/images/automation.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/automation:latest"],
    ),
    "agents": ImageBuildConfig(
        service_name="agents",
        dockerfile="docker/images/agents.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/agents:latest"],
    ),
    "orchestration": ImageBuildConfig(
        service_name="orchestration",
        dockerfile="docker/images/orchestration.Dockerfile",
        context=".",
        target="production",
        tags=["jarvis/orchestration:latest"],
    ),
}


class ContainerPlatform:
    def get_build_config(self, service: str) -> ImageBuildConfig:
        config = BUILD_CONFIGS.get(service)
        if config is None:
            raise ValueError(f"Unknown service: {service}. Known: {list(BUILD_CONFIGS.keys())}")
        return config

    def list_services(self) -> list[str]:
        return list(BUILD_CONFIGS.keys())

    def generate_dockerfile(self, service: str) -> str:
        config = self.get_build_config(service)
        return _DOCKERFILE_TEMPLATE.format(
            service=service,
            target=config.target or "production",
        )

    def generate_compose_service(self, service: str, version: str = "latest") -> dict[str, Any]:
        config = self.get_build_config(service)
        return {
            "image": f"jarvis/{service}:{version}",
            "build": {
                "context": config.context,
                "dockerfile": config.dockerfile,
                "target": config.target,
            },
            "ports": [],
            "healthcheck": {
                "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "40s",
            },
            "restart": "unless-stopped",
        }


_DOCKERFILE_TEMPLATE = """# syntax=docker/dockerfile:1
FROM python:3.13-slim AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group {service}

FROM base AS production

COPY --from=builder /app/.venv /app/.venv
COPY packages/{service}/src /app/src
COPY packages/core/src /app/src/core

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "src.{service}.app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS development

COPY . /workspace
WORKDIR /workspace
RUN pip install uv && uv sync --all-packages --group dev
CMD ["uv", "run", "uvicorn", "packages.{service}.src.{service}.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""
