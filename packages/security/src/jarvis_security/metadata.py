from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import Enum, auto
from uuid import uuid4


class SecurityObjectType(Enum):
    USER = auto()
    AGENT = auto()
    EXTENSION = auto()
    SERVICE = auto()
    ORGANIZATION = auto()
    WORKSPACE = auto()
    DEVICE = auto()
    ROLE = auto()
    PERMISSION = auto()
    POLICY = auto()
    SESSION = auto()
    SECURITY_CONTEXT = auto()
    AUDIT_EVENT = auto()
    TRUST_RELATIONSHIP = auto()
    SECRET_REFERENCE = auto()
    COMPLIANCE_CONTROL = auto()
    COMPLIANCE_ASSESSMENT = auto()
    AUTHENTICATION_RESULT = auto()
    AUTHORIZATION_DECISION = auto()


class SecurityStatus(Enum):
    DRAFT = auto()
    ACTIVE = auto()
    SUSPENDED = auto()
    DISABLED = auto()
    ARCHIVED = auto()
    DELETED = auto()


@dataclass(frozen=True, slots=True)
class SecurityMetadata:
    identifier: str
    object_type: SecurityObjectType
    owner_identifier: str
    workspace_identifier: str | None
    organization_identifier: str | None
    status: SecurityStatus
    created_timestamp: datetime
    updated_timestamp: datetime
    policy_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("identifier cannot be empty")
        if not self.owner_identifier.strip():
            raise ValueError("owner_identifier cannot be empty")
        if self.created_timestamp.tzinfo is None:
            raise ValueError("created_timestamp must be timezone-aware")
        if self.updated_timestamp.tzinfo is None:
            raise ValueError("updated_timestamp must be timezone-aware")
        if self.updated_timestamp < self.created_timestamp:
            raise ValueError("updated_timestamp cannot be before created_timestamp")

    def touch(self, at: datetime | None = None) -> SecurityMetadata:
        touched_at = at if at is not None else datetime.now(tz=UTC)
        return replace(self, updated_timestamp=touched_at)

    def with_status(self, status: SecurityStatus, at: datetime | None = None) -> SecurityMetadata:
        status_updated_at = at if at is not None else datetime.now(tz=UTC)
        return replace(self, status=status, updated_timestamp=status_updated_at)


def new_metadata(
    *,
    object_type: SecurityObjectType,
    owner_identifier: str,
    identifier: str | None = None,
    workspace_identifier: str | None = None,
    organization_identifier: str | None = None,
    status: SecurityStatus = SecurityStatus.ACTIVE,
    policy_references: tuple[str, ...] = (),
    created_at: datetime | None = None,
) -> SecurityMetadata:
    now = created_at if created_at is not None else datetime.now(tz=UTC)
    resolved_identifier = identifier if identifier is not None else f"sec-{uuid4().hex}"
    return SecurityMetadata(
        identifier=resolved_identifier,
        object_type=object_type,
        owner_identifier=owner_identifier,
        workspace_identifier=workspace_identifier,
        organization_identifier=organization_identifier,
        status=status,
        created_timestamp=now,
        updated_timestamp=now,
        policy_references=policy_references,
    )
