"""Collaboration platform service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.collaboration.models import (
    Approval,
    Discussion,
    DiscussionKind,
    DiscussionReply,
    ReviewStatus,
    ReviewWorkflow,
    SharedKnowledge,
    SharedProject,
)
from jarvis_enterprise.collaboration.repository import CollaborationRepository


class CollaborationService:
    def __init__(self, repository: CollaborationRepository) -> None:
        self._repository = repository

    def create_shared_project(
        self, workspace_id: UUID, name: str, owner_id: str, description: str = "",
    ) -> SharedProject:
        project = SharedProject(workspace_id=workspace_id, name=name, owner_id=owner_id, description=description)
        self._repository.save_shared_project(project)
        return project

    def list_shared_projects(self, workspace_id: UUID) -> list[SharedProject]:
        return self._repository.list_shared_projects(workspace_id)

    def create_shared_knowledge(self, title: str, content: str, author_id: str) -> SharedKnowledge:
        knowledge = SharedKnowledge(title=title, content=content, author_id=author_id)
        self._repository.save_shared_knowledge(knowledge)
        return knowledge

    def list_shared_knowledge(self) -> list[SharedKnowledge]:
        return self._repository.list_shared_knowledge()

    def create_discussion(self, title: str, content: str, author_id: str, kind: DiscussionKind = DiscussionKind.general) -> Discussion:
        discussion = Discussion(title=title, content=content, author_id=author_id, kind=kind)
        self._repository.save_discussion(discussion)
        return discussion

    def list_discussions(self) -> list[Discussion]:
        return self._repository.list_discussions()

    def add_reply(self, discussion_id: UUID, author_id: str, content: str) -> DiscussionReply | None:
        discussion = self._repository.get_shared_project(discussion_id) is not None
        reply = DiscussionReply(discussion_id=discussion_id, author_id=author_id, content=content)
        self._repository.save_reply(reply)
        return reply

    def create_review_workflow(self, title: str, created_by: str, reviewers: tuple[str, ...]) -> ReviewWorkflow:
        workflow = ReviewWorkflow(title=title, created_by=created_by, reviewers=reviewers)
        self._repository.save_workflow(workflow)
        return workflow

    def approve(self, workflow_id: UUID, reviewer_id: str, comment: str = "") -> Approval | None:
        workflow = self._repository.get_workflow(workflow_id)
        if workflow is None:
            return None
        approval = Approval(workflow_id=workflow_id, reviewer_id=reviewer_id, approved=True, comment=comment)
        self._repository.save_approval(approval)
        updated = ReviewWorkflow(
            id=workflow.id, title=workflow.title, description=workflow.description,
            created_by=workflow.created_by, reviewers=workflow.reviewers,
            status=ReviewStatus.approved, created_at=workflow.created_at,
        )
        self._repository.save_workflow(updated)
        return approval

    def reject(self, workflow_id: UUID, reviewer_id: str, comment: str = "") -> Approval | None:
        workflow = self._repository.get_workflow(workflow_id)
        if workflow is None:
            return None
        approval = Approval(workflow_id=workflow_id, reviewer_id=reviewer_id, approved=False, comment=comment)
        self._repository.save_approval(approval)
        updated = ReviewWorkflow(
            id=workflow.id, title=workflow.title, description=workflow.description,
            created_by=workflow.created_by, reviewers=workflow.reviewers,
            status=ReviewStatus.rejected, created_at=workflow.created_at,
        )
        self._repository.save_workflow(updated)
        return approval
