from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messages import ErrorMessage, Pagination, QueryMessage, WarningMessage
from jarvis_communication.pipeline import PipelineEngine

QueryHandler = Callable[[QueryMessage[Any], ExecutionContext], Awaitable[Any]]


class QueryCacheHook(Protocol):
    async def get(self, cache_key: str, context: ExecutionContext) -> Any | None: ...

    async def set(self, cache_key: str, value: Any, context: ExecutionContext) -> None: ...


class ProjectionContract(Protocol):
    async def project(
        self,
        value: Any,
        query: QueryMessage[Any],
        context: ExecutionContext,
    ) -> Any: ...


@dataclass(frozen=True, slots=True)
class QueryExecutionOptions:
    filters: Mapping[str, Any] = field(default_factory=dict)
    pagination: Pagination | None = None
    projection: ProjectionContract | None = None


@dataclass(frozen=True, slots=True)
class QueryResult[T]:
    success: bool
    data: T | None = None
    from_cache: bool = False
    pagination: Pagination | None = None
    filters: Mapping[str, Any] = field(default_factory=dict)
    errors: tuple[ErrorMessage, ...] = ()
    warnings: tuple[WarningMessage, ...] = ()


class QueryBus:
    def __init__(
        self,
        *,
        pipeline: PipelineEngine[QueryMessage[Any], Any] | None = None,
        cache_hook: QueryCacheHook | None = None,
    ) -> None:
        self._handlers: dict[str, QueryHandler] = {}
        self._pipeline = pipeline or PipelineEngine()
        self._cache_hook = cache_hook

    def register_handler(self, query_name: str, handler: QueryHandler) -> None:
        self._handlers[query_name] = handler

    async def dispatch(
        self,
        query: QueryMessage[Any],
        *,
        context: ExecutionContext | None = None,
        options: QueryExecutionOptions | None = None,
    ) -> QueryResult[Any]:
        execution_context = context or query.context or ExecutionContext.new(source="query-bus")
        execution_options = options or QueryExecutionOptions()
        effective_filters = {**dict(query.filters), **dict(execution_options.filters)}
        effective_pagination = execution_options.pagination or query.pagination

        handler = self._handlers.get(query.message_name)
        if handler is None:
            error = ErrorMessage(
                message_name="query.not_registered",
                payload={"query_name": query.message_name},
                code="query.handler.not_registered",
                detail=f"No handler registered for query '{query.message_name}'",
                context=execution_context,
            )
            return QueryResult(success=False, filters=effective_filters, errors=(error,))

        cache_key = self._build_cache_key(query, effective_filters, effective_pagination)
        if self._cache_hook is not None:
            cached = await self._cache_hook.get(cache_key, execution_context)
            if cached is not None:
                return QueryResult(
                    success=True,
                    data=cached,
                    from_cache=True,
                    pagination=effective_pagination,
                    filters=effective_filters,
                )

        try:
            raw_result = await self._pipeline.execute(
                query,
                execution_context,
                lambda current_query: handler(current_query, execution_context),
            )
            projected_result = raw_result
            if execution_options.projection is not None:
                projected_result = await execution_options.projection.project(
                    raw_result,
                    query,
                    execution_context,
                )
            if self._cache_hook is not None:
                await self._cache_hook.set(cache_key, projected_result, execution_context)
            return QueryResult(
                success=True,
                data=projected_result,
                pagination=effective_pagination,
                filters=effective_filters,
            )
        except Exception as error:
            failure = ErrorMessage(
                message_name="query.execution_failed",
                payload={"query_name": query.message_name},
                code="query.execution.failed",
                detail=str(error),
                context=execution_context,
            )
            return QueryResult(
                success=False,
                filters=effective_filters,
                pagination=effective_pagination,
                errors=(failure,),
            )

    @staticmethod
    def _build_cache_key(
        query: QueryMessage[Any],
        filters: Mapping[str, Any],
        pagination: Pagination | None,
    ) -> str:
        pagination_token = "none"
        if pagination is not None:
            pagination_token = f"{pagination.page}:{pagination.page_size}:{pagination.total_items}"
        return f"{query.message_name}|{dict(query.payload)}|{dict(filters)}|{pagination_token}"
