"""Collaboration domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ReviewStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    changes_requested = "changes_requested"


class DiscussionKind(StrEnum):
    general = "general"
    design = "design"
    review = "review"
    decision = "decision"


@dataclass(frozen=True, slots=True)
class SharedProject:
    id: UUID = field(default_factory=uuid4)
    workspace_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    owner_id: str = ""
    members: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class SharedKnowledge:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    author_id: str = ""
    tags: tuple[str, ...] = ()
    visibility: str = "internal"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class Discussion:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    author_id: str = ""
    kind: DiscussionKind = DiscussionKind.general
    tags: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class DiscussionReply:
    id: UUID = field(default_factory=uuid4)
    discussion_id: UUID = field(default_factory=uuid4)
    author_id: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class ReviewWorkflow:
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    created_by: str = ""
    reviewers: tuple[str, ...] = ()
    status: ReviewStatus = ReviewStatus.pending
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class Approval:
    id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default_factory=uuid4)
    reviewer_id: str = ""
    approved: bool = False
    comment: str = ""
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
