from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from jarvis_security.identity import Identity
from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata
from jarvis_security.roles import Capability
from jarvis_security.trust import TrustLevel


class ExecutionContextType(Enum):
    INTERACTIVE = auto()
    AUTOMATION = auto()
    API = auto()
    EXTENSION = auto()
    SERVICE = auto()


@dataclass(frozen=True, slots=True)
class SessionContext:
    metadata: SecurityMetadata
    session_identifier: str
    issued_at: datetime
    expires_at: datetime | None
    source_ip: str | None = None
    user_agent: str | None = None

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.SESSION:
            raise ValueError("metadata.object_type must be session")
        if not self.session_identifier.strip():
            raise ValueError("session_identifier cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        session_identifier: str,
        owner_identifier: str,
        workspace_identifier: str | None,
        organization_identifier: str | None,
        issued_at: datetime,
        expires_at: datetime | None = None,
        source_ip: str | None = None,
        user_agent: str | None = None,
    ) -> SessionContext:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.SESSION,
                owner_identifier=owner_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
            session_identifier=session_identifier,
            issued_at=issued_at,
            expires_at=expires_at,
            source_ip=source_ip,
            user_agent=user_agent,
        )


@dataclass(frozen=True, slots=True)
class SecurityContext:
    metadata: SecurityMetadata
    identity: Identity
    role_names: tuple[str, ...]
    permission_keys: tuple[str, ...]
    capabilities: tuple[Capability, ...]
    workspace_identifier: str
    organization_identifier: str
    workspace_memberships: tuple[str, ...]
    organization_memberships: tuple[str, ...]
    session: SessionContext | None
    execution_context: ExecutionContextType
    trust_level: TrustLevel

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.SECURITY_CONTEXT:
            raise ValueError("metadata.object_type must be security_context")
        if not self.workspace_identifier.strip():
            raise ValueError("workspace_identifier cannot be empty")
        if not self.organization_identifier.strip():
            raise ValueError("organization_identifier cannot be empty")

    def has_permission(self, permission_key: str) -> bool:
        return permission_key in set(self.permission_keys)

    def has_capability(self, capability_key: str) -> bool:
        return capability_key in {capability.key for capability in self.capabilities}

    def policy_attributes(self) -> tuple[tuple[str, str], ...]:
        return (
            ("identity_id", self.identity.immutable_id),
            ("identity_type", self.identity.identity_type.name.lower()),
            ("workspace_id", self.workspace_identifier),
            ("organization_id", self.organization_identifier),
            ("trust_level", str(int(self.trust_level))),
        )
