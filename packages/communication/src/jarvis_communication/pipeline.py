from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from datetime import timedelta
from time import perf_counter
from typing import Protocol, TypeVar

from jarvis_communication.context import ExecutionContext

RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")
RequestContraT = TypeVar("RequestContraT", contravariant=True)
ResponseContraT = TypeVar("ResponseContraT", contravariant=True)
RetryRequestT = TypeVar("RetryRequestT", contravariant=True)
RetryResponseT = TypeVar("RetryResponseT")
MiddlewareRequestT = TypeVar("MiddlewareRequestT")
MiddlewareResponseT = TypeVar("MiddlewareResponseT")


class ValidationHook(Protocol[RequestContraT]):
    async def validate(self, request: RequestContraT, context: ExecutionContext) -> None: ...


class AuthorizationHook(Protocol[RequestContraT]):
    async def authorize(self, request: RequestContraT, context: ExecutionContext) -> None: ...


class LoggingHook(Protocol[RequestContraT, ResponseContraT]):
    async def on_start(self, request: RequestContraT, context: ExecutionContext) -> None: ...

    async def on_success(
        self,
        request: RequestContraT,
        response: ResponseContraT,
        context: ExecutionContext,
    ) -> None: ...

    async def on_failure(
        self,
        request: RequestContraT,
        error: Exception,
        context: ExecutionContext,
    ) -> None: ...


class RetryHook(Protocol[RetryRequestT, RetryResponseT]):
    async def execute(
        self,
        request: RetryRequestT,
        context: ExecutionContext,
        operation: Callable[[], Awaitable[RetryResponseT]],
    ) -> RetryResponseT: ...


class MetricsHook(Protocol[RequestContraT]):
    async def on_success(
        self,
        request: RequestContraT,
        context: ExecutionContext,
        duration: timedelta,
    ) -> None: ...

    async def on_failure(
        self,
        request: RequestContraT,
        context: ExecutionContext,
        duration: timedelta,
    ) -> None: ...


class Middleware(Protocol[MiddlewareRequestT, MiddlewareResponseT]):
    async def __call__(
        self,
        request: MiddlewareRequestT,
        next_handler: Callable[[MiddlewareRequestT], Awaitable[MiddlewareResponseT]],
        context: ExecutionContext,
    ) -> MiddlewareResponseT: ...


@dataclass(slots=True)
class PipelineEngine[RequestT, ResponseT]:
    middlewares: Sequence[Middleware[RequestT, ResponseT]] = ()
    validation_hooks: Sequence[ValidationHook[RequestT]] = ()
    authorization_hooks: Sequence[AuthorizationHook[RequestT]] = ()
    logging_hooks: Sequence[LoggingHook[RequestT, ResponseT]] = ()
    metrics_hooks: Sequence[MetricsHook[RequestT]] = ()
    retry_hook: RetryHook[RequestT, ResponseT] | None = None

    async def execute(
        self,
        request: RequestT,
        context: ExecutionContext,
        handler: Callable[[RequestT], Awaitable[ResponseT]],
    ) -> ResponseT:
        for validation_hook in self.validation_hooks:
            await validation_hook.validate(request, context)
        for authorization_hook in self.authorization_hooks:
            await authorization_hook.authorize(request, context)
        for logging_hook in self.logging_hooks:
            await logging_hook.on_start(request, context)

        chain = self._build_chain(handler, context)
        started_at = perf_counter()

        try:
            if self.retry_hook is not None:
                response = await self.retry_hook.execute(
                    request,
                    context,
                    lambda: chain(request),
                )
            else:
                response = await chain(request)
        except Exception as error:
            duration = timedelta(seconds=perf_counter() - started_at)
            for logging_hook in self.logging_hooks:
                await logging_hook.on_failure(request, error, context)
            for metrics_hook in self.metrics_hooks:
                await metrics_hook.on_failure(request, context, duration)
            raise

        duration = timedelta(seconds=perf_counter() - started_at)
        for logging_hook in self.logging_hooks:
            await logging_hook.on_success(request, response, context)
        for metrics_hook in self.metrics_hooks:
            await metrics_hook.on_success(request, context, duration)
        return response

    def _build_chain(
        self,
        handler: Callable[[RequestT], Awaitable[ResponseT]],
        context: ExecutionContext,
    ) -> Callable[[RequestT], Awaitable[ResponseT]]:
        chain = handler
        for middleware in reversed(self.middlewares):
            next_handler = chain

            async def wrapped(
                request: RequestT,
                *,
                current_middleware: Middleware[RequestT, ResponseT] = middleware,
                current_next: Callable[[RequestT], Awaitable[ResponseT]] = next_handler,
            ) -> ResponseT:
                return await current_middleware(request, current_next, context)

            chain = wrapped
        return chain
