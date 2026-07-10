from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InMemoryEventIntegration:
    _subscriptions: dict[str, dict[str, str]] = field(default_factory=dict)

    def subscribe(
        self,
        extension_id: str,
        event_type: str,
        handler_id: str,
    ) -> None:
        if extension_id not in self._subscriptions:
            self._subscriptions[extension_id] = {}
        self._subscriptions[extension_id][event_type] = handler_id

    def unsubscribe(self, extension_id: str, event_type: str) -> None:
        subs = self._subscriptions.get(extension_id)
        if subs is not None:
            subs.pop(event_type, None)

    def list_subscriptions(self, extension_id: str) -> tuple[tuple[str, str], ...]:
        subs = self._subscriptions.get(extension_id)
        if subs is None:
            return ()
        return tuple((et, h) for et, h in subs.items())

    def unsubscribe_all(self, extension_id: str) -> None:
        self._subscriptions.pop(extension_id, None)
