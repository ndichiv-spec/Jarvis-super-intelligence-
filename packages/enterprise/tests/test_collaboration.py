"""Tests for Collaboration Platform."""

from uuid import uuid4

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
from jarvis_enterprise.collaboration.service import CollaborationService


class InMemoryCollabRepo:
    def __init__(self):
        self._projects: dict = {}
        self._knowledge: dict = {}
        self._discussions: dict = {}
        self._replies: dict = {}
        self._workflows: dict = {}
        self._approvals: dict = {}

    def save_shared_project(self, project) -> None:
        self._projects[project.id] = project

    def get_shared_project(self, project_id) -> SharedProject | None:
        return self._projects.get(project_id)

    def list_shared_projects(self, ws_id) -> list[SharedProject]:
        return [p for p in self._projects.values() if p.workspace_id == ws_id]

    def save_shared_knowledge(self, knowledge) -> None:
        self._knowledge[knowledge.id] = knowledge

    def list_shared_knowledge(self) -> list[SharedKnowledge]:
        return list(self._knowledge.values())

    def save_discussion(self, discussion) -> None:
        self._discussions[discussion.id] = discussion

    def list_discussions(self) -> list[Discussion]:
        return list(self._discussions.values())

    def save_reply(self, reply) -> None:
        self._replies[reply.id] = reply

    def list_replies(self, discussion_id) -> list[DiscussionReply]:
        return [r for r in self._replies.values() if r.discussion_id == discussion_id]

    def save_workflow(self, workflow) -> None:
        self._workflows[workflow.id] = workflow

    def get_workflow(self, workflow_id) -> ReviewWorkflow | None:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> list[ReviewWorkflow]:
        return list(self._workflows.values())

    def save_approval(self, approval) -> None:
        self._approvals[approval.id] = approval

    def list_approvals(self, workflow_id) -> list[Approval]:
        return [a for a in self._approvals.values() if a.workflow_id == workflow_id]


class TestCollaborationService:
    def setup_method(self):
        self.repo = CollaborationService(InMemoryCollabRepo())

    def test_create_shared_project(self):
        project = self.repo.create_shared_project(uuid4(), "My Project", "owner1")
        assert project.name == "My Project"

    def test_list_shared_projects(self):
        ws_id = uuid4()
        self.repo.create_shared_project(ws_id, "P1", "owner1")
        self.repo.create_shared_project(ws_id, "P2", "owner1")
        assert len(self.repo.list_shared_projects(ws_id)) == 2

    def test_create_shared_knowledge(self):
        knowledge = self.repo.create_shared_knowledge("How-to Guide", "Step 1...", "author1")
        assert knowledge.title == "How-to Guide"

    def test_create_discussion(self):
        discussion = self.repo.create_discussion("Question", "Anyone know?", "user1", DiscussionKind.general)
        assert discussion.kind == DiscussionKind.general

    def test_create_review_workflow(self):
        workflow = self.repo.create_review_workflow("Review PR", "user1", ("reviewer1", "reviewer2"))
        assert len(workflow.reviewers) == 2

    def test_approve_workflow(self):
        workflow = self.repo.create_review_workflow("Review", "user1", ("reviewer1",))
        approval = self.repo.approve(workflow.id, "reviewer1")
        assert approval is not None
        assert approval.approved is True

    def test_reject_workflow(self):
        workflow = self.repo.create_review_workflow("Review", "user1", ("reviewer1",))
        rejection = self.repo.reject(workflow.id, "reviewer1", "Needs work")
        assert rejection is not None
        assert rejection.approved is False
