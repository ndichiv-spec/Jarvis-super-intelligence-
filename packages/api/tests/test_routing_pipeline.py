import asyncio
from dataclasses import replace

from jarvis_api.gateway.pipeline import RequestPipeline, ResponsePipeline
from jarvis_api.gateway.routing import RouteDefinition, RoutingEngine
from jarvis_api.gateway.types import GatewayRequest, GatewayResponse, Protocols


class TraceRequestMiddleware:
    async def handle(self, request: GatewayRequest) -> GatewayRequest:
        trace = list(request.metadata.get("trace", ()))
        trace.append("request")
        return replace(request, metadata={**request.metadata, "trace": tuple(trace)})


class TraceResponseMiddleware:
    async def handle(self, response: GatewayResponse) -> GatewayResponse:
        body = response.body if isinstance(response.body, dict) else {}
        trace = list(body.get("trace", ()))
        trace.append("response")
        return replace(response, body={**body, "trace": tuple(trace)})


def test_routing_engine_resolves_longest_matching_prefix() -> None:
    routing = RoutingEngine()
    routing.register_route(RouteDefinition(identifier="brain", subsystem="brain", path_prefix="/brain"))
    routing.register_route(
        RouteDefinition(
            identifier="brain-memory",
            subsystem="memory",
            path_prefix="/brain/memory",
            supported_protocols=(Protocols.REST,),
        )
    )

    resolved = routing.resolve("/brain/memory/query", protocol=Protocols.REST)

    assert resolved.identifier == "brain-memory"
    assert resolved.subsystem == "memory"


def test_request_and_response_pipeline_execute_in_order() -> None:
    request_pipeline = RequestPipeline([TraceRequestMiddleware()])
    response_pipeline = ResponsePipeline([TraceResponseMiddleware()])

    request = GatewayRequest.new(protocol=Protocols.REST, path="/brain", version="1.0.0")
    piped_request = asyncio.run(request_pipeline.execute(request))

    assert piped_request.metadata["trace"] == ("request",)

    response = GatewayResponse.ok({"trace": ()})
    piped_response = asyncio.run(response_pipeline.execute(response))

    assert piped_response.body == {"trace": ("response",)}
