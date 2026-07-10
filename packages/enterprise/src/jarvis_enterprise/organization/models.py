"""Organization domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class OrganizationStatus(StrEnum):
    active = "active"
    suspended = "suspended"
    archived = "archived"
    deleted = "deleted"


class OrgUnitType(StrEnum):
    organization = "organization"
    division = "division"
    department = "department"
    team = "team"
    business_unit = "business_unit"


@dataclass(frozen=True, slots=True)
class OrgUnit:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    type: OrgUnitType = OrgUnitType.organization
    parent_id: UUID | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class Organization:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    description: str = ""
    status: OrganizationStatus = OrganizationStatus.active
    units: tuple[OrgUnit, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class OrganizationHierarchy:
    root: OrgUnit
    children: tuple[OrganizationHierarchy, ...] = ()


@dataclass(frozen=True, slots=True)
class OrganizationMember:
    org_id: UUID
    user_id: str
    role: str = "member"
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
