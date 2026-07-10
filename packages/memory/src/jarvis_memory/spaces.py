from __future__ import annotations

from collections.abc import Iterable

from jarvis_memory.models import MemoryRecord, MemoryType


class InMemorySpace:
    def __init__(self, *, allowed_types: frozenset[MemoryType] | None = None) -> None:
        self._allowed_types = allowed_types
        self._memories: dict[str, MemoryRecord] = {}

    def put(self, memory: MemoryRecord) -> None:
        if self._allowed_types is not None and memory.memory_type not in self._allowed_types:
            msg = f"Memory type {memory.memory_type} is not allowed in this space"
            raise ValueError(msg)
        self._memories[memory.metadata.identifier] = memory

    def get(self, identifier: str) -> MemoryRecord | None:
        return self._memories.get(identifier)

    def remove(self, identifier: str) -> None:
        self._memories.pop(identifier, None)

    def list(self) -> tuple[MemoryRecord, ...]:
        return tuple(sorted(self._memories.values(), key=lambda memory: memory.metadata.created_at))

    def clear(self) -> None:
        self._memories.clear()

    def purge_expired(self) -> tuple[str, ...]:
        expired_ids = tuple(
            memory.metadata.identifier for memory in self._memories.values() if memory.is_expired()
        )
        for memory_id in expired_ids:
            self._memories.pop(memory_id, None)
        return expired_ids


class WorkingMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.WORKING}))

    def clear_execution(self) -> None:
        self.clear()


class ShortTermMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.SHORT_TERM}))


class LongTermMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.LONG_TERM}))


class EpisodicMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.EPISODIC}))


class SemanticMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.SEMANTIC}))


class ProceduralMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.PROCEDURAL}))


class ConversationMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.CONVERSATION}))


class ProjectMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.PROJECT}))


class WorkspaceMemory(InMemorySpace):
    def __init__(self) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.WORKSPACE}))


class AgentMemory(InMemorySpace):
    def __init__(self, agent_id: str) -> None:
        super().__init__(allowed_types=frozenset({MemoryType.AGENT}))
        self.agent_id = agent_id


class AgentMemoryRegistry:
    def __init__(self) -> None:
        self._spaces: dict[str, AgentMemory] = {}

    def get_space(self, agent_id: str) -> AgentMemory:
        if agent_id not in self._spaces:
            self._spaces[agent_id] = AgentMemory(agent_id=agent_id)
        return self._spaces[agent_id]

    def iter_spaces(self) -> Iterable[AgentMemory]:
        return self._spaces.values()
