from __future__ import annotations

from jarvis_agents.models import AgentMetadata, AgentStatus

_TRANSITIONS: dict[AgentStatus, frozenset[AgentStatus]] = {
    AgentStatus.CREATED: frozenset({AgentStatus.INITIALIZING, AgentStatus.RETIRED}),
    AgentStatus.INITIALIZING: frozenset(
        {
            AgentStatus.READY,
            AgentStatus.FAILED,
            AgentStatus.RETIRED,
        }
    ),
    AgentStatus.READY: frozenset(
        {
            AgentStatus.BUSY,
            AgentStatus.PAUSED,
            AgentStatus.SUSPENDED,
            AgentStatus.RETIRED,
            AgentStatus.WAITING,
        }
    ),
    AgentStatus.BUSY: frozenset(
        {
            AgentStatus.READY,
            AgentStatus.PAUSED,
            AgentStatus.WAITING,
            AgentStatus.FAILED,
            AgentStatus.SUSPENDED,
        }
    ),
    AgentStatus.PAUSED: frozenset(
        {
            AgentStatus.READY,
            AgentStatus.BUSY,
            AgentStatus.SUSPENDED,
            AgentStatus.RETIRED,
        }
    ),
    AgentStatus.WAITING: frozenset(
        {
            AgentStatus.READY,
            AgentStatus.BUSY,
            AgentStatus.PAUSED,
            AgentStatus.SUSPENDED,
        }
    ),
    AgentStatus.SUSPENDED: frozenset(
        {
            AgentStatus.READY,
            AgentStatus.RECOVERING,
            AgentStatus.RETIRED,
        }
    ),
    AgentStatus.RETIRED: frozenset(),
    AgentStatus.FAILED: frozenset(
        {
            AgentStatus.RECOVERING,
            AgentStatus.RETIRED,
            AgentStatus.READY,
        }
    ),
    AgentStatus.RECOVERING: frozenset(
        {
            AgentStatus.READY,
            AgentStatus.FAILED,
            AgentStatus.RETIRED,
        }
    ),
}


class InMemoryLifecycleManager:
    def __init__(self) -> None:
        self._registry: dict[str, AgentStatus] = {}

    def initialize(self, identifier: str) -> None:
        self._registry[identifier] = AgentStatus.CREATED

    def transition(self, identifier: str, to: AgentStatus) -> AgentMetadata:
        current = self._registry.get(identifier)
        if current is None:
            msg = f"Agent not found: {identifier}"
            raise KeyError(msg)
        if not self.can_transition(current, to):
            msg = f"Cannot transition from {current.value} to {to.value}"
            raise ValueError(msg)
        self._registry[identifier] = to
        return AgentMetadata(
            identifier=identifier,
            name="",
            description="",
            role="",
            capabilities=(),
            permissions=(),
            version="",
            status=to,
            owner="",
            workspace="",
        )

    def current(self, identifier: str) -> AgentStatus | None:
        return self._registry.get(identifier)

    def can_transition(self, from_status: AgentStatus, to: AgentStatus) -> bool:
        allowed = _TRANSITIONS.get(from_status, frozenset())
        return to in allowed
