from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from jarvis_api.gateway.types import GatewayRequest, GatewayResponse


@runtime_checkable
class RequestValidatorProtocol(Protocol):
    async def validate(self, request: GatewayRequest) -> None: ...


@runtime_checkable
class AuthorizationServiceProtocol(Protocol):
    async def authorize(self, request: GatewayRequest, route: object) -> None: ...


@runtime_checkable
class RouteExecutorProtocol(Protocol):
    async def execute(self, request: GatewayRequest, route: object) -> GatewayResponse: ...


@runtime_checkable
class RequestMiddlewareProtocol(Protocol):
    async def handle(self, request: GatewayRequest) -> GatewayRequest: ...


@runtime_checkable
class ResponseMiddlewareProtocol(Protocol):
    async def handle(self, response: GatewayResponse) -> GatewayResponse: ...


@runtime_checkable
class ObservabilityProtocol(Protocol):
    def log(
        self,
        level: str,
        message: str,
        *,
        context: Mapping[str, object] | None = None,
    ) -> None: ...

    def increment(self, metric_name: str, *, tags: Mapping[str, str] | None = None) -> None: ...

    def record_latency(
        self,
        metric_name: str,
        milliseconds: float,
        *,
        tags: Mapping[str, str] | None = None,
    ) -> None: ...

    def health(self) -> Mapping[str, object]: ...

    def stats(self) -> Mapping[str, object]: ...
