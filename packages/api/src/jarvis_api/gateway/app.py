from __future__ import annotations

import json
from collections.abc import AsyncIterator, Mapping

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response, StreamingResponse

from jarvis_api.gateway.kernel import GatewayKernel
from jarvis_api.gateway.routes.agents import router as agents_router
from jarvis_api.gateway.routes.intelligence import router as intelligence_router
from jarvis_api.gateway.routes.planning import router as planning_router
from jarvis_api.gateway.routes.studio import router as studio_router
from jarvis_api.gateway.routes.communication import router as communication_router
from jarvis_api.gateway.types import GatewayRequest, GatewayResponse, Protocols, StreamEnvelope

REST_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD")


def create_gateway_app(kernel: GatewayKernel | None = None) -> FastAPI:
    gateway_kernel = kernel or GatewayKernel()
    app = FastAPI(title="JARVIS Professional Service Gateway", version="14.0.0")

    app.include_router(agents_router)
    app.include_router(intelligence_router)
    app.include_router(planning_router)
    app.include_router(studio_router)
    app.include_router(communication_router)

    @app.get("/health")
    async def health() -> Mapping[str, object]:
        return gateway_kernel.health()

    @app.get("/stats")
    async def stats() -> Mapping[str, object]:
        return gateway_kernel.stats()

    @app.api_route("/gateway/stream/{full_path:path}", methods=["GET", "POST"])
    async def gateway_stream(full_path: str, request: Request) -> Response:
        gateway_request = await _build_gateway_request(
            request=request,
            full_path=full_path,
            protocol=Protocols.SSE,
        )
        gateway_response = await gateway_kernel.handle(gateway_request)
        return _to_http_response(gateway_response)

    @app.api_route("/gateway/{full_path:path}", methods=list(REST_METHODS))
    async def gateway_http(full_path: str, request: Request) -> Response:
        gateway_request = await _build_gateway_request(
            request=request,
            full_path=full_path,
            protocol=Protocols.REST,
        )
        gateway_response = await gateway_kernel.handle(gateway_request)
        return _to_http_response(gateway_response)

    @app.websocket("/gateway/ws/{full_path:path}")
    async def gateway_websocket(full_path: str, websocket: WebSocket) -> None:
        await websocket.accept()

        try:
            incoming_payload = await _read_websocket_payload(websocket)
            request_headers = {
                key.lower(): value
                for key, value in websocket.headers.items()
            }
            gateway_request = GatewayRequest.new(
                protocol=Protocols.WEBSOCKET,
                path=f"/{full_path}",
                version=request_headers.get("x-api-version", "1.0.0"),
                method="WEBSOCKET",
                subject_id=request_headers.get("x-subject-id"),
                workspace_id=request_headers.get("x-workspace-id"),
                organization_id=request_headers.get("x-organization-id"),
                extension_id=request_headers.get("x-extension-id"),
                session_id=request_headers.get("x-session-id"),
                headers=request_headers,
                query={key: value for key, value in websocket.query_params.items()},
                payload=incoming_payload,
                metadata={"transport": "websocket"},
            )
            gateway_response = await gateway_kernel.handle(gateway_request)
            if gateway_response.stream is not None:
                async for chunk in gateway_response.stream:
                    if isinstance(chunk, StreamEnvelope):
                        await websocket.send_json(chunk.to_event())
                    else:
                        await websocket.send_json({"payload": chunk})
            else:
                await websocket.send_json(gateway_response.body)
        except WebSocketDisconnect:
            return
        finally:
            await websocket.close()

    return app


async def _build_gateway_request(
    *,
    request: Request,
    full_path: str,
    protocol: str,
) -> GatewayRequest:
    payload = await _extract_payload(request)
    headers = {key.lower(): value for key, value in request.headers.items()}
    query = {key: value for key, value in request.query_params.items()}

    return GatewayRequest.new(
        protocol=protocol,
        path=f"/{full_path}",
        version=headers.get("x-api-version", "1.0.0"),
        method=request.method,
        subject_id=headers.get("x-subject-id"),
        workspace_id=headers.get("x-workspace-id"),
        organization_id=headers.get("x-organization-id"),
        extension_id=headers.get("x-extension-id"),
        session_id=headers.get("x-session-id"),
        headers=headers,
        query=query,
        payload=payload,
        metadata={"transport": protocol},
    )


async def _extract_payload(request: Request) -> object | None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type.lower():
        try:
            return await request.json()
        except json.JSONDecodeError as error:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from error

    raw_payload = await request.body()
    if not raw_payload:
        return None
    try:
        return raw_payload.decode("utf-8")
    except UnicodeDecodeError:
        return raw_payload.hex()


def _to_http_response(response: GatewayResponse) -> Response:
    headers = dict(response.headers)
    if response.stream is not None:
        return StreamingResponse(
            _serialize_stream(response.stream, protocol=response.protocol),
            status_code=response.status_code,
            headers=headers,
            media_type="text/event-stream" if response.protocol == Protocols.SSE else "application/json",
        )

    if response.body is None:
        return Response(status_code=response.status_code, headers=headers)

    return JSONResponse(status_code=response.status_code, content=response.body, headers=headers)


async def _serialize_stream(
    stream: AsyncIterator[object],
    *,
    protocol: str,
) -> AsyncIterator[str]:
    async for chunk in stream:
        if isinstance(chunk, StreamEnvelope):
            serialized = json.dumps(chunk.to_event())
        else:
            serialized = json.dumps({"payload": chunk})
        if protocol == Protocols.SSE:
            yield f"data: {serialized}\n\n"
        else:
            yield f"{serialized}\n"


async def _read_websocket_payload(websocket: WebSocket) -> object:
    message = await websocket.receive()
    if "json" in message and message["json"] is not None:
        return message["json"]
    if "text" in message and message["text"] is not None:
        return message["text"]
    if "bytes" in message and message["bytes"] is not None:
        return message["bytes"].hex()
    return {}
