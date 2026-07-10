from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class AdapterStatus(StrEnum):
    REGISTERED = "registered"
    CONFIGURED = "configured"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class AdapterMetadata:
    identifier: str
    version: str
    provider: str
    capabilities: tuple[str, ...]
    configuration_profile: str
    compatibility: tuple[str, ...]
    status: AdapterStatus = AdapterStatus.REGISTERED

    def with_status(self, status: AdapterStatus) -> AdapterMetadata:
        return replace(self, status=status)
