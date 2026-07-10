"""Business continuity domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class RunbookCategory(StrEnum):
    backup = "backup"
    recovery = "recovery"
    incident = "incident"
    maintenance = "maintenance"
    onboarding = "onboarding"


class IncidentResponsePhase(StrEnum):
    detection = "detection"
    assessment = "assessment"
    containment = "containment"
    eradication = "eradication"
    recovery = "recovery"
    post_mortem = "post_mortem"


@dataclass(frozen=True, slots=True)
class Runbook:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    category: RunbookCategory = RunbookCategory.maintenance
    description: str = ""
    steps: tuple[str, ...] = ()
    owner: str = ""
    reviewed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class IncidentResponsePlan:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    severity: str = "medium"
    phases: tuple[IncidentResponsePhase, ...] = ()
    procedures: dict[str, str] = field(default_factory=dict)
    owners: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RecoveryProcedure:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    target: str = ""
    steps: tuple[str, ...] = ()
    estimated_rto_minutes: int = 60
    estimated_rpo_minutes: int = 60
    verified: bool = False
    last_tested: datetime | None = None


@dataclass(frozen=True, slots=True)
class BackupValidation:
    id: UUID = field(default_factory=uuid4)
    backup_name: str = ""
    validated: bool = False
    size_bytes: int = 0
    checksum: str = ""
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
