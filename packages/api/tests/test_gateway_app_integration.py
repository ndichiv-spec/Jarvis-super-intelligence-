import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass

from jarvis_api.gateway.app import create_gateway_app
from jarvis_api.gateway.kernel import (
    AllowAllAuthorizationService,
    GatewayKernel,
    NoOpRequestValidator,
)
from jarvis_api.gateway.routing import RouteDefinition, RoutingEngine
from jarvis_api.gateway.types import GatewayRequest, GatewayResponse, Protocols


@dataclass(frozen=True, slots=True)
class AsgiResponse:
    status: int
    headers: Mapping[str, str]
    body: str


async def _invoke_http(
    app: object,
    *,
    method: str,
    path: str,
    body: bytes = b"",
    headers: Mapping[str, str] | None = None,
) -> AsgiResponse:
    sent_messages: list[dict[str, object]] = []
    payload_sent = False

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [
            (key.lower().encode(), value.encode())
            for key, value in (headers or {}).items()
        ],
        "client": ("127.0.0.1", 9000),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        nonlocal payload_sent
        if not payload_sent:
            payload_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, object]) -> None:
        sent_messages.append(message)

    await app(scope, receive, send)

    start = next(message for message in sent_messages if message["type"] == "http.response.start")
    chunks = [
        message.get("body", b"")
        for message in sent_messages
        if message["type"] == "http.response.body"
    ]
    decoded_headers = {
        key.decode(): value.decode()
        for key, value in start.get("headers", [])
    }
    return AsgiResponse(
        status=int(start["status"]),
        headers=decoded_headers,
        body=b"".join(chunks).decode(),
    )


class IntegrationExecutor:
    async def execute(self, request: GatewayRequest, route: object) -> GatewayResponse:
        del route
        if request.protocol == Protocols.SSE:
            async def _stream() -> AsyncIterator[object]:
                yield {"event": "started"}
                yield {"event": "finished"}

            return GatewayResponse.ok(body=None, stream=_stream(), protocol=Protocols.SSE)
        return GatewayResponse.ok({"echo": request.payload, "path": request.path})


def _build_kernel() -> GatewayKernel:
    routing = RoutingEngine()
    routing.register_route(RouteDefinition(identifier="brain-route", subsystem="brain", path_prefix="/brain"))
    return GatewayKernel(
        routing_engine=routing,
        request_validator=NoOpRequestValidator(),
        authorization_service=AllowAllAuthorizationService(),
        route_executor=IntegrationExecutor(),
    )


def test_gateway_app_handles_http_requests_and_health_surfaces() -> None:
    app = create_gateway_app(_build_kernel())

    response = asyncio.run(
        _invoke_http(
            app,
            method="POST",
            path="/gateway/brain/query",
            body=json.dumps({"prompt": "hello"}).encode(),
            headers={"content-type": "application/json"},
        )
    )
    health = asyncio.run(_invoke_http(app, method="GET", path="/health"))
    stats = asyncio.run(_invoke_http(app, method="GET", path="/stats"))

    assert response.status == 200
    payload = json.loads(response.body)
    assert payload["ok"] is True
    assert payload["data"]["path"] == "/brain/query"

    assert health.status == 200
    assert json.loads(health.body)["status"] == "ok"

    assert stats.status == 200
    assert "observability" in json.loads(stats.body)


def test_gateway_app_stream_endpoint_returns_sse_payloads() -> None:
    app = create_gateway_app(_build_kernel())

    response = asyncio.run(_invoke_http(app, method="GET", path="/gateway/stream/brain/events"))

    assert response.status == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "sequence" in response.body
