from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class IdentityType(Enum):
    USER = auto()
    AGENT = auto()
    EXTENSION = auto()
    SERVICE = auto()
    ORGANIZATION = auto()
    WORKSPACE = auto()
    DEVICE = auto()


_OBJECT_TYPE_BY_IDENTITY: dict[IdentityType, SecurityObjectType] = {
    IdentityType.USER: SecurityObjectType.USER,
    IdentityType.AGENT: SecurityObjectType.AGENT,
    IdentityType.EXTENSION: SecurityObjectType.EXTENSION,
    IdentityType.SERVICE: SecurityObjectType.SERVICE,
    IdentityType.ORGANIZATION: SecurityObjectType.ORGANIZATION,
    IdentityType.WORKSPACE: SecurityObjectType.WORKSPACE,
    IdentityType.DEVICE: SecurityObjectType.DEVICE,
}


@dataclass(frozen=True, slots=True)
class IdentityAttribute:
    name: str
    value: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("attribute name cannot be empty")


@dataclass(frozen=True, slots=True)
class Identity:
    metadata: SecurityMetadata
    identity_type: IdentityType
    display_name: str
    attributes: tuple[IdentityAttribute, ...] = ()
    aliases: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise ValueError("display_name cannot be empty")
        expected_object_type = _OBJECT_TYPE_BY_IDENTITY[self.identity_type]
        if self.metadata.object_type is not expected_object_type:
            raise ValueError(
                "metadata.object_type must match identity_type "
                f"({expected_object_type.name.lower()})",
            )

    @property
    def immutable_id(self) -> str:
        return self.metadata.identifier

    def attribute(self, name: str) -> str | None:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute.value
        return None

    @classmethod
    def create(
        cls,
        *,
        identity_type: IdentityType,
        identifier: str,
        owner_identifier: str | None,
        display_name: str,
        workspace_identifier: str | None = None,
        organization_identifier: str | None = None,
        attributes: tuple[IdentityAttribute, ...] = (),
        aliases: tuple[str, ...] = (),
        tags: tuple[str, ...] = (),
        policy_references: tuple[str, ...] = (),
    ) -> Identity:
        resolved_owner = owner_identifier if owner_identifier is not None else identifier
        return cls(
            metadata=new_metadata(
                object_type=_OBJECT_TYPE_BY_IDENTITY[identity_type],
                owner_identifier=resolved_owner,
                identifier=identifier,
                workspace_identifier=workspace_identifier,
                organization_identifier=organization_identifier,
                policy_references=policy_references,
            ),
            identity_type=identity_type,
            display_name=display_name,
            attributes=attributes,
            aliases=aliases,
            tags=tags,
        )


class IdentityRegistryContract(Protocol):
    def register(self, identity: Identity) -> Identity:
        ...

    def get(self, identity_identifier: str) -> Identity | None:
        ...

    def list_identities(self) -> tuple[Identity, ...]:
        ...

    def exists(self, identity_identifier: str) -> bool:
        ...


@dataclass(slots=True)
class InMemoryIdentityRegistry(IdentityRegistryContract):
    _identities: dict[str, Identity] = field(default_factory=dict)

    def register(self, identity: Identity) -> Identity:
        self._identities[identity.immutable_id] = identity
        return identity

    def get(self, identity_identifier: str) -> Identity | None:
        return self._identities.get(identity_identifier)

    def list_identities(self) -> tuple[Identity, ...]:
        return tuple(self._identities.values())

    def exists(self, identity_identifier: str) -> bool:
        return identity_identifier in self._identities
