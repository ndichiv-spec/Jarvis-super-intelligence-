from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from jarvis_agents.models import (
    AgentCommunicationRequest,
    AgentCommunicationResponse,
    AgentEvent,
)


@dataclass(slots=True)
class InMemoryCommunicationBus:
    _requests: dict[str, list[AgentCommunicationRequest]] = field(default_factory=dict)
    _responses: dict[str, list[AgentCommunicationResponse]] = field(default_factory=dict)
    _events: dict[str, list[AgentEvent]] = field(default_factory=dict)
    _all_events: list[AgentEvent] = field(default_factory=list)
    _subscriptions: dict[str, list[Callable[[AgentEvent], None]]] = field(default_factory=dict)
    _event_filters: dict[str, list[str]] = field(default_factory=dict)

    def send_request(self, request: AgentCommunicationRequest) -> None:
        target = request.target_agent_id
        if target not in self._requests:
            self._requests[target] = []
        self._requests[target].append(request)

    def send_response(self, response: AgentCommunicationResponse) -> None:
        correlation = response.correlation_id
        if correlation not in self._responses:
            self._responses[correlation] = []
        self._responses[correlation].append(response)

    def publish_event(self, event: AgentEvent) -> None:
        self._all_events.append(event)
        if event.broadcast:
            for agent_id in list(self._events.keys()):
                self._events[agent_id].append(event)
        else:
            target = event.source_agent_id
            if target not in self._events:
                self._events[target] = []
            self._events[target].append(event)
        self._dispatch_to_subscribers(event)

    def subscribe(self, subscriber_id: str, handler: Callable[[AgentEvent], None]) -> None:
        if subscriber_id not in self._subscriptions:
            self._subscriptions[subscriber_id] = []
        self._subscriptions[subscriber_id].append(handler)

    def unsubscribe(self, subscriber_id: str, handler: Callable[[AgentEvent], None]) -> None:
        handlers = self._subscriptions.get(subscriber_id, [])
        if handler in handlers:
            handlers.remove(handler)

    def add_event_filter(self, subscriber_id: str, event_type: str) -> None:
        if subscriber_id not in self._event_filters:
            self._event_filters[subscriber_id] = []
        self._event_filters[subscriber_id].append(event_type)

    def remove_event_filter(self, subscriber_id: str, event_type: str) -> None:
        filters = self._event_filters.get(subscriber_id, [])
        if event_type in filters:
            filters.remove(event_type)

    def _dispatch_to_subscribers(self, event: AgentEvent) -> None:
        for subscriber_id, handlers in self._subscriptions.items():
            filters = self._event_filters.get(subscriber_id, [])
            if filters and event.event_type not in filters:
                continue
            for handler in handlers:
                handler(event)

    def pending_requests(self, agent_id: str) -> tuple[AgentCommunicationRequest, ...]:
        if agent_id not in self._requests:
            self._requests[agent_id] = []
        return tuple(self._requests[agent_id])

    def pending_responses(self, correlation_id: str) -> tuple[AgentCommunicationResponse, ...]:
        if correlation_id not in self._responses:
            self._responses[correlation_id] = []
        return tuple(self._responses[correlation_id])

    def pending_events(self, agent_id: str) -> tuple[AgentEvent, ...]:
        if agent_id not in self._events:
            self._events[agent_id] = []
        return tuple(self._events[agent_id])

    def drain_requests(self, agent_id: str) -> tuple[AgentCommunicationRequest, ...]:
        requests = tuple(self._requests.get(agent_id, []))
        self._requests[agent_id] = []
        return requests

    def drain_events(self, agent_id: str) -> tuple[AgentEvent, ...]:
        events = tuple(self._events.get(agent_id, []))
        self._events[agent_id] = []
        return events

    def event_count(self) -> int:
        return len(self._all_events)

    def clear(self) -> None:
        self._requests.clear()
        self._responses.clear()
        self._events.clear()
        self._all_events.clear()
