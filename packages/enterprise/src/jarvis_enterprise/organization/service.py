"""Organization management service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.organization.models import (
    Organization,
    OrganizationHierarchy,
    OrganizationMember,
    OrganizationStatus,
    OrgUnit,
    OrgUnitType,
)
from jarvis_enterprise.organization.repository import OrganizationRepository


class OrganizationService:
    def __init__(self, repository: OrganizationRepository) -> None:
        self._repository = repository

    def create_organization(self, name: str, display_name: str = "", description: str = "") -> Organization:
        org = Organization(name=name, display_name=display_name or name, description=description)
        root = OrgUnit(name=name, type=OrgUnitType.organization)
        org = Organization(id=org.id, name=org.name, display_name=org.display_name, description=org.description, units=(root,))
        self._repository.save(org)
        return org

    def get_organization(self, org_id: UUID) -> Organization | None:
        return self._repository.get(org_id)

    def suspend_organization(self, org_id: UUID) -> Organization | None:
        org = self._repository.get(org_id)
        if org is None:
            return None
        updated = Organization(
            id=org.id, name=org.name, display_name=org.display_name, description=org.description,
            status=OrganizationStatus.suspended, units=org.units, tags=org.tags, metadata=org.metadata,
            created_at=org.created_at,
        )
        self._repository.save(updated)
        return updated

    def archive_organization(self, org_id: UUID) -> Organization | None:
        org = self._repository.get(org_id)
        if org is None:
            return None
        updated = Organization(
            id=org.id, name=org.name, display_name=org.display_name, description=org.description,
            status=OrganizationStatus.archived, units=org.units, tags=org.tags, metadata=org.metadata,
            created_at=org.created_at,
        )
        self._repository.save(updated)
        return updated

    def list_organizations(self) -> list[Organization]:
        return self._repository.list()

    def add_unit(self, org_id: UUID, name: str, unit_type: OrgUnitType, parent_id: UUID | None = None) -> OrgUnit | None:
        org = self._repository.get(org_id)
        if org is None:
            return None
        unit = OrgUnit(name=name, type=unit_type, parent_id=parent_id)
        org = Organization(
            id=org.id, name=org.name, display_name=org.display_name, description=org.description,
            status=org.status, units=(*org.units, unit), tags=org.tags, metadata=org.metadata,
            created_at=org.created_at,
        )
        self._repository.save(org)
        return unit

    def add_member(self, org_id: UUID, user_id: str, role: str = "member") -> OrganizationMember | None:
        org = self._repository.get(org_id)
        if org is None:
            return None
        member = OrganizationMember(org_id=org_id, user_id=user_id, role=role)
        self._repository.add_member(org_id, member)
        return member

    def remove_member(self, org_id: UUID, user_id: str) -> bool:
        org = self._repository.get(org_id)
        if org is None:
            return False
        self._repository.remove_member(org_id, user_id)
        return True

    def get_members(self, org_id: UUID) -> list[OrganizationMember]:
        return self._repository.get_members(org_id)
