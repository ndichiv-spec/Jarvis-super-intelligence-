from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from jarvis_communication.context import ExecutionContext
from jarvis_communication.contracts import DeadLetterSink, EventReplayProvider
from jarvis_communication.messages import EventMessage

EventHandler = Callable[[EventMessage, ExecutionContext], Awaitable[None]]
EventFilter = Callable[[EventMessage, ExecutionContext], bool]


@dataclass(frozen=True, slots=True)
class EventSubscription:
    subscription_id: str
    handler: EventHandler
    event_name: str | None = None
    priority: int = 0
    event_filter: EventFilter | None = None
    once: bool = False

    def matches(self, event: EventMessage, context: ExecutionContext) -> bool:
        if self.event_name is not None and self.event_name != event.message_name:
            return False
        if self.event_filter is not None and not self.event_filter(event, context):
            return False
        return True


class EventBus:
    def __init__(self, *, dead_letter_sink: DeadLetterSink | None = None) -> None:
        self._subscriptions: list[EventSubscription] = []
        self._dead_letter_sink = dead_letter_sink

    def subscribe(
        self,
        handler: EventHandler,
        *,
        event_name: str | None = None,
        priority: int = 0,
        event_filter: EventFilter | None = None,
    ) -> str:
        subscription = EventSubscription(
            subscription_id=uuid4().hex,
            handler=handler,
            event_name=event_name,
            priority=priority,
            event_filter=event_filter,
        )
        self._subscriptions.append(subscription)
        return subscription.subscription_id

    def subscribe_once(
        self,
        handler: EventHandler,
        *,
        event_name: str | None = None,
        priority: int = 0,
        event_filter: EventFilter | None = None,
    ) -> str:
        subscription = EventSubscription(
            subscription_id=uuid4().hex,
            handler=handler,
            event_name=event_name,
            priority=priority,
            event_filter=event_filter,
            once=True,
        )
        self._subscriptions.append(subscription)
        return subscription.subscription_id

    def unsubscribe(self, subscription_id: str) -> None:
        self._subscriptions = [
            subscription
            for subscription in self._subscriptions
            if subscription.subscription_id != subscription_id
        ]

    async def publish(
        self,
        event: EventMessage,
        *,
        context: ExecutionContext | None = None,
    ) -> None:
        execution_context = context or event.context or ExecutionContext.new(source="event-bus")
        matching = [
            subscription
            for subscription in self._subscriptions
            if subscription.matches(event, execution_context)
        ]
        matching.sort(key=lambda subscription: subscription.priority, reverse=True)

        once_completed: list[str] = []
        for subscription in matching:
            try:
                await subscription.handler(event, execution_context)
            except Exception as error:
                if self._dead_letter_sink is not None:
                    await self._dead_letter_sink.publish_dead_letter(
                        event,
                        execution_context,
                        error,
                    )
            finally:
                if subscription.once:
                    once_completed.append(subscription.subscription_id)

        if once_completed:
            one_shot_ids = set(once_completed)
            self._subscriptions = [
                subscription
                for subscription in self._subscriptions
                if subscription.subscription_id not in one_shot_ids
            ]

    async def replay(
        self,
        replay_provider: EventReplayProvider,
        *,
        context: ExecutionContext,
        event_name: str | None = None,
        from_timestamp: datetime | None = None,
    ) -> None:
        async for replayed_event in replay_provider.replay(
            event_name=event_name,
            from_timestamp=from_timestamp,
        ):
            await self.publish(replayed_event, context=context.child(source="event-replay"))
