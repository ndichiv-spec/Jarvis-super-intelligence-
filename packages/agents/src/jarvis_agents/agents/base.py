from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_agents.models import (
    AgentCapability,
    AgentCommunicationRequest,
    AgentCommunicationResponse,
    AgentMetadata,
    AgentPermission,
    AgentStatus,
    AgentTask,
    AgentTaskResult,
)


def _new_id() -> str:
    return uuid4().hex[:8]


class BaseAgent:
    agent_id: str
    name: str
    description: str
    capabilities: tuple[AgentCapability, ...]
    permissions: tuple[AgentPermission, ...]
    status: AgentStatus
    metadata: AgentMetadata

    def __init__(
        self,
        *,
        agent_id: str | None = None,
        name: str,
        description: str,
        capabilities: tuple[AgentCapability, ...],
        permissions: tuple[AgentPermission, ...],
        metadata: AgentMetadata | None = None,
    ) -> None:
        self.agent_id = agent_id or f"agent-{_new_id()}"
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.permissions = permissions
        self._messages: deque[AgentCommunicationRequest] = deque()
        self._responses: deque[AgentCommunicationResponse] = deque()
        self.status = AgentStatus.CREATED
        self.metadata = metadata or AgentMetadata(
            identifier=self.agent_id,
            name=self.name,
            description=self.description,
            role=self.__class__.__name__.replace("Agent", "").lower(),
            capabilities=self.capabilities,
            permissions=self.permissions,
            version="1.0.0",
            status=self.status,
            owner="system",
            workspace="default",
        )

    def initialize(self) -> None:
        self.status = AgentStatus.INITIALIZING

    def start(self) -> None:
        self.status = AgentStatus.READY

    def stop(self) -> None:
        self.status = AgentStatus.RETIRED

    def pause(self) -> None:
        self.status = AgentStatus.PAUSED

    def resume(self) -> None:
        self.status = AgentStatus.READY

    def handle_task(self, task: AgentTask) -> AgentTaskResult:
        return self._process_task(task)

    def _process_task(self, task: AgentTask) -> AgentTaskResult:
        raise NotImplementedError

    def send_message(
        self,
        target_id: str,
        message_type: str,
        payload: str,
    ) -> str:
        corr_id = f"corr-{_new_id()}"
        self._messages.append(AgentCommunicationRequest(
            source_agent_id=self.agent_id,
            target_agent_id=target_id,
            message_type=message_type,
            payload=payload,
            correlation_id=corr_id,
            created_at=datetime.now(UTC),
        ))
        return corr_id

    def receive_messages(self) -> tuple[AgentCommunicationRequest, ...]:
        msgs = tuple(self._messages)
        self._messages.clear()
        return msgs

    def send_response(
        self,
        correlation_id: str,
        target_id: str,
        payload: str,
        success: bool = True,
    ) -> None:
        self._responses.append(AgentCommunicationResponse(
            correlation_id=correlation_id,
            source_agent_id=self.agent_id,
            target_agent_id=target_id,
            payload=payload,
            success=success,
            created_at=datetime.now(UTC),
        ))

    def receive_responses(self) -> tuple[AgentCommunicationResponse, ...]:
        resps = tuple(self._responses)
        self._responses.clear()
        return resps
