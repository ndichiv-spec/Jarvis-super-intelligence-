from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot


class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    DONE = "done"


@dataclass(frozen=True, slots=True)
class Workspace:
    name: str


@dataclass(frozen=True, slots=True)
class Artifact:
    name: str


@dataclass(frozen=True, slots=True)
class Task:
    title: str
    done: bool


@dataclass(frozen=True, slots=True)
class Milestone:
    title: str


@dataclass(slots=True)
class Project(AggregateRoot):
    workspace: Workspace
    artifacts: tuple[Artifact, ...]
    tasks: tuple[Task, ...]
    milestones: tuple[Milestone, ...]
    status: ProjectStatus


class ProjectRepository(Protocol):
    def save(self, project: Project) -> None: ...


@dataclass(frozen=True, slots=True)
class ProjectCreated(DomainEvent):
    workspace_name: str


@dataclass(frozen=True, slots=True)
class TaskCompleted(DomainEvent):
    task_title: str
