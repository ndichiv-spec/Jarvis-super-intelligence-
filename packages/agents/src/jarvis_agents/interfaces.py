from __future__ import annotations

from typing import Protocol

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


class Agent(Protocol):
    agent_id: str
    name: str
    description: str
    capabilities: tuple[AgentCapability, ...]
    permissions: tuple[AgentPermission, ...]
    status: AgentStatus
    metadata: AgentMetadata

    def initialize(self) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def pause(self) -> None: ...

    def resume(self) -> None: ...

    def handle_task(self, task: AgentTask) -> AgentTaskResult: ...

    def send_message(
        self,
        target_id: str,
        message_type: str,
        payload: str,
    ) -> str: ...

    def receive_messages(self) -> tuple[AgentCommunicationRequest, ...]: ...

    def send_response(
        self,
        correlation_id: str,
        target_id: str,
        payload: str,
        success: bool = True,
    ) -> None: ...

    def receive_responses(self) -> tuple[AgentCommunicationResponse, ...]: ...
