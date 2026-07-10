from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from jarvis_memory.engines import (
    DefaultConsolidationEngine,
    DefaultForgettingEngine,
    DefaultMemoryPolicyEngine,
    DefaultRankingEngine,
    DefaultRetrievalEngine,
    DefaultTimelineEngine,
    utc_now,
)
from jarvis_memory.models import (
    MemoryPolicy,
    MemoryRecord,
    MemoryRelationship,
    MemoryRelationshipType,
    MemoryType,
    PolicyScope,
    RankingContext,
    RetrievalQuery,
    ScoredMemory,
    TimelineEvent,
)
from jarvis_memory.protocols import (
    ConsolidationEngine,
    ForgettingEngine,
    MemoryPolicyEngine,
    RankingEngine,
    RetrievalEngine,
    TimelineEngine,
)
from jarvis_memory.spaces import (
    AgentMemoryRegistry,
    ConversationMemory,
    EpisodicMemory,
    LongTermMemory,
    ProceduralMemory,
    ProjectMemory,
    SemanticMemory,
    ShortTermMemory,
    WorkingMemory,
    WorkspaceMemory,
)


class MemoryKernel:
    def __init__(
        self,
        *,
        retrieval_engine: RetrievalEngine | None = None,
        ranking_engine: RankingEngine | None = None,
        consolidation_engine: ConsolidationEngine | None = None,
        forgetting_engine: ForgettingEngine | None = None,
        policy_engine: MemoryPolicyEngine | None = None,
        timeline_engine: TimelineEngine | None = None,
    ) -> None:
        self.working_memory = WorkingMemory()
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        self.conversation_memory = ConversationMemory()
        self.project_memory = ProjectMemory()
        self.workspace_memory = WorkspaceMemory()
        self.agent_memory = AgentMemoryRegistry()

        self._retrieval_engine = retrieval_engine or DefaultRetrievalEngine()
        self._ranking_engine = ranking_engine or DefaultRankingEngine()
        self._consolidation_engine = consolidation_engine or DefaultConsolidationEngine()
        self._forgetting_engine = forgetting_engine or DefaultForgettingEngine()
        self._policy_engine = policy_engine or DefaultMemoryPolicyEngine()
        self._timeline_engine = timeline_engine or DefaultTimelineEngine()

        self._index: dict[str, MemoryRecord] = {}

    def store(self, memory: MemoryRecord, *, scope: PolicyScope | None = None) -> MemoryRecord:
        resolved_scope = scope or self._scope_for(memory)
        policy = self._policy_engine.resolve(resolved_scope)
        prepared = self._apply_store_policy(memory=memory, policy=policy)
        self._index[prepared.metadata.identifier] = prepared
        self._store_in_space(prepared)
        return prepared

    def retrieve(
        self, query: RetrievalQuery, *, context: RankingContext | None = None
    ) -> tuple[ScoredMemory, ...]:
        base = tuple(memory for memory in self._index.values() if not memory.archived)
        matched = self._retrieval_engine.search(base, query)
        ranking_context = context or RankingContext()
        return self._ranking_engine.rank(matched, ranking_context)

    def get(self, identifier: str) -> MemoryRecord | None:
        memory = self._index.get(identifier)
        if memory is None:
            return None
        updated_metadata = replace(
            memory.metadata, access_count=memory.metadata.access_count + 1
        ).touch()
        updated_memory = replace(memory, metadata=updated_metadata)
        self._index[identifier] = updated_memory
        self._store_in_space(updated_memory)
        return updated_memory

    def update(
        self,
        identifier: str,
        *,
        content: str | None = None,
        confidence: float | None = None,
        importance: float | None = None,
        tags: frozenset[str] | None = None,
    ) -> MemoryRecord:
        current = self._index.get(identifier)
        if current is None:
            msg = f"Unknown memory identifier: {identifier}"
            raise KeyError(msg)
        updated = current.with_update(
            content=content,
            confidence=confidence,
            importance=importance,
            tags=tags,
        )
        self._index[identifier] = updated
        self._store_in_space(updated)
        return updated

    def add_relationship(
        self,
        *,
        source_id: str,
        target_id: str,
        relationship_type: MemoryRelationshipType,
    ) -> MemoryRecord:
        source = self._index.get(source_id)
        if source is None:
            msg = f"Unknown source memory identifier: {source_id}"
            raise KeyError(msg)
        related = source.with_relationship(
            MemoryRelationship(target_id=target_id, relationship_type=relationship_type)
        )
        self._index[source_id] = related
        self._store_in_space(related)
        return related

    def apply_policies(self, *, now: datetime | None = None) -> tuple[str, ...]:
        current_time = now or utc_now()
        archived_or_deleted: list[str] = []
        for memory_id, memory in tuple(self._index.items()):
            policy = self._policy_engine.resolve(self._scope_for(memory))
            decision = self._forgetting_engine.evaluate(memory, policy, current_time)
            if decision.delete and policy.allow_permanent_deletion:
                self._remove_memory(memory_id)
                archived_or_deleted.append(memory_id)
                continue
            if decision.archive and not memory.archived:
                archived = replace(memory, archived=True)
                self._index[memory_id] = archived
                self._store_in_space(archived)
                archived_or_deleted.append(memory_id)
        return tuple(archived_or_deleted)

    def consolidate(self) -> tuple[MemoryRecord, ...]:
        consolidated = self._consolidation_engine.consolidate(tuple(self._index.values()))
        self._reset_all_spaces()
        self._index = {}
        for memory in consolidated:
            self._index[memory.metadata.identifier] = memory
            self._store_in_space(memory)
        return consolidated

    def clear_working_memory(self) -> None:
        for memory in self.working_memory.list():
            self._index.pop(memory.metadata.identifier, None)
        self.working_memory.clear_execution()

    def build_timeline(self) -> tuple[TimelineEvent, ...]:
        return self._timeline_engine.build(tuple(self._index.values()))

    def manual_delete(self, identifier: str, *, policy_approved: bool) -> None:
        if not policy_approved:
            msg = "Permanent deletion requires policy approval"
            raise PermissionError(msg)
        memory = self._index.get(identifier)
        if memory is None:
            return
        policy = self._policy_engine.resolve(self._scope_for(memory))
        if not policy.allow_manual_deletion or not policy.allow_permanent_deletion:
            msg = "Policy does not allow permanent deletion"
            raise PermissionError(msg)
        self._remove_memory(identifier)

    def all_memories(self) -> tuple[MemoryRecord, ...]:
        return tuple(sorted(self._index.values(), key=lambda memory: memory.metadata.created_at))

    def _apply_store_policy(self, *, memory: MemoryRecord, policy: MemoryPolicy) -> MemoryRecord:
        if memory.memory_type is MemoryType.SHORT_TERM and memory.expires_at is None:
            return replace(memory, expires_at=utc_now() + policy.short_term_ttl)
        if policy.legal_retention is not None and memory.retention_until is None:
            return replace(
                memory, retention_until=memory.metadata.created_at + policy.legal_retention
            )
        return memory

    def _store_in_space(self, memory: MemoryRecord) -> None:
        if memory.memory_type is MemoryType.WORKING:
            self.working_memory.put(memory)
        elif memory.memory_type is MemoryType.SHORT_TERM:
            self.short_term_memory.put(memory)
        elif memory.memory_type is MemoryType.LONG_TERM:
            self.long_term_memory.put(memory)
        elif memory.memory_type is MemoryType.EPISODIC:
            self.episodic_memory.put(memory)
        elif memory.memory_type is MemoryType.SEMANTIC:
            self.semantic_memory.put(memory)
        elif memory.memory_type is MemoryType.PROCEDURAL:
            self.procedural_memory.put(memory)
        elif memory.memory_type is MemoryType.CONVERSATION:
            self.conversation_memory.put(memory)
        elif memory.memory_type is MemoryType.PROJECT:
            self.project_memory.put(memory)
        elif memory.memory_type is MemoryType.WORKSPACE:
            self.workspace_memory.put(memory)
        elif memory.memory_type is MemoryType.AGENT:
            agent_id = memory.agent_id or "default-agent"
            self.agent_memory.get_space(agent_id).put(memory)

    def _remove_memory(self, identifier: str) -> None:
        memory = self._index.pop(identifier, None)
        if memory is None:
            return
        if memory.memory_type is MemoryType.WORKING:
            self.working_memory.remove(identifier)
        elif memory.memory_type is MemoryType.SHORT_TERM:
            self.short_term_memory.remove(identifier)
        elif memory.memory_type is MemoryType.LONG_TERM:
            self.long_term_memory.remove(identifier)
        elif memory.memory_type is MemoryType.EPISODIC:
            self.episodic_memory.remove(identifier)
        elif memory.memory_type is MemoryType.SEMANTIC:
            self.semantic_memory.remove(identifier)
        elif memory.memory_type is MemoryType.PROCEDURAL:
            self.procedural_memory.remove(identifier)
        elif memory.memory_type is MemoryType.CONVERSATION:
            self.conversation_memory.remove(identifier)
        elif memory.memory_type is MemoryType.PROJECT:
            self.project_memory.remove(identifier)
        elif memory.memory_type is MemoryType.WORKSPACE:
            self.workspace_memory.remove(identifier)
        elif memory.memory_type is MemoryType.AGENT:
            agent_id = memory.agent_id or "default-agent"
            self.agent_memory.get_space(agent_id).remove(identifier)

    def _scope_for(self, memory: MemoryRecord) -> PolicyScope:
        return PolicyScope(
            workspace_id=memory.workspace_id,
            project_id=memory.project_id,
            agent_id=memory.agent_id,
        )

    def _reset_all_spaces(self) -> None:
        self.working_memory.clear()
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        self.episodic_memory.clear()
        self.semantic_memory.clear()
        self.procedural_memory.clear()
        self.conversation_memory.clear()
        self.project_memory.clear()
        self.workspace_memory.clear()
        self.agent_memory = AgentMemoryRegistry()
