from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class SecretKind(Enum):
    API_KEY = auto()
    TOKEN = auto()
    CERTIFICATE = auto()
    SIGNING_KEY = auto()
    ENCRYPTION_KEY = auto()


@dataclass(frozen=True, slots=True)
class SecretReference:
    metadata: SecurityMetadata
    kind: SecretKind
    name: str
    description: str
    rotation_interval_days: int | None = None

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.SECRET_REFERENCE:
            raise ValueError("metadata.object_type must be secret_reference")
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.description.strip():
            raise ValueError("description cannot be empty")
        if self.rotation_interval_days is not None and self.rotation_interval_days <= 0:
            raise ValueError("rotation_interval_days must be positive")

    @classmethod
    def create(
        cls,
        *,
        kind: SecretKind,
        name: str,
        description: str,
        owner_identifier: str,
        workspace_identifier: str | None,
        organization_identifier: str | None,
        rotation_interval_days: int | None = None,
    ) -> SecretReference:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.SECRET_REFERENCE,
                owner_identifier=owner_identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
            ),
            kind=kind,
            name=name,
            description=description,
            rotation_interval_days=rotation_interval_days,
        )


class SecretManagerContract(Protocol):
    def create_secret(self, reference: SecretReference, value: str) -> None:
        ...

    def get_secret(self, reference_identifier: str) -> str | None:
        ...

    def rotate_secret(self, reference_identifier: str, new_value: str) -> None:
        ...

    def revoke_secret(self, reference_identifier: str) -> None:
        ...
