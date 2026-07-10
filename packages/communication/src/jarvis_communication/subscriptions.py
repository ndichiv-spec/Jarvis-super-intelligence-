from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from jarvis_communication.context import ExecutionContext
from jarvis_communication.models import Subscription, SubscriptionType


class SubscriptionManager:
    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}
        self._target_subscriptions: dict[str, list[str]] = {}

    async def subscribe(
        self,
        subscriber_id: str,
        subscription_type: SubscriptionType,
        target_id: str,
        *,
        metadata: dict[str, Any] | None = None,
        context: ExecutionContext | None = None,
    ) -> Subscription:
        subscription = Subscription(
            subscriber_id=subscriber_id,
            subscription_type=subscription_type,
            target_id=target_id,
            metadata=metadata or {},
        )
        self._subscriptions[subscription.subscription_id] = subscription
        self._target_subscriptions.setdefault(target_id, []).append(
            subscription.subscription_id
        )
        return subscription

    async def unsubscribe(
        self,
        subscription_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        subscription = self._subscriptions.pop(subscription_id, None)
        if subscription is None:
            return False
        target_list = self._target_subscriptions.get(subscription.target_id, [])
        if subscription_id in target_list:
            target_list.remove(subscription_id)
        return True

    async def get(
        self,
        subscription_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> Subscription | None:
        return self._subscriptions.get(subscription_id)

    async def list_by_subscriber(
        self,
        subscriber_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Subscription]:
        return [
            sub
            for sub in self._subscriptions.values()
            if sub.subscriber_id == subscriber_id and sub.active
        ]

    async def list_by_target(
        self,
        target_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[Subscription]:
        subscription_ids = self._target_subscriptions.get(target_id, [])
        return [
            self._subscriptions[sid]
            for sid in subscription_ids
            if sid in self._subscriptions and self._subscriptions[sid].active
        ]

    async def list_subscribers(
        self,
        target_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> list[str]:
        return [
            sub.subscriber_id
            for sub in await self.list_by_target(target_id, context=context)
        ]

    async def deactivate(
        self,
        subscription_id: str,
        *,
        context: ExecutionContext | None = None,
    ) -> bool:
        subscription = self._subscriptions.get(subscription_id)
        if subscription is None:
            return False
        updated = Subscription(
            subscription_id=subscription.subscription_id,
            subscriber_id=subscription.subscriber_id,
            subscription_type=subscription.subscription_type,
            target_id=subscription.target_id,
            created_at=subscription.created_at,
            active=False,
            metadata=subscription.metadata,
        )
        self._subscriptions[subscription_id] = updated
        return True

    @property
    def total_subscriptions(self) -> int:
        return len(self._subscriptions)
