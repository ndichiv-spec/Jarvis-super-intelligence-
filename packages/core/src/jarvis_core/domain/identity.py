from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import DomainIdentifier, Email, Timestamp


class SessionState(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class Permission:
    key: str


@dataclass(frozen=True, slots=True)
class Role:
    name: str
    permissions: tuple[Permission, ...]


@dataclass(frozen=True, slots=True)
class Profile:
    display_name: str
    timezone: str


@dataclass(frozen=True, slots=True)
class Preference:
    key: str
    value: str


@dataclass(frozen=True, slots=True)
class Device:
    name: str
    fingerprint: str


@dataclass(slots=True)
class User(AggregateRoot):
    email: Email
    profile: Profile
    roles: tuple[Role, ...]
    preferences: tuple[Preference, ...]
    devices: tuple[Device, ...]


@dataclass(frozen=True, slots=True)
class Session:
    id: DomainIdentifier
    user_id: DomainIdentifier
    created_at: Timestamp
    state: SessionState


class IdentityRepository(Protocol):
    def save_user(self, user: User) -> None: ...

    def get_user(self, user_id: DomainIdentifier) -> User | None: ...


class AuthenticationPort(Protocol):
    def hash_secret(self, secret: str) -> str: ...


class IdentityService:
    def can(self, user: User, permission_key: str) -> bool:
        return any(
            permission_key == permission.key
            for role in user.roles
            for permission in role.permissions
        )


@dataclass(frozen=True, slots=True)
class UserRegistered(DomainEvent):
    email: Email
