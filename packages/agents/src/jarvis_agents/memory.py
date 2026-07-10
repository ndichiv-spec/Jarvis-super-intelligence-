from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InMemoryMemoryInterface:
    _store: dict[str, dict[str, str]] = field(default_factory=dict)

    def store(self, agent_id: str, key: str, value: str) -> None:
        if agent_id not in self._store:
            self._store[agent_id] = {}
        self._store[agent_id][key] = value

    def retrieve(self, agent_id: str, key: str) -> str | None:
        return self._store.get(agent_id, {}).get(key)

    def search(self, agent_id: str, query: str) -> tuple[str, ...]:
        results: list[str] = []
        agent_store = self._store.get(agent_id, {})
        for key, value in agent_store.items():
            if query.lower() in key.lower() or query.lower() in value.lower():
                results.append(f"{key}: {value}")
        return tuple(results)

    def delete(self, agent_id: str, key: str) -> None:
        if agent_id in self._store:
            self._store[agent_id].pop(key, None)
