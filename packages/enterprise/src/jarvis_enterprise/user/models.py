"""User administration domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class UserStatus(StrEnum):
    invited = "invited"
    active = "active"
    suspended = "suspended"
    deactivated = "deactivated"


class InvitationStatus(StrEnum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    revoked = "revoked"


@dataclass(frozen=True, slots=True)
class EnterpriseUser:
    id: str = ""
    email: str = ""
    display_name: str = ""
    status: UserStatus = UserStatus.active
    org_ids: tuple[UUID, ...] = ()
    roles: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class Invitation:
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    org_id: UUID = field(default_factory=uuid4)
    role: str = "member"
    invited_by: str = ""
    status: InvitationStatus = InvitationStatus.pending
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class AccessReview:
    id: UUID = field(default_factory=uuid4)
    org_id: UUID = field(default_factory=uuid4)
    reviewer_id: str = ""
    target_user_id: str = ""
    reviewed_at: datetime | None = None
    approved: bool = False
    notes: str = ""
