import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from jarvis_communication.command_bus import CommandBus
from jarvis_communication.context import ExecutionContext
from jarvis_communication.messages import CommandMessage, Pagination, QueryMessage
from jarvis_communication.pipeline import (
    AuthorizationHook,
    Middleware,
    PipelineEngine,
    ValidationHook,
)
from jarvis_communication.query_bus import (
    ProjectionContract,
    QueryBus,
    QueryCacheHook,
    QueryExecutionOptions,
)


def _run[T](coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro)


def test_command_dispatch_uses_pipeline_hooks_and_handler() -> None:
    calls: list[str] = []

    @dataclass(slots=True)
    class Validation(ValidationHook[CommandMessage[Any]]):
        async def validate(self, request: CommandMessage[Any], context: ExecutionContext) -> None:
            calls.append(f"validate:{request.message_name}:{context.source}")

    @dataclass(slots=True)
    class Authorization(AuthorizationHook[CommandMessage[Any]]):
        async def authorize(self, request: CommandMessage[Any], context: ExecutionContext) -> None:
            calls.append(f"authorize:{request.message_name}:{context.source}")

    @dataclass(slots=True)
    class RecorderMiddleware(Middleware[CommandMessage[Any], str]):
        async def __call__(
            self,
            request: CommandMessage[Any],
            next_handler: Callable[[CommandMessage[Any]], Awaitable[str]],
            context: ExecutionContext,
        ) -> str:
            calls.append(f"middleware.before:{request.message_name}:{context.source}")
            value = await next_handler(request)
            calls.append(f"middleware.after:{request.message_name}:{context.source}")
            return value

    async def command_handler(command: CommandMessage[Any], context: ExecutionContext) -> str:
        calls.append(f"handler:{command.message_name}:{context.source}")
        return "done"

    pipeline: PipelineEngine[CommandMessage[Any], str] = PipelineEngine(
        middlewares=(RecorderMiddleware(),),
        validation_hooks=(Validation(),),
        authorization_hooks=(Authorization(),),
    )
    bus = CommandBus(pipeline=pipeline)
    bus.register_handler("command.create", command_handler)

    result = _run(
        bus.dispatch(
            CommandMessage(message_name="command.create", payload={"id": "1"}),
            context=ExecutionContext.new(source="test-command"),
        )
    )

    assert result.success is True
    assert result.value == "done"
    assert calls == [
        "validate:command.create:test-command",
        "authorize:command.create:test-command",
        "middleware.before:command.create:test-command",
        "handler:command.create:test-command",
        "middleware.after:command.create:test-command",
    ]


def test_query_dispatch_supports_filters_pagination_projection_and_cache() -> None:
    cache: dict[str, Any] = {}

    @dataclass(slots=True)
    class InMemoryCache(QueryCacheHook):
        async def get(self, cache_key: str, context: ExecutionContext) -> Any | None:
            return cache.get(cache_key)

        async def set(self, cache_key: str, value: Any, context: ExecutionContext) -> None:
            cache[cache_key] = value

    @dataclass(slots=True)
    class NameProjection(ProjectionContract):
        async def project(
            self,
            value: Any,
            query: QueryMessage[Any],
            context: ExecutionContext,
        ) -> Any:
            return {"name": value["name"]}

    async def query_handler(query: QueryMessage[Any], context: ExecutionContext) -> dict[str, Any]:
        return {
            "name": query.payload["name"],
            "source": context.source,
            "filters": dict(query.filters),
        }

    bus = QueryBus(cache_hook=InMemoryCache())
    bus.register_handler("query.user", query_handler)
    context = ExecutionContext.new(source="test-query")
    options = QueryExecutionOptions(
        filters={"active": True},
        pagination=Pagination(page=1, page_size=10),
        projection=NameProjection(),
    )

    query: QueryMessage[dict[str, Any]] = QueryMessage(
        message_name="query.user",
        payload={"name": "Ada"},
        filters={"region": "eu"},
    )

    first = _run(bus.dispatch(query, context=context, options=options))
    second = _run(bus.dispatch(query, context=context, options=options))

    assert first.success is True
    assert first.from_cache is False
    assert first.data == {"name": "Ada"}
    assert first.filters == {"region": "eu", "active": True}
    assert first.pagination == Pagination(page=1, page_size=10)
    assert second.from_cache is True
