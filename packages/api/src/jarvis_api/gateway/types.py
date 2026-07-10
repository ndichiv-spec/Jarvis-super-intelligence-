from __future__ import annotations

from collections.abc import AsyncIterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from jarvis_api.gateway.errors import GatewayErrorContract

ProtocolName = str
SubsystemName = str


class Protocols:
    REST: ProtocolName = "rest"
    WEBSOCKET: ProtocolName = "websocket"
    SSE: ProtocolName = "sse"
    MCP: ProtocolName = "mcp"
    GRPC: ProtocolName = "grpc"
    GRAPHQL: ProtocolName = "graphql"


class Subsystems:
    BRAIN: SubsystemName = "brain"
    MEMORY: SubsystemName = "memory"
    KNOWLEDGE: SubsystemName = "knowledge"
    AGENTS: SubsystemName = "agents"
    TOOLS: SubsystemName = "tools"
    AUTOMATION: SubsystemName = "automation"
    EXTENSIONS: SubsystemName = "extensions"
    ADMINISTRATION: SubsystemName = "administration"


class StreamKinds:
    TOKEN: str = "token"
    WORKFLOW_PROGRESS: str = "workflow_progress"
    AGENT_EVENT: str = "agent_event"
    AUTOMATION_PROGRESS: str = "automation_progress"
    NOTIFICATION: str = "notification"
    TELEMETRY: str = "telemetry"


@dataclass(frozen=True, slots=True)
class GatewayRequest:
    request_id: str
    protocol: ProtocolName
    path: str
    version: str
    method: str = "GET"
    subject_id: str | None = None
    workspace_id: str | None = None
    organization_id: str | None = None
    extension_id: str | None = None
    session_id: str | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    query: Mapping[str, str] = field(default_factory=dict)
    payload: object | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    stream: AsyncIterable[object] | None = None

    @classmethod
    def new(
        cls,
        *,
        protocol: ProtocolName,
        path: str,
        version: str,
        method: str = "GET",
        subject_id: str | None = None,
        workspace_id: str | None = None,
        organization_id: str | None = None,
        extension_id: str | None = None,
        session_id: str | None = None,
        headers: Mapping[str, str] | None = None,
        query: Mapping[str, str] | None = None,
        payload: object | None = None,
        metadata: Mapping[str, Any] | None = None,
        stream: AsyncIterable[object] | None = None,
    ) -> GatewayRequest:
        return cls(
            request_id=str(uuid4()),
            protocol=protocol,
            path=path,
            version=version,
            method=method,
            subject_id=subject_id,
            workspace_id=workspace_id,
            organization_id=organization_id,
            extension_id=extension_id,
            session_id=session_id,
            headers=headers or {},
            query=query or {},
            payload=payload,
            metadata=metadata or {},
            stream=stream,
        )


@dataclass(frozen=True, slots=True)
class GatewayResponse:
    status_code: int
    body: object | None = None
    headers: Mapping[str, str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    stream: AsyncIterable[object] | None = None
    protocol: ProtocolName = Protocols.REST
    error: GatewayErrorContract | None = None

    @classmethod
    def ok(
        cls,
        body: object | None,
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        metadata: Mapping[str, Any] | None = None,
        stream: AsyncIterable[object] | None = None,
        protocol: ProtocolName = Protocols.REST,
    ) -> GatewayResponse:
        return cls(
            status_code=status_code,
            body=body,
            headers=headers or {},
            metadata=metadata or {},
            stream=stream,
            protocol=protocol,
        )

    @classmethod
    def failure(
        cls,
        *,
        error: GatewayErrorContract,
        headers: Mapping[str, str] | None = None,
        metadata: Mapping[str, Any] | None = None,
        protocol: ProtocolName = Protocols.REST,
    ) -> GatewayResponse:
        return cls(
            status_code=error.status_code,
            body=None,
            headers=headers or {},
            metadata=metadata or {},
            protocol=protocol,
            error=error,
        )


@dataclass(frozen=True, slots=True)
class ServiceMetadata:
    identifier: str
    version: str
    protocol: ProtocolName
    capabilities: tuple[str, ...]
    workspace_visibility: tuple[str, ...]
    authorization_requirements: tuple[str, ...]
    documentation_references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StreamEnvelope:
    sequence: int
    channel_id: str
    kind: str
    timestamp: datetime
    payload: object
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_event(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "channel_id": self.channel_id,
            "kind": self.kind,
            "timestamp": self.timestamp.astimezone(UTC).isoformat(),
            "payload": self.payload,
            "metadata": dict(self.metadata),
        }
