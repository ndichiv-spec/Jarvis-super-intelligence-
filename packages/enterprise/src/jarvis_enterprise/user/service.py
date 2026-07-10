"""User administration service."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import UUID

from jarvis_enterprise.user.models import (
    AccessReview,
    EnterpriseUser,
    Invitation,
    InvitationStatus,
    UserStatus,
)
from jarvis_enterprise.user.repository import EnterpriseUserRepository


class UserAdministrationService:
    def __init__(self, repository: EnterpriseUserRepository) -> None:
        self._repository = repository

    def create_user(self, user_id: str, email: str, display_name: str = "") -> EnterpriseUser:
        user = EnterpriseUser(id=user_id, email=email, display_name=display_name or email)
        self._repository.save_user(user)
        return user

    def get_user(self, user_id: str) -> EnterpriseUser | None:
        return self._repository.get_user(user_id)

    def suspend_user(self, user_id: str) -> EnterpriseUser | None:
        user = self._repository.get_user(user_id)
        if user is None:
            return None
        updated = EnterpriseUser(
            id=user.id, email=user.email, display_name=user.display_name,
            status=UserStatus.suspended, org_ids=user.org_ids, roles=user.roles,
            tags=user.tags, metadata=user.metadata, created_at=user.created_at,
        )
        self._repository.save_user(updated)
        return updated

    def list_users(self, org_id: UUID) -> list[EnterpriseUser]:
        return self._repository.list_users(org_id)

    def assign_user_to_org(self, user_id: str, org_id: UUID) -> EnterpriseUser | None:
        user = self._repository.get_user(user_id)
        if user is None:
            return None
        updated = EnterpriseUser(
            id=user.id, email=user.email, display_name=user.display_name,
            status=user.status, org_ids=(*user.org_ids, org_id), roles=user.roles,
            tags=user.tags, metadata=user.metadata, created_at=user.created_at,
        )
        self._repository.save_user(updated)
        return updated

    def invite_user(self, email: str, org_id: UUID, invited_by: str, role: str = "member") -> Invitation:
        invitation = Invitation(
            email=email, org_id=org_id, invited_by=invited_by, role=role,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        self._repository.save_invitation(invitation)
        return invitation

    def accept_invitation(self, invitation_id: UUID) -> Invitation | None:
        inv = self._repository.get_invitation(invitation_id)
        if inv is None or inv.status != InvitationStatus.pending:
            return None
        updated = Invitation(
            id=inv.id, email=inv.email, org_id=inv.org_id, role=inv.role,
            invited_by=inv.invited_by, status=InvitationStatus.accepted,
            expires_at=inv.expires_at, created_at=inv.created_at,
        )
        self._repository.save_invitation(updated)
        return updated

    def create_access_review(self, org_id: UUID, reviewer_id: str, target_user_id: str) -> AccessReview:
        review = AccessReview(org_id=org_id, reviewer_id=reviewer_id, target_user_id=target_user_id)
        self._repository.save_access_review(review)
        return review

    def complete_access_review(self, review_id: UUID, approved: bool, notes: str = "") -> AccessReview | None:
        reviews = self._repository.list_access_reviews(UUID(int=0))
        for r in reviews:
            if r.id == review_id:
                updated = AccessReview(
                    id=r.id, org_id=r.org_id, reviewer_id=r.reviewer_id,
                    target_user_id=r.target_user_id,
                    reviewed_at=datetime.now(timezone.utc),
                    approved=approved, notes=notes,
                )
                self._repository.save_access_review(updated)
                return updated
        return None
