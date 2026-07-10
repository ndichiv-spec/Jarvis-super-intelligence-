"""Diagnostics — environment report, modules, config summary, timing, errors."""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.kernel import AppKernel


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    platform_info: dict[str, Any] = field(default_factory=dict)
    python_info: dict[str, Any] = field(default_factory=dict)
    config_summary: dict[str, Any] = field(default_factory=dict)
    services: list[dict[str, Any]] = field(default_factory=list)
    lifecycle: dict[str, Any] = field(default_factory=dict)
    health: dict[str, Any] = field(default_factory=dict)
    dependency_graph: dict[str, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def generate_report(kernel: AppKernel) -> DiagnosticReport:
    platform_info = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "hostname": platform.node(),
    }
    python_info = {
        "version": sys.version,
        "executable": sys.executable,
        "argv": sys.argv,
    }
    config_summary = {
        "profile": kernel.config.profile,
        "debug": kernel.config.debug,
        "log_level": kernel.config.log_level,
        "gateway_host": kernel.config.gateway_host,
        "gateway_port": kernel.config.gateway_port,
        "database_url": kernel.config.database_url,
        "redis_url": kernel.config.redis_url,
    }
    services = []
    for svc in kernel.registry.list():
        services.append({
            "id": svc.id,
            "name": svc.name,
            "version": svc.version,
            "status": svc.status.value,
            "health": svc.health.value,
            "capabilities": list(svc.capabilities),
        })
    lifecycle = {
        "state": kernel.lifecycle.state.value,
        "history": [{"from": e.from_state.value, "to": e.to_state.value, "reason": e.reason} for e in kernel.lifecycle.history],
    }
    health_report = kernel.get_health_report()
    health = {
        "platform": health_report.platform.value,
        "summary": health_report.summary,
        "checks": [{"subsystem": c.subsystem, "status": c.status.value, "message": c.message} for c in health_report.checks],
    }
    dependency_graph = kernel.registry.get_dependency_graph()
    warnings: list[str] = []
    if kernel.config.secret_key == "change-me-in-production":
        warnings.append("Default secret key in use — set JARVIS_APP__SECRET_KEY")
    return DiagnosticReport(
        platform_info=platform_info,
        python_info=python_info,
        config_summary=config_summary,
        services=services,
        lifecycle=lifecycle,
        health=health,
        dependency_graph=dependency_graph,
        warnings=warnings,
    )


def print_report(report: DiagnosticReport) -> None:
    import json
    print(json.dumps({
        "timestamp": report.timestamp.isoformat(),
        "platform": report.platform_info,
        "python": report.python_info,
        "config": report.config_summary,
        "services": report.services,
        "lifecycle": report.lifecycle,
        "health": report.health,
        "dependency_graph": report.dependency_graph,
        "warnings": report.warnings,
    }, indent=2, default=str))
