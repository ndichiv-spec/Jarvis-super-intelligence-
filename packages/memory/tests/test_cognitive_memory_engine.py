from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from jarvis_memory.engines import DefaultMemoryPolicyEngine
from jarvis_memory.kernel import MemoryKernel
from jarvis_memory.models import (
    MemoryMetadata,
    MemoryPolicy,
    MemoryPrivacyLevel,
    MemoryRecord,
    MemoryRelationshipType,
    MemoryType,
    MemoryVisibility,
    PolicyScope,
    RankingContext,
    RetrievalQuery,
)
from jarvis_memory.spaces import AgentMemoryRegistry


def build_memory(
    *,
    identifier: str,
    memory_type: MemoryType,
    content: str,
    context: str | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    conversation_id: str | None = None,
    project_id: str | None = None,
    workflow_id: str | None = None,
    workspace_id: str | None = None,
    agent_id: str | None = None,
    importance: float = 0.5,
    confidence: float = 0.7,
    tags: frozenset[str] = frozenset(),
    expires_at: datetime | None = None,
    event_time: datetime | None = None,
) -> MemoryRecord:
    created = created_at or datetime.now(UTC)
    metadata = MemoryMetadata(
        identifier=identifier,
        created_at=created,
        updated_at=updated_at or created,
        confidence=confidence,
        importance=importance,
        source="unit-test",
        visibility=MemoryVisibility.PRIVATE,
        privacy_level=MemoryPrivacyLevel.MEDIUM,
        relationships=(),
        classification=memory_type,
        tags=tags,
    )
    return MemoryRecord(
        metadata=metadata,
        content=content,
        memory_type=memory_type,
        context=context,
        conversation_id=conversation_id,
        project_id=project_id,
        workflow_id=workflow_id,
        workspace_id=workspace_id,
        agent_id=agent_id,
        event_time=event_time,
        expires_at=expires_at,
    )


def test_memory_kernel_store_retrieve_and_update_lifecycle() -> None:
    kernel = MemoryKernel()
    memory = build_memory(
        identifier="m-1", memory_type=MemoryType.LONG_TERM, content="preferred editor"
    )

    kernel.store(memory)
    loaded = kernel.get("m-1")
    assert loaded is not None
    assert loaded.metadata.access_count == 1

    updated = kernel.update("m-1", content="preferred editor is PyCharm", importance=0.9)
    assert updated.content == "preferred editor is PyCharm"
    assert updated.metadata.importance == pytest.approx(0.9)


def test_working_memory_is_temporary_and_cleared_after_execution() -> None:
    kernel = MemoryKernel()
    working = build_memory(
        identifier="w-1", memory_type=MemoryType.WORKING, content="active reasoning"
    )

    kernel.store(working)
    assert len(kernel.working_memory.list()) == 1
    kernel.clear_working_memory()

    assert len(kernel.working_memory.list()) == 0
    assert kernel.get("w-1") is None


def test_short_term_memory_uses_policy_ttl() -> None:
    policy_engine = DefaultMemoryPolicyEngine(
        default_policy=MemoryPolicy(
            policy_id="default",
            name="default",
            short_term_ttl=timedelta(minutes=5),
        )
    )
    kernel = MemoryKernel(policy_engine=policy_engine)
    created = datetime(2026, 1, 1, tzinfo=UTC)
    memory = build_memory(
        identifier="s-1",
        memory_type=MemoryType.SHORT_TERM,
        content="recent interaction",
        created_at=created,
        updated_at=created,
    )

    stored = kernel.store(memory)
    assert stored.expires_at is not None
    assert stored.expires_at > created


def test_conversation_and_project_memory_retrieval_continuity() -> None:
    kernel = MemoryKernel()
    c1 = build_memory(
        identifier="c-1",
        memory_type=MemoryType.CONVERSATION,
        content="Decision: use domain events",
        conversation_id="conv-1",
        project_id="proj-1",
        tags=frozenset({"decision", "architecture"}),
    )
    c2 = build_memory(
        identifier="c-2",
        memory_type=MemoryType.CONVERSATION,
        content="Follow-up on architecture notes",
        conversation_id="conv-2",
        project_id="proj-2",
    )
    kernel.store(c1)
    kernel.store(c2)

    results = kernel.retrieve(
        RetrievalQuery(conversation_id="conv-1", project_id="proj-1", tags=frozenset({"decision"})),
        context=RankingContext(conversation_id="conv-1", project_id="proj-1"),
    )
    assert len(results) == 1
    assert results[0].memory.metadata.identifier == "c-1"


def test_relationship_management_updates_memory_graph() -> None:
    kernel = MemoryKernel()
    parent = build_memory(identifier="p", memory_type=MemoryType.PROJECT, content="milestone")
    child = build_memory(identifier="ch", memory_type=MemoryType.PROJECT, content="task")
    kernel.store(parent)
    kernel.store(child)

    updated_parent = kernel.add_relationship(
        source_id="p",
        target_id="ch",
        relationship_type=MemoryRelationshipType.CHILD,
    )
    assert len(updated_parent.metadata.relationships) == 1
    assert updated_parent.metadata.relationships[0].target_id == "ch"


def test_ranking_engine_prioritizes_relevance() -> None:
    kernel = MemoryKernel()
    now = datetime(2026, 1, 10, tzinfo=UTC)
    low = build_memory(
        identifier="r1",
        memory_type=MemoryType.SEMANTIC,
        content="generic concept",
        updated_at=now - timedelta(days=20),
        importance=0.2,
        confidence=0.3,
    )
    high = build_memory(
        identifier="r2",
        memory_type=MemoryType.SEMANTIC,
        content="active project concept",
        project_id="proj",
        workflow_id="wf",
        updated_at=now - timedelta(days=1),
        importance=0.9,
        confidence=0.95,
    )
    kernel.store(low)
    kernel.store(high)

    ranked = kernel.retrieve(
        RetrievalQuery(),
        context=RankingContext(project_id="proj", workflow_id="wf", now=now),
    )
    assert ranked[0].memory.metadata.identifier == "r2"


def test_consolidation_merges_duplicates_and_preserves_lineage() -> None:
    kernel = MemoryKernel()
    first = build_memory(
        identifier="d-1",
        memory_type=MemoryType.PROCEDURAL,
        content="run build then tests",
        tags=frozenset({"ci"}),
    )
    second = build_memory(
        identifier="d-2",
        memory_type=MemoryType.PROCEDURAL,
        content="run build then tests",
        tags=frozenset({"automation"}),
    )
    kernel.store(first)
    kernel.store(second)

    consolidated = kernel.consolidate()
    assert len(consolidated) == 1
    merged = consolidated[0]
    assert merged.metadata.identifier == "d-1"
    assert "d-1" in merged.metadata.lineage
    assert "d-2" in merged.metadata.lineage
    assert merged.metadata.tags == frozenset({"ci", "automation"})


def test_forgetting_policy_archives_expired_memories() -> None:
    kernel = MemoryKernel()
    expired = build_memory(
        identifier="f-1",
        memory_type=MemoryType.SHORT_TERM,
        content="old context",
        expires_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    kernel.store(expired)

    affected = kernel.apply_policies(now=datetime(2026, 2, 1, tzinfo=UTC))
    assert "f-1" in affected
    loaded = kernel.get("f-1")
    assert loaded is not None and loaded.archived


def test_manual_delete_requires_policy_approval_and_policy_permissions() -> None:
    policy_engine = DefaultMemoryPolicyEngine(
        default_policy=MemoryPolicy(
            policy_id="strict",
            name="strict",
            allow_manual_deletion=True,
            allow_permanent_deletion=False,
        )
    )
    kernel = MemoryKernel(policy_engine=policy_engine)
    memory = build_memory(
        identifier="md-1", memory_type=MemoryType.LONG_TERM, content="important fact"
    )
    kernel.store(memory)

    with pytest.raises(PermissionError):
        kernel.manual_delete("md-1", policy_approved=False)
    with pytest.raises(PermissionError):
        kernel.manual_delete("md-1", policy_approved=True)


def test_policy_engine_scope_resolution() -> None:
    policy_engine = DefaultMemoryPolicyEngine(
        default_policy=MemoryPolicy(
            policy_id="d", name="default", short_term_ttl=timedelta(minutes=10)
        )
    )
    workspace_policy = MemoryPolicy(
        policy_id="w", name="workspace", short_term_ttl=timedelta(hours=1)
    )
    project_policy = MemoryPolicy(policy_id="p", name="project", short_term_ttl=timedelta(hours=2))
    agent_policy = MemoryPolicy(policy_id="a", name="agent", short_term_ttl=timedelta(hours=3))

    policy_engine.set_workspace_policy("ws-1", workspace_policy)
    policy_engine.set_project_policy("proj-1", project_policy)
    policy_engine.set_agent_policy("agent-1", agent_policy)

    assert policy_engine.resolve(PolicyScope(workspace_id="ws-1")).policy_id == "w"
    assert policy_engine.resolve(PolicyScope(project_id="proj-1")).policy_id == "p"
    assert policy_engine.resolve(PolicyScope(agent_id="agent-1")).policy_id == "a"


def test_timeline_reconstruction_is_chronological() -> None:
    kernel = MemoryKernel()
    kernel.store(
        build_memory(
            identifier="t-2",
            memory_type=MemoryType.EPISODIC,
            content="second",
            event_time=datetime(2026, 1, 2, tzinfo=UTC),
        )
    )
    kernel.store(
        build_memory(
            identifier="t-1",
            memory_type=MemoryType.EPISODIC,
            content="first",
            event_time=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )

    timeline = kernel.build_timeline()
    assert [event.identifier for event in timeline] == ["t-1", "t-2"]


def test_agent_memory_registry_is_isolated_per_agent() -> None:
    registry = AgentMemoryRegistry()
    agent_a = registry.get_space("research-agent")
    agent_b = registry.get_space("engineering-agent")

    agent_a.put(
        build_memory(
            identifier="a-1",
            memory_type=MemoryType.AGENT,
            content="research",
            agent_id="research-agent",
        )
    )
    agent_b.put(
        build_memory(
            identifier="b-1",
            memory_type=MemoryType.AGENT,
            content="implementation",
            agent_id="engineering-agent",
        )
    )

    assert [memory.metadata.identifier for memory in agent_a.list()] == ["a-1"]
    assert [memory.metadata.identifier for memory in agent_b.list()] == ["b-1"]


def test_all_memory_types_route_to_expected_spaces() -> None:
    kernel = MemoryKernel()
    values = {
        MemoryType.WORKING: kernel.working_memory,
        MemoryType.SHORT_TERM: kernel.short_term_memory,
        MemoryType.LONG_TERM: kernel.long_term_memory,
        MemoryType.EPISODIC: kernel.episodic_memory,
        MemoryType.SEMANTIC: kernel.semantic_memory,
        MemoryType.PROCEDURAL: kernel.procedural_memory,
        MemoryType.CONVERSATION: kernel.conversation_memory,
        MemoryType.PROJECT: kernel.project_memory,
        MemoryType.WORKSPACE: kernel.workspace_memory,
    }

    for index, (memory_type, space) in enumerate(values.items()):
        kernel.store(
            build_memory(
                identifier=f"x-{index}", memory_type=memory_type, content=memory_type.value
            )
        )
        assert len(space.list()) == 1

    kernel.store(
        build_memory(
            identifier="x-agent",
            memory_type=MemoryType.AGENT,
            content="agent memory",
            agent_id="design-agent",
        )
    )
    assert len(kernel.agent_memory.get_space("design-agent").list()) == 1


def test_retrieval_supports_composite_search_filters() -> None:
    kernel = MemoryKernel()
    base_time = datetime(2026, 1, 1, tzinfo=UTC)
    target = build_memory(
        identifier="q-1",
        memory_type=MemoryType.SEMANTIC,
        content="Python typing protocol guide",
        context="developer guide",
        project_id="proj-typing",
        importance=0.8,
        tags=frozenset({"python", "typing"}),
        created_at=base_time,
        updated_at=base_time,
    )
    kernel.store(target)
    kernel.store(
        build_memory(
            identifier="q-2",
            memory_type=MemoryType.SEMANTIC,
            content="Unrelated guide",
            project_id="proj-other",
            importance=0.3,
            created_at=base_time,
            updated_at=base_time,
        )
    )

    query = RetrievalQuery(
        project_id="proj-typing",
        context="protocol",
        min_importance=0.6,
        tags=frozenset({"python"}),
        from_time=base_time - timedelta(minutes=1),
        to_time=base_time + timedelta(minutes=1),
    )
    result = kernel.retrieve(query)
    assert [item.memory.metadata.identifier for item in result] == ["q-1"]
