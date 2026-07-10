from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class ContextEntry:
    key: str
    value: str
    source_agent_id: str
    context_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class SharedContext:
    _contexts: dict[str, dict[str, ContextEntry]] = field(default_factory=dict)
    _history: dict[str, list[ContextEntry]] = field(default_factory=dict)

    def create_context(self) -> str:
        context_id = f"ctx-{uuid4().hex[:8]}"
        self._contexts[context_id] = {}
        self._history[context_id] = []
        return context_id

    def set(
        self,
        context_id: str,
        key: str,
        value: str,
        source_agent_id: str,
    ) -> ContextEntry:
        if context_id not in self._contexts:
            msg = f"Context not found: {context_id}"
            raise KeyError(msg)
        entry = ContextEntry(
            key=key,
            value=value,
            source_agent_id=source_agent_id,
            context_id=context_id,
        )
        self._contexts[context_id][key] = entry
        self._history[context_id].append(entry)
        return entry

    def get(self, context_id: str, key: str) -> str | None:
        ctx = self._contexts.get(context_id)
        if ctx is None:
            return None
        entry = ctx.get(key)
        return entry.value if entry is not None else None

    def get_entry(self, context_id: str, key: str) -> ContextEntry | None:
        ctx = self._contexts.get(context_id)
        if ctx is None:
            return None
        return ctx.get(key)

    def get_all(self, context_id: str) -> Mapping[str, str]:
        ctx = self._contexts.get(context_id, {})
        return {k: v.value for k, v in ctx.items()}

    def delete(self, context_id: str, key: str) -> bool:
        ctx = self._contexts.get(context_id)
        if ctx is None:
            return False
        return ctx.pop(key, None) is not None

    def destroy_context(self, context_id: str) -> bool:
        if context_id not in self._contexts:
            return False
        self._contexts.pop(context_id, None)
        return True

    def get_history(self, context_id: str) -> tuple[ContextEntry, ...]:
        return tuple(self._history.get(context_id, []))

    def list_contexts(self) -> tuple[str, ...]:
        return tuple(self._contexts.keys())

    def search(self, query: str) -> tuple[ContextEntry, ...]:
        results: list[ContextEntry] = []
        for ctx in self._contexts.values():
            for entry in ctx.values():
                if query.lower() in entry.key.lower() or query.lower() in entry.value.lower():
                    results.append(entry)
        return tuple(results)

    def clear(self) -> None:
        self._contexts.clear()
        self._history.clear()
