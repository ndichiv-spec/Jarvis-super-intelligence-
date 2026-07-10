from __future__ import annotations

from collections.abc import Iterable

from jarvis_api.gateway.protocols import RequestMiddlewareProtocol, ResponseMiddlewareProtocol
from jarvis_api.gateway.types import GatewayRequest, GatewayResponse


class RequestPipeline:
    def __init__(self, middlewares: Iterable[RequestMiddlewareProtocol] | None = None) -> None:
        self._middlewares: list[RequestMiddlewareProtocol] = list(middlewares or ())

    def add_middleware(self, middleware: RequestMiddlewareProtocol) -> None:
        self._middlewares.append(middleware)

    async def execute(self, request: GatewayRequest) -> GatewayRequest:
        current = request
        for middleware in self._middlewares:
            current = await middleware.handle(current)
        return current


class ResponsePipeline:
    def __init__(self, middlewares: Iterable[ResponseMiddlewareProtocol] | None = None) -> None:
        self._middlewares: list[ResponseMiddlewareProtocol] = list(middlewares or ())

    def add_middleware(self, middleware: ResponseMiddlewareProtocol) -> None:
        self._middlewares.append(middleware)

    async def execute(self, response: GatewayResponse) -> GatewayResponse:
        current = response
        for middleware in self._middlewares:
            current = await middleware.handle(current)
        return current
