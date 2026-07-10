"""Tests for Organization Management."""

from uuid import uuid4

from jarvis_enterprise.organization.models import (
    Organization,
    OrganizationHierarchy,
    OrganizationMember,
    OrganizationStatus,
    OrgUnit,
    OrgUnitType,
)
from jarvis_enterprise.organization.repository import OrganizationRepository
from jarvis_enterprise.organization.service import OrganizationService


class InMemoryOrgRepository:
    def __init__(self):
        self._orgs: dict = {}
        self._members: dict = {}

    def save(self, org: Organization) -> None:
        self._orgs[org.id] = org

    def get(self, org_id) -> Organization | None:
        return self._orgs.get(org_id)

    def delete(self, org_id) -> None:
        self._orgs.pop(org_id, None)

    def list(self) -> list[Organization]:
        return list(self._orgs.values())

    def add_member(self, org_id, member) -> None:
        self._members.setdefault(org_id, []).append(member)

    def remove_member(self, org_id, user_id) -> None:
        self._members[org_id] = [m for m in self._members.get(org_id, []) if m.user_id != user_id]

    def get_members(self, org_id) -> list[OrganizationMember]:
        return list(self._members.get(org_id, []))


class TestOrganizationModels:
    def test_create_organization(self):
        org = Organization(name="Acme Corp", display_name="Acme Corporation")
        assert org.name == "Acme Corp"
        assert org.status == OrganizationStatus.active

    def test_create_org_unit(self):
        unit = OrgUnit(name="Engineering", type=OrgUnitType.department)
        assert unit.type == OrgUnitType.department

    def test_create_member(self):
        member = OrganizationMember(org_id=uuid4(), user_id="user1", role="admin")
        assert member.role == "admin"


class TestOrganizationService:
    def setup_method(self):
        self.repo = OrganizationService(InMemoryOrgRepository())

    def test_create_and_get(self):
        org = self.repo.create_organization("TestOrg")
        fetched = self.repo.get_organization(org.id)
        assert fetched is not None
        assert fetched.name == "TestOrg"

    def test_create_multiple(self):
        self.repo.create_organization("Org1")
        self.repo.create_organization("Org2")
        assert len(self.repo.list_organizations()) == 2

    def test_suspend(self):
        org = self.repo.create_organization("Test")
        suspended = self.repo.suspend_organization(org.id)
        assert suspended is not None
        assert suspended.status == OrganizationStatus.suspended

    def test_archive(self):
        org = self.repo.create_organization("Test")
        archived = self.repo.archive_organization(org.id)
        assert archived is not None
        assert archived.status == OrganizationStatus.archived

    def test_get_nonexistent(self):
        assert self.repo.get_organization(uuid4()) is None

    def test_add_unit(self):
        org = self.repo.create_organization("Test")
        unit = self.repo.add_unit(org.id, "Engineering", OrgUnitType.department)
        assert unit is not None
        assert unit.name == "Engineering"

    def test_add_remove_member(self):
        org = self.repo.create_organization("Test")
        member = self.repo.add_member(org.id, "user1", "admin")
        assert member is not None
        assert len(self.repo.get_members(org.id)) == 1
        self.repo.remove_member(org.id, "user1")
        assert len(self.repo.get_members(org.id)) == 0

    def test_add_member_nonexistent_org(self):
        assert self.repo.add_member(uuid4(), "user1") is None
