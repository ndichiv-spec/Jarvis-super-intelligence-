from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterable, Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx
import anyio

from jarvis_api.gateway import (
    GatewayKernel,
    GatewayRequest,
    GatewayResponse,
    Protocols,
    RouteDefinition,
    RoutingEngine,
    ServiceMetadata,
)
from jarvis_api.gateway.protocols import RouteExecutorProtocol

logger = logging.getLogger(__name__)


class DesktopRouteExecutor(RouteExecutorProtocol):
    async def execute(self, request: GatewayRequest, route: object) -> GatewayResponse:
        path = request.path.strip("/")
        parts = path.split("/")

        if len(parts) >= 2 and parts[0] == "desktop":
            subsystem = parts[1]
            if subsystem == "runtime":
                return await self._handle_runtime(request)
            if subsystem == "permissions":
                return await self._handle_permissions(request)
            if subsystem == "sync":
                return await self._handle_sync(request)
            if subsystem == "files":
                return await self._handle_files(request)
            if subsystem == "notifications":
                return await self._handle_notifications(request)
            if subsystem == "diagnostics":
                return await self._handle_diagnostics(request)
            if subsystem == "offline":
                return await self._handle_offline(request)
            if subsystem == "updates":
                return await self._handle_updates(request)
            if subsystem == "integrations":
                return await self._handle_integrations(request)

        return GatewayResponse.failure(
            error=GatewayKernel._make_error(
                status_code=404,
                code="ROUTE_NOT_FOUND",
                message=f"No desktop route for path: {path}",
            ),
        )

    async def _handle_runtime(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "version": "1.0.0",
            "status": "running",
            "session_id": str(uuid4()),
            "uptime_seconds": 0,
            "capabilities": [
                "file_interaction",
                "notifications",
                "sync",
                "offline",
                "updates",
                "command_palette",
                "diagnostics",
                "audit",
                "permissions",
            ],
            "gateway_connected": True,
        })

    async def _handle_permissions(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "permissions",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_sync(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "sync",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_files(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "files",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_notifications(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "notifications",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_diagnostics(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "diagnostics",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_offline(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "offline",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_updates(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "updates",
            "status": "available",
            "protocol": "desktop-ipc",
        })

    async def _handle_integrations(self, request: GatewayRequest) -> GatewayResponse:
        return GatewayResponse.ok({
            "service": "integrations",
            "status": "available",
            "protocol": "desktop-ipc",
        })


@dataclass
class DesktopGatewayBridge:
    kernel: GatewayKernel | None = None
    routing_engine: RoutingEngine | None = None
    executor: DesktopRouteExecutor | None = None
    _client: httpx.AsyncClient | None = None
    _gateway_url: str = "http://127.0.0.1:8080"
    _connected: bool = False
    _session_id: str = field(default_factory=lambda: str(uuid4()))

    @classmethod
    def create(cls, gateway_url: str = "http://127.0.0.1:8080") -> DesktopGatewayBridge:
        routing_engine = RoutingEngine()
        executor = DesktopRouteExecutor()

        routes = [
            RouteDefinition(
                identifier="desktop-runtime",
                subsystem="administration",
                path_prefix="/desktop/runtime",
                supported_protocols=(Protocols.REST,),
                capabilities=("runtime:status",),
            ),
            RouteDefinition(
                identifier="desktop-permissions",
                subsystem="administration",
                path_prefix="/desktop/permissions",
                supported_protocols=(Protocols.REST,),
                capabilities=("permissions:manage",),
            ),
            RouteDefinition(
                identifier="desktop-sync",
                subsystem="administration",
                path_prefix="/desktop/sync",
                supported_protocols=(Protocols.REST,),
                capabilities=("sync:manage",),
            ),
            RouteDefinition(
                identifier="desktop-files",
                subsystem="administration",
                path_prefix="/desktop/files",
                supported_protocols=(Protocols.REST,),
                capabilities=("files:interact",),
            ),
            RouteDefinition(
                identifier="desktop-notifications",
                subsystem="administration",
                path_prefix="/desktop/notifications",
                supported_protocols=(Protocols.REST,),
                capabilities=("notifications:send",),
            ),
            RouteDefinition(
                identifier="desktop-diagnostics",
                subsystem="administration",
                path_prefix="/desktop/diagnostics",
                supported_protocols=(Protocols.REST,),
                capabilities=("diagnostics:read",),
            ),
            RouteDefinition(
                identifier="desktop-offline",
                subsystem="administration",
                path_prefix="/desktop/offline",
                supported_protocols=(Protocols.REST,),
                capabilities=("offline:manage",),
            ),
            RouteDefinition(
                identifier="desktop-updates",
                subsystem="administration",
                path_prefix="/desktop/updates",
                supported_protocols=(Protocols.REST,),
                capabilities=("updates:check",),
            ),
            RouteDefinition(
                identifier="desktop-integrations",
                subsystem="administration",
                path_prefix="/desktop/integrations",
                supported_protocols=(Protocols.REST,),
                capabilities=("integrations:list",),
            ),
        ]

        for route in routes:
            routing_engine.register_route(route)

        kernel = GatewayKernel(
            routing_engine=routing_engine,
            route_executor=executor,
        )

        return cls(
            kernel=kernel,
            routing_engine=routing_engine,
            executor=executor,
            _gateway_url=gateway_url,
            _connected=False,
        )

    async def connect(self) -> bool:
        try:
            self._client = httpx.AsyncClient(base_url=self._gateway_url, timeout=10.0)
            response = await self._client.get("/health")
            if response.status_code == 200:
                self._connected = True
                logger.info("Connected to Service Gateway at %s", self._gateway_url)
                await self._register_with_gateway()
                return True
            logger.warning("Gateway health check failed: %d", response.status_code)
            return False
        except Exception as exc:
            logger.warning("Failed to connect to gateway: %s", exc)
            self._connected = False
            return False

    async def disconnect(self) -> None:
        self._connected = False
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("Disconnected from Service Gateway")

    async def _register_with_gateway(self) -> None:
        if not self._client:
            return
        metadata = ServiceMetadata(
            identifier="jarvis-desktop-intelligence",
            version="1.0.0",
            protocol=Protocols.REST,
            capabilities=(
                "runtime:status",
                "permissions:manage",
                "sync:manage",
                "files:interact",
                "notifications:send",
                "diagnostics:read",
                "offline:manage",
                "updates:check",
                "integrations:list",
            ),
            workspace_visibility=("private",),
            authorization_requirements=("session:active",),
            documentation_references=(
                "docs/architecture.md",
                "docs/runtime-guide.md",
            ),
        )
        try:
            response = await self._client.post(
                "/gateway/register",
                json={
                    "service": "desktop",
                    "metadata": {
                        "identifier": metadata.identifier,
                        "version": metadata.version,
                        "protocol": metadata.protocol,
                        "capabilities": list(metadata.capabilities),
                        "workspace_visibility": list(metadata.workspace_visibility),
                        "authorization_requirements": list(metadata.authorization_requirements),
                        "documentation_references": list(metadata.documentation_references),
                    },
                    "routes": [
                        {
                            "identifier": route.identifier,
                            "subsystem": route.subsystem,
                            "path_prefix": route.path_prefix,
                            "supported_protocols": list(route.supported_protocols),
                        }
                        for route in self.routing_engine.list_routes()
                    ],
                },
            )
            if response.status_code == 200:
                logger.info("Desktop routes registered with gateway")
            else:
                logger.warning("Route registration returned %d", response.status_code)
        except Exception as exc:
            logger.warning("Route registration failed: %s", exc)

    async def handle_request(
        self,
        path: str,
        method: str = "GET",
        payload: object | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> GatewayResponse:
        if not self.kernel:
            return GatewayResponse.failure(
                error=GatewayKernel._make_error(
                    status_code=503,
                    code="GATEWAY_NOT_INITIALIZED",
                    message="Desktop gateway bridge not initialized",
                ),
            )
        request = GatewayRequest.new(
            protocol=Protocols.REST,
            path=path,
            version="1.0",
            method=method,
            session_id=self._session_id,
            headers=headers or {},
            payload=payload,
        )
        return await self.kernel.handle(request)

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def session_id(self) -> str:
        return self._session_id
