import asyncio
from collections.abc import AsyncIterator
from datetime import timedelta

from jarvis_api.gateway.errors import GatewayException
from jarvis_api.gateway.kernel import (
    AllowAllAuthorizationService,
    GatewayKernel,
    NoOpRequestValidator,
)
from jarvis_api.gateway.rate_limit import RateLimiter, RateLimitPolicy, RateLimitScope
from jarvis_api.gateway.routing import RouteDefinition, RoutingEngine
from jarvis_api.gateway.types import GatewayRequest, GatewayResponse, Protocols


class FailingValidator(NoOpRequestValidator):
    async def validate(self, request: GatewayRequest) -> None:
        del request
        raise GatewayException.validation("Invalid payload")


class EchoExecutor:
    async def execute(self, request: GatewayRequest, route: object) -> GatewayResponse:
        del route
        return GatewayResponse.ok({"path": request.path, "payload": request.payload})


class StreamExecutor:
    async def execute(self, request: GatewayRequest, route: object) -> GatewayResponse:
        del request
        del route

        async def _stream() -> AsyncIterator[object]:
            yield {"step": 1}
            yield {"step": 2}

        return GatewayResponse.ok(body=None, stream=_stream(), protocol=Protocols.SSE)


def _build_routing_engine() -> RoutingEngine:
    routing = RoutingEngine()
    routing.register_route(RouteDefinition(identifier="brain-route", subsystem="brain", path_prefix="/brain"))
    return routing


def test_gateway_kernel_successfully_processes_request_and_normalizes_response() -> None:
    kernel = GatewayKernel(
        routing_engine=_build_routing_engine(),
        request_validator=NoOpRequestValidator(),
        authorization_service=AllowAllAuthorizationService(),
        route_executor=EchoExecutor(),
    )
    request = GatewayRequest.new(
        protocol=Protocols.REST,
        path="/brain/query",
        version="1.0.0",
        subject_id="user-1",
        workspace_id="workspace-1",
        payload={"prompt": "hello"},
    )

    response = asyncio.run(kernel.handle(request))

    assert response.status_code == 200
    assert isinstance(response.body, dict)
    assert response.body["ok"] is True
    assert response.body["data"] == {"path": "/brain/query", "payload": {"prompt": "hello"}}
    assert response.body["metadata"]["route"] == "brain-route"
    assert response.headers["x-jarvis-request-id"] == request.request_id


def test_gateway_kernel_transforms_validation_error_to_standard_contract() -> None:
    kernel = GatewayKernel(
        routing_engine=_build_routing_engine(),
        request_validator=FailingValidator(),
        authorization_service=AllowAllAuthorizationService(),
        route_executor=EchoExecutor(),
    )

    request = GatewayRequest.new(protocol=Protocols.REST, path="/brain/query", version="1.0.0")
    response = asyncio.run(kernel.handle(request))

    assert response.status_code == 400
    assert isinstance(response.body, dict)
    assert response.body["ok"] is False
    assert response.body["error"]["code"] == "validation_error"


def test_gateway_kernel_applies_rate_limits_and_returns_429() -> None:
    rate_limiter = RateLimiter(
        policies=(
            RateLimitPolicy(scope=RateLimitScope.USER, limit=1, window=timedelta(seconds=60)),
        )
    )
    kernel = GatewayKernel(
        routing_engine=_build_routing_engine(),
        request_validator=NoOpRequestValidator(),
        authorization_service=AllowAllAuthorizationService(),
        route_executor=EchoExecutor(),
        rate_limiter=rate_limiter,
    )
    request = GatewayRequest.new(
        protocol=Protocols.REST,
        path="/brain/query",
        version="1.0.0",
        subject_id="user-1",
    )

    first = asyncio.run(kernel.handle(request))
    second = asyncio.run(kernel.handle(request))

    assert first.status_code == 200
    assert second.status_code == 429


def test_gateway_kernel_coordinates_streaming_responses() -> None:
    kernel = GatewayKernel(
        routing_engine=_build_routing_engine(),
        request_validator=NoOpRequestValidator(),
        authorization_service=AllowAllAuthorizationService(),
        route_executor=StreamExecutor(),
    )
    request = GatewayRequest.new(protocol=Protocols.SSE, path="/brain/stream", version="1.0.0")

    response = asyncio.run(kernel.handle(request))

    assert response.status_code == 200
    assert response.stream is not None
