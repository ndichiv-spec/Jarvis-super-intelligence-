from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from jarvis_communication.command_bus import CommandBus, CommandResult
from jarvis_communication.context import ExecutionContext
from jarvis_communication.event_bus import EventBus
from jarvis_communication.messages import (
    BaseMessage,
    CommandMessage,
    EventMessage,
    NotificationMessage,
    QueryMessage,
)
from jarvis_communication.query_bus import QueryBus, QueryExecutionOptions, QueryResult
from jarvis_communication.routing import RoutingEngine

NotificationHandler = Callable[[NotificationMessage, ExecutionContext], Awaitable[None]]
GenericHandler = Callable[[BaseMessage, ExecutionContext], Awaitable[None]]


class MessageBus:
    def __init__(
        self,
        *,
        event_bus: EventBus | None = None,
        command_bus: CommandBus | None = None,
        query_bus: QueryBus | None = None,
        routing_engine: RoutingEngine | None = None,
    ) -> None:
        self.event_bus = event_bus or EventBus()
        self.command_bus = command_bus or CommandBus()
        self.query_bus = query_bus or QueryBus()
        self.routing_engine = routing_engine or RoutingEngine()
        self._notification_handlers: dict[str, list[NotificationHandler]] = {}
        self._route_handlers: dict[str, GenericHandler] = {}

    async def publish_event(
        self,
        event: EventMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        await self.event_bus.publish(event, context=context)

    async def dispatch_command(
        self,
        command: CommandMessage[Any],
        *,
        context: ExecutionContext | None = None,
    ) -> CommandResult[Any]:
        return await self.command_bus.dispatch(command, context=context)

    async def dispatch_query(
        self,
        query: QueryMessage[Any],
        *,
        context: ExecutionContext | None = None,
        options: QueryExecutionOptions | None = None,
    ) -> QueryResult[Any]:
        return await self.query_bus.dispatch(query, context=context, options=options)

    def subscribe_notification(
        self,
        notification_name: str,
        handler: NotificationHandler,
    ) -> None:
        handlers = self._notification_handlers.setdefault(notification_name, [])
        handlers.append(handler)

    async def publish_notification(
        self,
        notification: NotificationMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        execution_context = (
            context
            or notification.context
            or ExecutionContext.new(source="message-bus")
        )
        for handler in self._notification_handlers.get(notification.message_name, []):
            await handler(notification, execution_context)

    def register_route_handler(self, handler_name: str, handler: GenericHandler) -> None:
        self._route_handlers[handler_name] = handler

    async def route_message(
        self,
        message: BaseMessage,
        *,
        context: ExecutionContext,
        target: str | None = None,
    ) -> tuple[str, ...]:
        decision = self.routing_engine.resolve(message, context, target=target)
        for handler_name in decision.handlers:
            handler = self._route_handlers.get(handler_name)
            if handler is not None:
                await handler(message, context)
        return decision.handlers
