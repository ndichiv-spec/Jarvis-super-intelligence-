"""Tests for User Administration."""

from uuid import uuid4

from jarvis_enterprise.user.models import (
    AccessReview,
    EnterpriseUser,
    Invitation,
    InvitationStatus,
    UserStatus,
)
from jarvis_enterprise.user.repository import EnterpriseUserRepository
from jarvis_enterprise.user.service import UserAdministrationService


class InMemoryUserRepository:
    def __init__(self):
        self._users: dict = {}
        self._invitations: dict = {}
        self._reviews: dict = {}

    def save_user(self, user) -> None:
        self._users[user.id] = user

    def get_user(self, user_id) -> EnterpriseUser | None:
        return self._users.get(user_id)

    def list_users(self, org_id) -> list[EnterpriseUser]:
        return [u for u in self._users.values() if org_id in u.org_ids]

    def save_invitation(self, inv) -> None:
        self._invitations[inv.id] = inv

    def get_invitation(self, inv_id) -> Invitation | None:
        return self._invitations.get(inv_id)

    def list_invitations(self, org_id) -> list[Invitation]:
        return [i for i in self._invitations.values() if i.org_id == org_id]

    def save_access_review(self, review) -> None:
        self._reviews[review.id] = review

    def list_access_reviews(self, org_id) -> list[AccessReview]:
        return list(self._reviews.values())


class TestUserService:
    def setup_method(self):
        self.repo = UserAdministrationService(InMemoryUserRepository())

    def test_create_and_get(self):
        user = self.repo.create_user("u1", "user@test.com")
        assert user.id == "u1"
        fetched = self.repo.get_user("u1")
        assert fetched is not None

    def test_suspend_user(self):
        self.repo.create_user("u1", "user@test.com")
        suspended = self.repo.suspend_user("u1")
        assert suspended is not None
        assert suspended.status == UserStatus.suspended

    def test_assign_to_org(self):
        user = self.repo.create_user("u1", "user@test.com")
        org_id = uuid4()
        updated = self.repo.assign_user_to_org("u1", org_id)
        assert updated is not None
        assert org_id in updated.org_ids

    def test_invite_user(self):
        org_id = uuid4()
        inv = self.repo.invite_user("new@test.com", org_id, "admin")
        assert inv.email == "new@test.com"
        assert inv.status == InvitationStatus.pending

    def test_accept_invitation(self):
        org_id = uuid4()
        inv = self.repo.invite_user("new@test.com", org_id, "admin")
        accepted = self.repo.accept_invitation(inv.id)
        assert accepted is not None
        assert accepted.status == InvitationStatus.accepted

    def test_access_review(self):
        org_id = uuid4()
        review = self.repo.create_access_review(org_id, "reviewer1", "target1")
        assert review.reviewer_id == "reviewer1"
