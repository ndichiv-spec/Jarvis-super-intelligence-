from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from jarvis_api.gateway.types import GatewayRequest


class RateLimitScope(StrEnum):
    USER = "user"
    WORKSPACE = "workspace"
    ORGANIZATION = "organization"
    EXTENSION = "extension"
    PROTOCOL = "protocol"


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    scope: RateLimitScope
    limit: int
    window: timedelta


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int | None
    retry_after_seconds: int | None
    scope_results: tuple[tuple[RateLimitScope, str], ...]


class RateLimiter:
    def __init__(self, policies: tuple[RateLimitPolicy, ...] = ()) -> None:
        self._policies: list[RateLimitPolicy] = list(policies)
        self._buckets: dict[tuple[RateLimitScope, str], deque[datetime]] = {}

    def add_policy(self, policy: RateLimitPolicy) -> None:
        self._policies.append(policy)

    def evaluate(
        self,
        request: GatewayRequest,
        *,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        current_time = now or datetime.now(tz=UTC)
        applicable: list[tuple[RateLimitPolicy, str, deque[datetime]]] = []

        for policy in self._policies:
            key_value = self._resolve_key(policy.scope, request)
            if key_value is None:
                continue

            bucket_key = (policy.scope, key_value)
            bucket = self._buckets.setdefault(bucket_key, deque())
            self._purge_expired(bucket, current_time=current_time, window=policy.window)

            if len(bucket) >= policy.limit:
                retry_after_seconds = max(
                    int((bucket[0] + policy.window - current_time).total_seconds()),
                    1,
                )
                return RateLimitDecision(
                    allowed=False,
                    remaining=0,
                    retry_after_seconds=retry_after_seconds,
                    scope_results=((policy.scope, key_value),),
                )

            applicable.append((policy, key_value, bucket))

        for _, _, bucket in applicable:
            bucket.append(current_time)

        if not applicable:
            return RateLimitDecision(
                allowed=True,
                remaining=None,
                retry_after_seconds=None,
                scope_results=(),
            )

        remaining = min(policy.limit - len(bucket) for policy, _, bucket in applicable)
        scope_results = tuple((policy.scope, key) for policy, key, _ in applicable)
        return RateLimitDecision(
            allowed=True,
            remaining=max(remaining, 0),
            retry_after_seconds=None,
            scope_results=scope_results,
        )

    def _resolve_key(self, scope: RateLimitScope, request: GatewayRequest) -> str | None:
        if scope is RateLimitScope.USER:
            return request.subject_id
        if scope is RateLimitScope.WORKSPACE:
            return request.workspace_id
        if scope is RateLimitScope.ORGANIZATION:
            return request.organization_id
        if scope is RateLimitScope.EXTENSION:
            return request.extension_id
        if scope is RateLimitScope.PROTOCOL:
            return request.protocol
        return None

    @staticmethod
    def _purge_expired(
        bucket: deque[datetime],
        *,
        current_time: datetime,
        window: timedelta,
    ) -> None:
        while bucket and bucket[0] + window <= current_time:
            bucket.popleft()
