from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.protocol_registry import ProtocolDescriptor, ProtocolRegistry
from jarvis_api.gateway.types import Protocols


def test_protocol_registry_defaults_include_current_and_future_protocols() -> None:
    registry = ProtocolRegistry.with_defaults()

    names = {descriptor.name for descriptor in registry.list_protocols()}
    assert {Protocols.REST, Protocols.WEBSOCKET, Protocols.SSE, Protocols.MCP}.issubset(names)
    assert {Protocols.GRPC, Protocols.GRAPHQL}.issubset(names)

    grpc_descriptor = registry.resolve(Protocols.GRPC)
    assert grpc_descriptor is not None
    assert grpc_descriptor.enabled is False


def test_protocol_registry_supports_custom_protocol_registration() -> None:
    registry = ProtocolRegistry.with_defaults()
    descriptor = ProtocolDescriptor(
        name="custom-binary",
        transport="tcp",
        supports_streaming=True,
        capabilities=("experimental",),
    )

    registry.register(descriptor)

    resolved = registry.ensure_supported("custom-binary")
    assert resolved == descriptor


def test_protocol_registry_rejects_duplicate_registration() -> None:
    registry = ProtocolRegistry()
    descriptor = ProtocolDescriptor(name=Protocols.REST, transport="http", supports_streaming=False)
    registry.register(descriptor)

    try:
        registry.register(descriptor)
    except GatewayException as error:
        assert error.contract.code.value == "validation_error"
    else:
        msg = "Expected duplicate protocol registration to fail"
        raise AssertionError(msg)
