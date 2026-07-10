from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from jarvis_communication.context import ExecutionContext
from jarvis_communication.messages import BaseMessage


class DispatchMode(StrEnum):
    BROADCAST = "broadcast"
    DIRECTED = "directed"
    GROUPED = "grouped"


@dataclass(frozen=True, slots=True)
class Route:
    handler_name: str
    message_name: str | None = None
    priority: int = 0
    mode: DispatchMode = DispatchMode.BROADCAST
    destination: str | None = None
    group: str | None = None
    condition: Callable[[BaseMessage, ExecutionContext], bool] | None = None

    def matches(
        self,
        message: BaseMessage,
        context: ExecutionContext,
        *,
        target: str | None,
    ) -> bool:
        if self.message_name is not None and self.message_name != message.message_name:
            return False
        if self.mode is DispatchMode.DIRECTED and target is not None and self.destination != target:
            return False
        if self.mode is DispatchMode.DIRECTED and target is None:
            return False
        if self.condition is not None and not self.condition(message, context):
            return False
        return True


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    handlers: tuple[str, ...]


class RoutingEngine:
    def __init__(self) -> None:
        self._routes: list[Route] = []

    def register(self, route: Route) -> None:
        self._routes.append(route)

    def resolve(
        self,
        message: BaseMessage,
        context: ExecutionContext,
        *,
        target: str | None = None,
    ) -> RoutingDecision:
        matching = [
            route
            for route in self._routes
            if route.matches(message, context, target=target)
        ]

        grouped: dict[str, Route] = {}
        direct_or_broadcast: list[Route] = []
        for route in matching:
            if route.mode is DispatchMode.GROUPED:
                group_name = route.group or route.handler_name
                current = grouped.get(group_name)
                if current is None or route.priority > current.priority:
                    grouped[group_name] = route
            else:
                direct_or_broadcast.append(route)

        selected = [*direct_or_broadcast, *grouped.values()]
        selected.sort(key=lambda route: route.priority, reverse=True)
        return RoutingDecision(handlers=tuple(route.handler_name for route in selected))
