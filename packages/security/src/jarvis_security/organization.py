from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum, auto

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class OrganizationUnitType(Enum):
    ORGANIZATION = auto()
    DEPARTMENT = auto()
    TEAM = auto()
    PROJECT = auto()


@dataclass(frozen=True, slots=True)
class OrganizationUnit:
    metadata: SecurityMetadata
    name: str
    unit_type: OrganizationUnitType
    parent_identifier: str | None = None
    delegated_to: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.ORGANIZATION:
            raise ValueError("metadata.object_type must be organization")
        if not self.name.strip():
            raise ValueError("name cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        identifier: str,
        owner_identifier: str,
        name: str,
        unit_type: OrganizationUnitType,
        parent_identifier: str | None = None,
    ) -> OrganizationUnit:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.ORGANIZATION,
                owner_identifier=owner_identifier,
                identifier=identifier,
                organization_identifier=identifier,
            ),
            name=name,
            unit_type=unit_type,
            parent_identifier=parent_identifier,
        )


@dataclass(frozen=True, slots=True)
class OrganizationMembership:
    metadata: SecurityMetadata
    identity_identifier: str
    unit_identifier: str
    role_name: str
    delegated: bool = False

    def __post_init__(self) -> None:
        if not self.identity_identifier.strip():
            raise ValueError("identity_identifier cannot be empty")
        if not self.unit_identifier.strip():
            raise ValueError("unit_identifier cannot be empty")
        if not self.role_name.strip():
            raise ValueError("role_name cannot be empty")


@dataclass(slots=True)
class OrganizationModel:
    _units: dict[str, OrganizationUnit] = field(default_factory=dict)
    _memberships_by_identity: dict[str, list[OrganizationMembership]] = field(
        default_factory=dict,
    )

    def register_unit(self, unit: OrganizationUnit) -> OrganizationUnit:
        self._units[unit.metadata.identifier] = unit
        return unit

    def get_unit(self, unit_identifier: str) -> OrganizationUnit | None:
        return self._units.get(unit_identifier)

    def list_units(self) -> tuple[OrganizationUnit, ...]:
        return tuple(self._units.values())

    def add_membership(
        self,
        *,
        identity_identifier: str,
        unit_identifier: str,
        role_name: str,
        owner_identifier: str,
        delegated: bool = False,
    ) -> OrganizationMembership:
        if unit_identifier not in self._units:
            raise KeyError(f"Unknown organization unit: {unit_identifier}")
        membership = OrganizationMembership(
            metadata=new_metadata(
                object_type=SecurityObjectType.ORGANIZATION,
                owner_identifier=owner_identifier,
                organization_identifier=self._root_identifier(unit_identifier),
            ),
            identity_identifier=identity_identifier,
            unit_identifier=unit_identifier,
            role_name=role_name,
            delegated=delegated,
        )
        self._memberships_by_identity.setdefault(identity_identifier, []).append(membership)
        return membership

    def list_memberships(self, identity_identifier: str) -> tuple[OrganizationMembership, ...]:
        return tuple(self._memberships_by_identity.get(identity_identifier, []))

    def is_member(self, identity_identifier: str, unit_identifier: str) -> bool:
        memberships = self._memberships_by_identity.get(identity_identifier, [])
        for membership in memberships:
            if membership.unit_identifier == unit_identifier:
                return True
            if unit_identifier in self._ancestor_identifiers(membership.unit_identifier):
                return True
        return False

    def lineage(self, unit_identifier: str) -> tuple[OrganizationUnit, ...]:
        lineage_items: list[OrganizationUnit] = []
        current = self._units.get(unit_identifier)
        while current is not None:
            lineage_items.append(current)
            parent_identifier = current.parent_identifier
            current = self._units.get(parent_identifier) if parent_identifier is not None else None
        return tuple(lineage_items)

    def delegate_unit(self, unit_identifier: str, delegate_identity: str) -> OrganizationUnit:
        unit = self._units.get(unit_identifier)
        if unit is None:
            raise KeyError(f"Unknown organization unit: {unit_identifier}")
        if delegate_identity in unit.delegated_to:
            return unit
        updated = replace(unit, delegated_to=(*unit.delegated_to, delegate_identity))
        self._units[unit_identifier] = updated
        return updated

    def _ancestor_identifiers(self, unit_identifier: str) -> tuple[str, ...]:
        identifiers: list[str] = []
        current = self._units.get(unit_identifier)
        while current is not None and current.parent_identifier is not None:
            identifiers.append(current.parent_identifier)
            current = self._units.get(current.parent_identifier)
        return tuple(identifiers)

    def _root_identifier(self, unit_identifier: str) -> str:
        current = self._units.get(unit_identifier)
        if current is None:
            return unit_identifier
        while current.parent_identifier is not None:
            parent = self._units.get(current.parent_identifier)
            if parent is None:
                return current.parent_identifier
            current = parent
        return current.metadata.identifier
