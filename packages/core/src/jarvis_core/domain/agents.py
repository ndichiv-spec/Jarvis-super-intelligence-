from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from jarvis_core.domain.shared.events import DomainEvent
from jarvis_core.domain.shared.models import AggregateRoot
from jarvis_core.domain.shared.value_objects import DomainIdentifier


class AgentState(StrEnum):
    IDLE = "idle"
    BUSY = "busy"


@dataclass(frozen=True, slots=True)
class AgentCapability:
    name: str


@dataclass(frozen=True, slots=True)
class AgentRole:
    name: str


@dataclass(frozen=True, slots=True)
class AgentPermission:
    key: str


@dataclass(frozen=True, slots=True)
class AgentTask:
    title: str
    done: bool


@dataclass(slots=True)
class Agent(AggregateRoot):
    role: AgentRole
    permissions: tuple[AgentPermission, ...]
    capabilities: tuple[AgentCapability, ...]
    state: AgentState
    tasks: tuple[AgentTask, ...]


class AgentRepository(Protocol):
    def save(self, agent: Agent) -> None: ...


class AgentMemoryPort(Protocol):
    def link(self, agent_id: DomainIdentifier, memory_id: DomainIdentifier) -> None: ...


@dataclass(frozen=True, slots=True)
class AgentCreated(DomainEvent):
    role: str
