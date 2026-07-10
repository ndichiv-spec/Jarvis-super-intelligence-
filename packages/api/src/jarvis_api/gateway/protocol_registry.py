from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.types import ProtocolName, Protocols


@dataclass(frozen=True, slots=True)
class ProtocolDescriptor:
    name: ProtocolName
    transport: str
    supports_streaming: bool
    enabled: bool = True
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    documentation_reference: str = ""


class ProtocolRegistry:
    def __init__(self) -> None:
        self._descriptors: dict[ProtocolName, ProtocolDescriptor] = {}

    def register(self, descriptor: ProtocolDescriptor) -> None:
        if descriptor.name in self._descriptors:
            raise GatewayException.validation(
                f"Protocol '{descriptor.name}' is already registered",
                details={"protocol": descriptor.name},
            )
        self._descriptors[descriptor.name] = descriptor

    def replace(self, descriptor: ProtocolDescriptor) -> None:
        self._descriptors[descriptor.name] = descriptor

    def resolve(self, protocol_name: ProtocolName) -> ProtocolDescriptor | None:
        return self._descriptors.get(protocol_name)

    def ensure_supported(self, protocol_name: ProtocolName) -> ProtocolDescriptor:
        descriptor = self.resolve(protocol_name)
        if descriptor is None:
            raise GatewayException.validation(
                f"Unsupported protocol '{protocol_name}'",
                details={"protocol": protocol_name},
            )
        if not descriptor.enabled:
            raise GatewayException.policy_violation(
                f"Protocol '{protocol_name}' is not enabled",
                details={"protocol": protocol_name},
            )
        return descriptor

    def list_protocols(self) -> tuple[ProtocolDescriptor, ...]:
        return tuple(sorted(self._descriptors.values(), key=lambda descriptor: descriptor.name))

    @classmethod
    def with_defaults(cls) -> ProtocolRegistry:
        registry = cls()
        registry.register(
            ProtocolDescriptor(
                name=Protocols.REST,
                transport="http",
                supports_streaming=False,
                capabilities=("request_response", "cache_headers", "metadata"),
                documentation_reference="phase14_protocol_model.md#rest",
            )
        )
        registry.register(
            ProtocolDescriptor(
                name=Protocols.WEBSOCKET,
                transport="ws",
                supports_streaming=True,
                capabilities=("bidirectional", "events", "notifications"),
                documentation_reference="phase14_protocol_model.md#websocket",
            )
        )
        registry.register(
            ProtocolDescriptor(
                name=Protocols.SSE,
                transport="http",
                supports_streaming=True,
                capabilities=("unidirectional", "token_streaming", "events"),
                documentation_reference="phase14_protocol_model.md#sse",
            )
        )
        registry.register(
            ProtocolDescriptor(
                name=Protocols.MCP,
                transport="http",
                supports_streaming=True,
                capabilities=("tool_context", "extensions", "agent_events"),
                documentation_reference="phase14_protocol_model.md#mcp",
            )
        )
        registry.register(
            ProtocolDescriptor(
                name=Protocols.GRPC,
                transport="http2",
                supports_streaming=True,
                enabled=False,
                capabilities=("protobuf", "future_protocol"),
                documentation_reference="phase14_protocol_model.md#future-protocols",
            )
        )
        registry.register(
            ProtocolDescriptor(
                name=Protocols.GRAPHQL,
                transport="http",
                supports_streaming=True,
                enabled=False,
                capabilities=("schema_queries", "subscriptions", "future_protocol"),
                documentation_reference="phase14_protocol_model.md#future-protocols",
            )
        )
        return registry
