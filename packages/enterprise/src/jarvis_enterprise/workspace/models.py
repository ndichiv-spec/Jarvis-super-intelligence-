"""Workspace domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class WorkspaceStatus(StrEnum):
    active = "active"
    suspended = "suspended"
    archived = "archived"


class WorkspaceVisibility(StrEnum):
    private = "private"
    internal = "internal"
    shared = "shared"


@dataclass(frozen=True, slots=True)
class Workspace:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    name: str = ""
    display_name: str = ""
    description: str = ""
    status: WorkspaceStatus = WorkspaceStatus.active
    visibility: WorkspaceVisibility = WorkspaceVisibility.private
    owner_id: str = ""
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class WorkspaceMembership:
    workspace_id: UUID
    user_id: str
    role: str = "viewer"
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class Project:
    id: UUID = field(default_factory=uuid4)
    workspace_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    owner_id: str = ""
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class ResourceAllocation:
    workspace_id: UUID
    resource_type: str = ""
    allocated: int = 0
    used: int = 0
    limit: int = 0
