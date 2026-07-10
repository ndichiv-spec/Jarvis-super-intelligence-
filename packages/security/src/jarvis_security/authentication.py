from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Protocol

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class AuthenticationMethod(Enum):
    PASSWORD = auto()
    PASSKEY = auto()
    OAUTH2 = auto()
    OPENID_CONNECT = auto()
    SAML = auto()
    API_KEY = auto()
    SERVICE_ACCOUNT = auto()
    MULTI_FACTOR = auto()


@dataclass(frozen=True, slots=True)
class AuthenticationFactor:
    name: str
    evidence: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.evidence.strip():
            raise ValueError("evidence cannot be empty")


@dataclass(frozen=True, slots=True)
class AuthenticationRequest:
    identity_identifier: str
    method: AuthenticationMethod
    factors: tuple[AuthenticationFactor, ...] = ()
    workspace_identifier: str | None = None
    organization_identifier: str | None = None
    session_identifier: str | None = None

    def __post_init__(self) -> None:
        if not self.identity_identifier.strip():
            raise ValueError("identity_identifier cannot be empty")


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    metadata: SecurityMetadata
    authenticated: bool
    identity_identifier: str
    method: AuthenticationMethod
    assurance_level: int
    issued_at: datetime
    expires_at: datetime | None = None
    failure_reason: str | None = None

    @classmethod
    def accepted(
        cls,
        *,
        identity_identifier: str,
        method: AuthenticationMethod,
        owner_identifier: str,
        assurance_level: int,
        issued_at: datetime,
        expires_at: datetime | None = None,
    ) -> AuthenticationResult:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.AUTHENTICATION_RESULT,
                owner_identifier=owner_identifier,
                workspace_identifier=None,
                organization_identifier=None,
            ),
            authenticated=True,
            identity_identifier=identity_identifier,
            method=method,
            assurance_level=assurance_level,
            issued_at=issued_at,
            expires_at=expires_at,
        )

    @classmethod
    def rejected(
        cls,
        *,
        identity_identifier: str,
        method: AuthenticationMethod,
        owner_identifier: str,
        issued_at: datetime,
        reason: str,
    ) -> AuthenticationResult:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.AUTHENTICATION_RESULT,
                owner_identifier=owner_identifier,
                workspace_identifier=None,
                organization_identifier=None,
            ),
            authenticated=False,
            identity_identifier=identity_identifier,
            method=method,
            assurance_level=0,
            issued_at=issued_at,
            failure_reason=reason,
        )


class AuthenticationProviderContract(Protocol):
    provider_name: str

    def supports(self, method: AuthenticationMethod) -> bool:
        ...

    def authenticate(self, request: AuthenticationRequest) -> AuthenticationResult:
        ...


class SessionIssuerContract(Protocol):
    def issue_session(
        self,
        *,
        identity_identifier: str,
        workspace_identifier: str | None,
        organization_identifier: str | None,
    ) -> str:
        ...
