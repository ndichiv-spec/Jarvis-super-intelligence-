from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from jarvis_knowledge.engines import (
    DefaultKnowledgeClassificationEngine,
    DefaultKnowledgePolicyEngine,
    DefaultKnowledgeRankingEngine,
    DefaultKnowledgeSearchEngine,
    DefaultKnowledgeValidationEngine,
    InMemoryCitationEngine,
    InMemoryKnowledgeVersionManager,
    default_classification,
)
from jarvis_knowledge.graph import InMemoryKnowledgeGraph
from jarvis_knowledge.kernel import KnowledgeKernel
from jarvis_knowledge.models import (
    KnowledgeAccessContext,
    KnowledgeCitationType,
    KnowledgeClassification,
    KnowledgeCollection,
    KnowledgeDocument,
    KnowledgeImportance,
    KnowledgeMetadata,
    KnowledgePolicy,
    KnowledgePolicyScope,
    KnowledgeRankingContext,
    KnowledgeRelationship,
    KnowledgeRelationshipType,
    KnowledgeSearchQuery,
    KnowledgeSensitivity,
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeVisibility,
)
from jarvis_knowledge.protocols import (
    KnowledgePolicyEngine,
)


def make_source(
    *,
    source_id: str | None = None,
    name: str = "Test Source",
    source_type: KnowledgeSourceType = KnowledgeSourceType.DOCUMENTATION,
    owner: str = "user-1",
    workspace: str = "ws-1",
    project: str = "proj-1",
    quality_score: float = 0.8,
) -> KnowledgeSource:
    return KnowledgeSource(
        source_id=source_id or f"src-{uuid4().hex[:8]}",
        name=name,
        source_type=source_type,
        owner=owner,
        workspace=workspace,
        project=project,
        description=f"Source: {name}",
        quality_score=quality_score,
    )


def make_collection(
    *,
    collection_id: str | None = None,
    name: str = "General",
    domain: str = "general",
    owner: str = "user-1",
    workspace: str = "ws-1",
    project: str = "proj-1",
    visibility: KnowledgeVisibility = KnowledgeVisibility.WORKSPACE,
) -> KnowledgeCollection:
    return KnowledgeCollection(
        collection_id=collection_id or f"col-{uuid4().hex[:8]}",
        name=name,
        domain=domain,
        owner=owner,
        workspace=workspace,
        project=project,
        visibility=visibility,
    )


def make_document(
    *,
    identifier: str | None = None,
    title: str = "Test Document",
    summary: str = "A test knowledge document",
    content_reference: str = "/docs/test.md",
    source_id: str = "src-1",
    owner: str = "user-1",
    workspace: str = "ws-1",
    project: str = "proj-1",
    language: str = "en",
    version: int = 1,
    visibility: KnowledgeVisibility = KnowledgeVisibility.WORKSPACE,
    confidence: float = 0.8,
    collection_ids: tuple[str, ...] = (),
    relationships: tuple[KnowledgeRelationship, ...] = (),
    tags: frozenset[str] = frozenset(),
    domain: str = "general",
    topic: str = "general",
    category: str = "general",
) -> KnowledgeDocument:
    classification = KnowledgeClassification(
        domain=domain,
        topic=topic,
        category=category,
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=visibility,
        language=language,
        workspace=workspace,
        project=project,
        tags=tags,
    )
    metadata = KnowledgeMetadata(
        identifier=identifier or f"doc-{uuid4().hex[:8]}",
        title=title,
        description=f"Description of {title}",
        owner=owner,
        workspace=workspace,
        project=project,
        classification=classification,
        tags=tags,
        language=language,
        version=version,
        visibility=visibility,
        confidence=confidence,
        relationships=relationships,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return KnowledgeDocument(
        metadata=metadata,
        summary=summary,
        content_reference=content_reference,
        source_id=source_id,
        collection_ids=collection_ids,
    )


def make_kernel(
    *,
    source: KnowledgeSource | None = None,
    collection: KnowledgeCollection | None = None,
    policy_engine: KnowledgePolicyEngine | None = None,
) -> tuple[KnowledgeKernel, KnowledgeSource, KnowledgeCollection]:
    kernel = KnowledgeKernel(policy_engine=policy_engine)
    src = source or make_source(source_id="src-main")
    col = collection or make_collection()
    kernel.register_source(src)
    kernel.register_collection(col)
    return kernel, src, col


def register(
    kernel: KnowledgeKernel,
    document: KnowledgeDocument,
    *,
    policy_scope: KnowledgePolicyScope | None = None,
    policy: KnowledgePolicy | None = None,
) -> KnowledgeDocument:
    if policy_scope is not None and policy is not None:
        kernel.register_policy(policy_scope, policy)
    return kernel.register_knowledge(document)


# ---------------------------------------------------------------------------
# Knowledge Registration
# ---------------------------------------------------------------------------


def test_knowledge_registration_lifecycle() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(source_id=src.source_id, collection_ids=(col.collection_id,))
    registered = kernel.register_knowledge(doc)
    assert registered.metadata.identifier == doc.metadata.identifier
    assert registered.metadata.version == 1

    retrieved = kernel.retrieve_knowledge(
        doc.metadata.identifier,
        access=KnowledgeAccessContext(requester_id="user-1", workspace="ws-1", project="proj-1"),
    )
    assert retrieved is not None
    assert retrieved.metadata.identifier == doc.metadata.identifier


def test_knowledge_registration_fails_for_unregistered_source() -> None:
    kernel = KnowledgeKernel()
    doc = make_document(source_id="nonexistent-source")
    with pytest.raises(KeyError, match="source is not registered"):
        kernel.register_knowledge(doc)


def test_knowledge_registration_fails_for_invalid_document() -> None:
    kernel, src, _ = make_kernel()
    doc = make_document(source_id=src.source_id, title="", summary="")
    with pytest.raises(ValueError, match="validation failed"):
        kernel.register_knowledge(doc)


# ---------------------------------------------------------------------------
# Knowledge Retrieval and Access Control
# ---------------------------------------------------------------------------


def test_retrieve_knowledge_requires_access() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        workspace="workspace-a",
        project="project-a",
        owner="user-1",
    )
    kernel.register_knowledge(doc)

    result = kernel.retrieve_knowledge(
        doc.metadata.identifier,
        access=KnowledgeAccessContext(
            requester_id="user-2", workspace="workspace-b", project="project-b"
        ),
    )
    assert result is None


def test_retrieve_knowledge_returns_none_for_missing() -> None:
    kernel = KnowledgeKernel()
    result = kernel.retrieve_knowledge(
        "does-not-exist",
        access=KnowledgeAccessContext(requester_id="user-1", workspace="ws-1", project="proj-1"),
    )
    assert result is None


# ---------------------------------------------------------------------------
# Knowledge Update
# ---------------------------------------------------------------------------


def test_knowledge_update_lifecycle() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(source_id=src.source_id, collection_ids=(col.collection_id,))
    registered = kernel.register_knowledge(doc)

    updated = kernel.update_knowledge(
        registered.metadata.identifier,
        summary="Updated summary",
        changed_by="user-1",
        change_summary="Updated content",
    )
    assert updated.summary == "Updated summary"
    assert updated.metadata.version > registered.metadata.version


def test_knowledge_update_fails_for_missing() -> None:
    kernel = KnowledgeKernel()
    with pytest.raises(KeyError, match="not found"):
        kernel.update_knowledge(
            "nonexistent",
            changed_by="user-1",
            change_summary="fail",
        )


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def test_classification_engine_applies_collection_domain() -> None:
    engine = DefaultKnowledgeClassificationEngine()
    src = make_source(source_id="src")
    col = make_collection(domain="engineering", name="Programming")
    doc = make_document(source_id="src", collection_ids=(col.collection_id,))

    result = engine.classify(document=doc, source=src, collections=(col,))
    assert result.domain == "engineering"
    assert result.category == "Programming"


def test_classification_engine_falls_back_to_document_defaults() -> None:
    engine = DefaultKnowledgeClassificationEngine()
    src = make_source(source_id="src")
    doc = make_document(source_id="src", domain="science")
    result = engine.classify(document=doc, source=src, collections=())
    assert result.domain == "science"
    assert result.category == "general"


def test_classify_knowledge_updates_document() -> None:
    kernel, src, col = make_kernel()
    col2 = make_collection(collection_id="col-2", domain="engineering", name="Backend")
    kernel.register_collection(col2)
    doc = make_document(
        source_id=src.source_id, collection_ids=(col2.collection_id, col.collection_id)
    )
    registered = kernel.register_knowledge(doc)

    reclassified = kernel.classify_knowledge(registered.metadata.identifier)
    assert reclassified.metadata.classification.domain == "engineering"


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------


def test_relationship_management() -> None:
    kernel, src, col = make_kernel()
    parent = make_document(
        identifier="doc-parent",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        title="Parent Document",
    )
    child = make_document(
        identifier="doc-child",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        title="Child Document",
    )
    kernel.register_knowledge(parent)
    kernel.register_knowledge(child)

    linked = kernel.link_knowledge(
        source_identifier="doc-parent",
        target_identifier="doc-child",
        relationship_type=KnowledgeRelationshipType.PARENT,
    )
    assert len(linked.metadata.relationships) == 1
    assert linked.metadata.relationships[0].target_id == "doc-child"
    assert linked.metadata.relationships[0].relationship_type == KnowledgeRelationshipType.PARENT


def test_relationship_to_nonexistent_target_raises() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(source_id=src.source_id, collection_ids=(col.collection_id,))
    kernel.register_knowledge(doc)
    with pytest.raises(KeyError, match="not found"):
        kernel.link_knowledge(
            source_identifier=doc.metadata.identifier,
            target_identifier="does-not-exist",
            relationship_type=KnowledgeRelationshipType.REFERENCE,
        )


def test_relationship_from_nonexistent_source_raises() -> None:
    kernel = KnowledgeKernel()
    with pytest.raises(KeyError, match="not found"):
        kernel.link_knowledge(
            source_identifier="missing",
            target_identifier="also-missing",
            relationship_type=KnowledgeRelationshipType.REFERENCE,
        )


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------


def test_knowledge_graph_neighbors() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.link(source_id="a", target_id="c", relationship_type=KnowledgeRelationshipType.DEPENDS_ON)

    neighbors = graph.neighbors(source_id="a")
    assert len(neighbors) == 2

    ref_neighbors = graph.neighbors(
        source_id="a", relationship_type=KnowledgeRelationshipType.REFERENCE
    )
    assert len(ref_neighbors) == 1
    assert ref_neighbors[0].target_id == "b"


def test_knowledge_graph_does_not_duplicate_links() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="x", target_id="y", relationship_type=KnowledgeRelationshipType.RELATED_TO)
    graph.link(source_id="x", target_id="y", relationship_type=KnowledgeRelationshipType.RELATED_TO)

    assert len(graph.neighbors(source_id="x")) == 1


def test_kernel_graph_neighbors() -> None:
    kernel, src, col = make_kernel()
    a = make_document(
        identifier="graph-a", source_id=src.source_id, collection_ids=(col.collection_id,)
    )
    b = make_document(
        identifier="graph-b", source_id=src.source_id, collection_ids=(col.collection_id,)
    )
    kernel.register_knowledge(a)
    kernel.register_knowledge(b)
    kernel.link_knowledge(
        source_identifier="graph-a",
        target_identifier="graph-b",
        relationship_type=KnowledgeRelationshipType.EXPLAINS,
    )

    neighbors = kernel.neighbors("graph-a")
    assert len(neighbors) == 1
    assert neighbors[0].target_id == "graph-b"


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def test_search_engine_exact_identifier() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="find-me", title="Target")
    doc2 = make_document(identifier="other", title="Other")
    query = KnowledgeSearchQuery(identifier="find-me")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "find-me"


def test_search_engine_by_title_substring() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", title="Python Architecture Guide")
    doc2 = make_document(identifier="d2", title="Java Best Practices")
    query = KnowledgeSearchQuery(title="python")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d1"


def test_search_engine_by_category() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", category="tutorial")
    doc2 = make_document(identifier="d2", category="reference")
    query = KnowledgeSearchQuery(category="reference")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d2"


def test_search_engine_by_topic() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", topic="containers")
    doc2 = make_document(identifier="d2", topic="networking")
    query = KnowledgeSearchQuery(topic="containers")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d1"


def test_search_engine_by_tags() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", tags=frozenset({"python", "typing"}))
    doc2 = make_document(identifier="d2", tags=frozenset({"java"}))
    query = KnowledgeSearchQuery(tags=frozenset({"python", "typing"}))
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d1"


def test_search_engine_by_workspace() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", workspace="ws-alpha")
    doc2 = make_document(identifier="d2", workspace="ws-beta")
    query = KnowledgeSearchQuery(workspace="ws-alpha")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1


def test_search_engine_by_project() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", project="proj-x")
    doc2 = make_document(identifier="d2", project="proj-y")
    query = KnowledgeSearchQuery(project="proj-x")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1


def test_search_engine_by_owner() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", owner="alice")
    doc2 = make_document(identifier="d2", owner="bob")
    query = KnowledgeSearchQuery(owner="alice")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1


def test_search_engine_by_language() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1", language="en")
    doc2 = make_document(identifier="d2", language="fr")
    query = KnowledgeSearchQuery(language="fr")
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1


def test_search_engine_by_relationship_type() -> None:
    engine = DefaultKnowledgeSearchEngine()
    rel = KnowledgeRelationship(
        target_id="target-1", relationship_type=KnowledgeRelationshipType.DEPENDS_ON
    )
    doc1 = make_document(identifier="d1", relationships=(rel,))
    doc2 = make_document(identifier="d2")
    query = KnowledgeSearchQuery(relationship_type=KnowledgeRelationshipType.DEPENDS_ON)
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1


def test_search_engine_by_metadata_filters() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(identifier="d1")
    doc1_with_attr = doc1.with_update()
    doc1_with_attr_typed = KnowledgeDocument(
        metadata=doc1_with_attr.metadata,
        summary=doc1_with_attr.summary,
        content_reference=doc1_with_attr.content_reference,
        source_id=doc1_with_attr.source_id,
        collection_ids=doc1_with_attr.collection_ids,
        attributes={"framework": "pytest"},
    )
    query = KnowledgeSearchQuery(metadata_filters={"framework": "pytest"})
    results = engine.search((doc1_with_attr_typed, make_document(identifier="d2")), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d1"


def test_search_engine_by_text_terms() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(
        identifier="d1", title="Database Design", summary="How to design relational databases"
    )
    doc2 = make_document(identifier="d2", title="API Development", summary="Building REST APIs")
    query = KnowledgeSearchQuery(terms=("database", "design"))
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d1"


def test_search_engine_composite_query() -> None:
    engine = DefaultKnowledgeSearchEngine()
    doc1 = make_document(
        identifier="d1",
        title="Python Guide",
        workspace="ws-1",
        project="proj-1",
        tags=frozenset({"python"}),
        topic="programming",
    )
    doc2 = make_document(
        identifier="d2",
        title="Java Guide",
        workspace="ws-1",
        project="proj-2",
        tags=frozenset({"java"}),
        topic="programming",
    )
    query = KnowledgeSearchQuery(
        terms=("guide",),
        workspace="ws-1",
        project="proj-1",
        tags=frozenset({"python"}),
    )
    results = engine.search((doc1, doc2), query)
    assert len(results) == 1
    assert results[0].metadata.identifier == "d1"


def test_search_engine_respects_limit() -> None:
    engine = DefaultKnowledgeSearchEngine()
    docs = tuple(make_document(identifier=f"d{i}", title="Same Title") for i in range(5))
    query = KnowledgeSearchQuery(title="Same Title", limit=3)
    results = engine.search(docs, query)
    assert len(results) == 3


def test_kernel_search_filters_by_access() -> None:
    kernel, src, col = make_kernel()
    doc1 = make_document(
        identifier="search-a",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        workspace="ws-1",
        project="proj-1",
    )
    doc2 = make_document(
        identifier="search-b",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        workspace="ws-2",
        project="proj-2",
    )
    kernel.register_knowledge(doc1)
    kernel.register_knowledge(doc2)

    results = kernel.search_knowledge(
        KnowledgeSearchQuery(),
        access=KnowledgeAccessContext(requester_id="user-1", workspace="ws-1", project="proj-1"),
    )
    assert any(s.document.metadata.identifier == "search-a" for s in results)
    assert not any(s.document.metadata.identifier == "search-b" for s in results)


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def test_ranking_engine_orders_by_relevance() -> None:
    engine = DefaultKnowledgeRankingEngine()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    low = make_document(identifier="r-low", title="Generic", summary="something else")
    high = make_document(identifier="r-high", title="Python Guide", summary="Learn Python")

    context = KnowledgeRankingContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
        query_terms=("python",),
        now=now,
    )
    ranked = engine.rank((low, high), context)
    assert ranked[0].document.metadata.identifier == "r-high"
    assert ranked[0].score > ranked[1].score


def test_ranking_engine_prioritizes_higher_confidence() -> None:
    engine = DefaultKnowledgeRankingEngine()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    low = make_document(identifier="r-c1", confidence=0.3, title="A", summary="same")
    high = make_document(identifier="r-c2", confidence=0.9, title="B", summary="same")

    context = KnowledgeRankingContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
        now=now,
    )
    ranked = engine.rank((low, high), context)
    assert ranked[0].document.metadata.identifier == "r-c2"


def test_ranking_engine_boosts_workspace_and_project_context() -> None:
    engine = DefaultKnowledgeRankingEngine()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    same_ws = make_document(identifier="r-ws", workspace="ws-1", project="proj-1")
    diff_ws = make_document(identifier="r-other", workspace="ws-2", project="proj-2")

    context = KnowledgeRankingContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
        now=now,
    )
    ranked = engine.rank((same_ws, diff_ws), context)
    assert ranked[0].document.metadata.identifier == "r-ws"


def test_ranking_engine_freshness_decays_with_age() -> None:
    engine = DefaultKnowledgeRankingEngine()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    old = make_document(
        identifier="r-old",
        title="Old Doc",
    )
    old_with_past = KnowledgeDocument(
        metadata=old.metadata.touch(updated_at=now - timedelta(days=500)),
        summary=old.summary,
        content_reference=old.content_reference,
        source_id=old.source_id,
        collection_ids=old.collection_ids,
    )
    fresh = make_document(identifier="r-fresh", title="Fresh Doc")

    context = KnowledgeRankingContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
        now=now,
    )
    ranked = engine.rank((old_with_past, fresh), context)
    assert ranked[0].document.metadata.identifier == "r-fresh"


def test_kernel_rank_delegates_to_engine() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(source_id=src.source_id, collection_ids=(col.collection_id,))
    kernel.register_knowledge(doc)

    context = KnowledgeRankingContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
    )
    ranked = kernel.rank_knowledge((doc,), context=context)
    assert len(ranked) == 1
    assert ranked[0].document.metadata.identifier == doc.metadata.identifier


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_validation_engine_passes_for_valid_document() -> None:
    engine = DefaultKnowledgeValidationEngine()
    src = make_source(source_id="src-v")
    catalog = type(
        "FakeCatalog", (), {"get_source": lambda self, _: src, "get_document": lambda self, _: None}
    )()
    doc = make_document(source_id="src-v")
    report = engine.validate(document=doc, catalog=catalog)
    assert report.is_valid
    assert report.completeness == 1.0
    assert report.consistency == 1.0
    assert report.integrity == 1.0


def test_validation_engine_reports_incomplete_document() -> None:
    engine = DefaultKnowledgeValidationEngine()
    src = make_source(source_id="src-v")
    catalog = type(
        "FakeCatalog", (), {"get_source": lambda self, _: src, "get_document": lambda self, _: None}
    )()
    doc = make_document(source_id="src-v", title="", summary="")
    report = engine.validate(document=doc, catalog=catalog)
    assert not report.is_valid
    assert report.completeness < 1.0


def test_validation_engine_reports_classification_inconsistency() -> None:
    engine = DefaultKnowledgeValidationEngine()
    src = make_source(source_id="src-v")
    catalog = type(
        "FakeCatalog", (), {"get_source": lambda self, _: src, "get_document": lambda self, _: None}
    )()
    bad_classification = KnowledgeClassification(
        domain="x",
        topic="x",
        category="x",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language="en",
        workspace="wrong-ws",
        project="wrong-proj",
    )
    meta = KnowledgeMetadata(
        identifier="doc-v",
        title="Test",
        description="d",
        owner="u",
        workspace="ws-1",
        project="proj-1",
        classification=bad_classification,
        tags=frozenset(),
        language="en",
        version=1,
        visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8,
        relationships=(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    doc = KnowledgeDocument(metadata=meta, summary="s", content_reference="c", source_id="src-v")
    report = engine.validate(document=doc, catalog=catalog)
    assert not report.is_valid
    assert report.consistency < 1.0


def test_validation_engine_reports_integrity_violation() -> None:
    engine = DefaultKnowledgeValidationEngine()
    src = make_source(source_id="src-v")
    catalog = type(
        "FakeCatalog", (), {"get_source": lambda self, _: src, "get_document": lambda self, _: None}
    )()
    doc = make_document(source_id="src-v", confidence=-0.1)
    report = engine.validate(document=doc, catalog=catalog)
    assert not report.is_valid
    assert report.integrity < 1.0


def test_validation_engine_reports_missing_source() -> None:
    engine = DefaultKnowledgeValidationEngine()
    catalog = type(
        "FakeCatalog",
        (),
        {"get_source": lambda self, _: None, "get_document": lambda self, _: None},
    )()
    doc = make_document(source_id="src-missing")
    report = engine.validate(document=doc, catalog=catalog)
    assert not report.is_valid
    assert report.source_quality == 0.0


def test_validation_engine_reports_low_source_quality() -> None:
    engine = DefaultKnowledgeValidationEngine()
    src = make_source(source_id="src-v", quality_score=0.1)
    catalog = type(
        "FakeCatalog", (), {"get_source": lambda self, _: src, "get_document": lambda self, _: None}
    )()
    doc = make_document(source_id="src-v")
    report = engine.validate(document=doc, catalog=catalog)
    assert report.is_valid
    assert report.source_quality == 0.1
    assert any(issue.code == "low_source_quality" for issue in report.issues)


def test_validation_engine_reports_broken_relationships() -> None:
    engine = DefaultKnowledgeValidationEngine()
    src = make_source(source_id="src-v")
    existing_doc = make_document(identifier="existing-doc", source_id="src-v")
    catalog = type(
        "FakeCatalog",
        (),
        {
            "get_source": lambda self, _: src,
            "get_document": lambda self, id: existing_doc if id == "existing-doc" else None,
        },
    )()
    broken_rel = KnowledgeRelationship(
        target_id="nonexistent-target",
        relationship_type=KnowledgeRelationshipType.REFERENCE,
    )
    doc = make_document(source_id="src-v", relationships=(broken_rel,))
    report = engine.validate(document=doc, catalog=catalog)
    assert not report.is_valid
    assert report.relationship_integrity < 1.0


def test_kernel_validate_delegates_to_engine() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(source_id=src.source_id, collection_ids=(col.collection_id,))
    registered = kernel.register_knowledge(doc)
    report = kernel.validate_knowledge(registered.metadata.identifier)
    assert report.document_id == registered.metadata.identifier
    assert report.is_valid


def test_kernel_validate_fails_for_missing() -> None:
    kernel = KnowledgeKernel()
    with pytest.raises(KeyError, match="not found"):
        kernel.validate_knowledge("nonexistent")


# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------


def test_version_manager_registers_initial() -> None:
    vm = InMemoryKnowledgeVersionManager()
    doc = make_document(identifier="ver-doc")
    vm.register_initial(doc)
    current = vm.current_version("ver-doc")
    assert current is not None
    assert current.number == 1
    assert current.change_summary == "Initial registration"


def test_version_manager_records_subsequent_versions() -> None:
    vm = InMemoryKnowledgeVersionManager()
    doc = make_document(identifier="ver-doc")
    vm.register_initial(doc)
    updated = vm.record_version(document=doc, changed_by="user-1", change_summary="First update")
    assert updated.metadata.version == 2
    current = vm.current_version("ver-doc")
    assert current is not None
    assert current.number == 2


def test_version_manager_tracks_history() -> None:
    vm = InMemoryKnowledgeVersionManager()
    doc = make_document(identifier="ver-doc")
    vm.register_initial(doc)
    vm.record_version(document=doc, changed_by="user-1", change_summary="Update 1")
    vm.record_version(document=doc, changed_by="user-2", change_summary="Update 2")

    history = vm.history("ver-doc")
    assert len(history) == 3
    assert history[0].number == 1
    assert history[1].number == 2
    assert history[2].number == 3


def test_version_manager_compatibility() -> None:
    vm = InMemoryKnowledgeVersionManager()
    doc = make_document(identifier="ver-doc")
    vm.register_initial(doc)
    assert vm.is_compatible("ver-doc", 1) is True
    assert vm.is_compatible("ver-doc", 2) is False


def test_version_manager_compatibility_with_custom() -> None:
    vm = InMemoryKnowledgeVersionManager()
    doc = make_document(identifier="ver-doc")
    vm.register_initial(doc)
    vm.record_version(document=doc, changed_by="u", change_summary="v2", compatible_with=(1, 2))
    assert vm.is_compatible("ver-doc", 1) is True
    assert vm.is_compatible("ver-doc", 2) is True


def test_version_manager_current_none_for_unknown() -> None:
    vm = InMemoryKnowledgeVersionManager()
    assert vm.current_version("unknown") is None
    assert vm.history("unknown") == ()


def test_version_manager_register_initial_is_idempotent() -> None:
    vm = InMemoryKnowledgeVersionManager()
    doc = make_document(identifier="ver-doc")
    vm.register_initial(doc)
    vm.register_initial(doc)
    assert len(vm.history("ver-doc")) == 1


def test_kernel_version_history_and_compatibility() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(source_id=src.source_id, collection_ids=(col.collection_id,))
    registered = kernel.register_knowledge(doc)

    kernel.update_knowledge(
        registered.metadata.identifier,
        summary="v2",
        changed_by="user-1",
        change_summary="Second version",
    )

    history = kernel.version_history(registered.metadata.identifier)
    assert len(history) == 2
    assert history[0].number == 1
    assert history[1].number == 2
    assert kernel.is_version_compatible(registered.metadata.identifier, 2) is True


# ---------------------------------------------------------------------------
# Citation Management
# ---------------------------------------------------------------------------


def test_citation_engine_create_and_list() -> None:
    engine = InMemoryCitationEngine()
    cit = engine.create_citation(
        from_document_id="doc-1",
        to_reference="https://example.com/ref",
        citation_type=KnowledgeCitationType.EXTERNAL,
    )
    assert cit.from_document_id == "doc-1"
    assert cit.to_reference == "https://example.com/ref"

    citations = engine.list_citations("doc-1")
    assert len(citations) == 1
    assert citations[0].citation_id == cit.citation_id


def test_citation_engine_list_empty_for_unknown() -> None:
    engine = InMemoryCitationEngine()
    assert engine.list_citations("unknown") == ()


def test_kernel_create_citation() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(
        identifier="cit-doc",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
    )
    kernel.register_knowledge(doc)

    citation = kernel.create_citation(
        from_document_id="cit-doc",
        to_reference="https://example.com/knowledge",
        citation_type=KnowledgeCitationType.EXTERNAL,
    )
    assert citation.from_document_id == "cit-doc"
    assert citation.to_reference == "https://example.com/knowledge"

    citations = kernel.list_citations("cit-doc")
    assert len(citations) == 1


def test_kernel_create_citation_links_to_known_document() -> None:
    kernel, src, col = make_kernel()
    doc_a = make_document(
        identifier="cit-a",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
    )
    doc_b = make_document(
        identifier="cit-b",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
    )
    kernel.register_knowledge(doc_a)
    kernel.register_knowledge(doc_b)

    kernel.create_citation(
        from_document_id="cit-a",
        to_reference="cit-b",
        citation_type=KnowledgeCitationType.INTERNAL,
    )
    neighbors = kernel.neighbors("cit-a")
    assert any(n.target_id == "cit-b" for n in neighbors)


def test_kernel_create_citation_fails_for_missing_source() -> None:
    kernel = KnowledgeKernel()
    with pytest.raises(KeyError, match="not found"):
        kernel.create_citation(
            from_document_id="ghost",
            to_reference="anything",
            citation_type=KnowledgeCitationType.INTERNAL,
        )


# ---------------------------------------------------------------------------
# Policy Engine
# ---------------------------------------------------------------------------


def test_policy_engine_default_resolution() -> None:
    engine = DefaultKnowledgePolicyEngine()
    scope = KnowledgePolicyScope(owner="u1", workspace="ws-1", project="proj-1")
    policy = engine.resolve(scope)
    assert policy.policy_id == "default"


def test_policy_engine_enterprise_resolution() -> None:
    engine = DefaultKnowledgePolicyEngine()
    scope = KnowledgePolicyScope(owner="u1", workspace="ws-1", project="proj-1", is_enterprise=True)
    policy = engine.resolve(scope)
    assert policy.policy_id == "enterprise-default"


def test_policy_engine_custom_registration() -> None:
    engine = DefaultKnowledgePolicyEngine()
    scope = KnowledgePolicyScope(owner="u1", workspace="ws-1", project="proj-1")
    custom = KnowledgePolicy(policy_id="custom", name="Custom Policy", retention_days=90)
    engine.register_policy(scope, custom)
    resolved = engine.resolve(scope)
    assert resolved.policy_id == "custom"
    assert resolved.retention_days == 90


def test_policy_engine_access_visibility() -> None:
    engine = DefaultKnowledgePolicyEngine()
    policy = KnowledgePolicy(
        policy_id="strict",
        name="Strict",
        allowed_visibility=(KnowledgeVisibility.PRIVATE, KnowledgeVisibility.WORKSPACE),
    )
    doc_private = make_document(owner="u1", visibility=KnowledgeVisibility.PRIVATE)
    doc_public = make_document(owner="u1", visibility=KnowledgeVisibility.PUBLIC)

    access = KnowledgeAccessContext(requester_id="u1", workspace="ws-1", project="proj-1")
    assert engine.can_access(document=doc_private, access=access, policy=policy) is True
    assert engine.can_access(document=doc_public, access=access, policy=policy) is False


def test_policy_engine_workspace_isolation() -> None:
    engine = DefaultKnowledgePolicyEngine()
    policy = KnowledgePolicy(
        policy_id="iso",
        name="Isolated",
        workspace_isolation=True,
    )
    doc = make_document(workspace="ws-a")
    same = KnowledgeAccessContext(requester_id="u", workspace="ws-a", project="proj-1")
    diff = KnowledgeAccessContext(requester_id="u", workspace="ws-b", project="proj-1")
    assert engine.can_access(document=doc, access=same, policy=policy) is True
    assert engine.can_access(document=doc, access=diff, policy=policy) is False


def test_policy_engine_project_ownership() -> None:
    engine = DefaultKnowledgePolicyEngine()
    policy = KnowledgePolicy(
        policy_id="owner",
        name="Owner Enforced",
        enforce_project_ownership=True,
    )
    doc = make_document(project="proj-x")
    same = KnowledgeAccessContext(requester_id="u", workspace="ws-1", project="proj-x")
    diff = KnowledgeAccessContext(requester_id="u", workspace="ws-1", project="proj-y")
    assert engine.can_access(document=doc, access=same, policy=policy) is True
    assert engine.can_access(document=doc, access=diff, policy=policy) is False


def test_policy_engine_private_visibility_restricts_owner() -> None:
    engine = DefaultKnowledgePolicyEngine()
    policy = KnowledgePolicy(policy_id="d", name="Default")
    doc = make_document(owner="alice", visibility=KnowledgeVisibility.PRIVATE)
    alice = KnowledgeAccessContext(requester_id="alice", workspace="ws-1", project="proj-1")
    bob = KnowledgeAccessContext(requester_id="bob", workspace="ws-1", project="proj-1")
    assert engine.can_access(document=doc, access=alice, policy=policy) is True
    assert engine.can_access(document=doc, access=bob, policy=policy) is False


# ---------------------------------------------------------------------------
# In-Memory Catalog
# ---------------------------------------------------------------------------


def test_catalog_source_lifecycle() -> None:
    from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog

    catalog = InMemoryKnowledgeCatalog()
    src = make_source(source_id="src-cat")
    catalog.register_source(src)
    assert catalog.get_source("src-cat") is src
    assert catalog.get_source("missing") is None


def test_catalog_collection_lifecycle() -> None:
    from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog

    catalog = InMemoryKnowledgeCatalog()
    col = make_collection(collection_id="col-cat")
    catalog.register_collection(col)
    assert catalog.get_collection("col-cat") is col
    assert catalog.get_collection("missing") is None


def test_catalog_document_lifecycle() -> None:
    from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog

    catalog = InMemoryKnowledgeCatalog()
    doc = make_document(identifier="doc-cat")
    catalog.register_document(doc)
    assert catalog.get_document("doc-cat") is doc
    assert catalog.get_document("missing") is None

    updated = make_document(identifier="doc-cat", title="Updated")
    catalog.update_document(updated)
    assert catalog.get_document("doc-cat").metadata.title == "Updated"

    docs = catalog.list_documents()
    assert len(docs) == 1


def test_catalog_update_unknown_raises() -> None:
    from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog

    catalog = InMemoryKnowledgeCatalog()
    doc = make_document(identifier="ghost")
    with pytest.raises(KeyError, match="not registered"):
        catalog.update_document(doc)


# ---------------------------------------------------------------------------
# Knowledge Graph Contract
# ---------------------------------------------------------------------------


def test_graph_contracts() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(
        source_id="n1", target_id="n2", relationship_type=KnowledgeRelationshipType.REFERENCE
    )
    graph.link(
        source_id="n1", target_id="n3", relationship_type=KnowledgeRelationshipType.REFERENCE
    )
    graph.link(
        source_id="n2", target_id="n3", relationship_type=KnowledgeRelationshipType.DEPENDS_ON
    )

    assert len(graph.neighbors(source_id="n1")) == 2
    assert len(graph.neighbors(source_id="n2")) == 1
    assert graph.neighbors(source_id="n3") == ()
    assert (
        len(graph.neighbors(source_id="n1", relationship_type=KnowledgeRelationshipType.REFERENCE))
        == 2
    )


# ---------------------------------------------------------------------------
# Knowledge Kernel Behavior
# ---------------------------------------------------------------------------


def test_kernel_register_source_and_collection() -> None:
    kernel = KnowledgeKernel()
    src = make_source(source_id="new-src")
    col = make_collection(collection_id="new-col")
    kernel.register_source(src)
    kernel.register_collection(col)
    doc = make_document(source_id="new-src", collection_ids=("new-col",))
    result = kernel.register_knowledge(doc)
    assert result is not None


def test_kernel_register_policy_and_validate() -> None:
    kernel, src, col = make_kernel()
    scope = KnowledgePolicyScope(owner="admin", workspace="ws-1", project="proj-1")
    policy = KnowledgePolicy(
        policy_id="strict",
        name="Strict Policy",
        allowed_visibility=(KnowledgeVisibility.PRIVATE,),
        workspace_isolation=True,
    )
    kernel.register_policy(scope, policy)

    doc = make_document(
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        visibility=KnowledgeVisibility.PRIVATE,
        owner="admin",
    )
    registered = kernel.register_knowledge(doc)
    retrieved = kernel.retrieve_knowledge(
        registered.metadata.identifier,
        access=KnowledgeAccessContext(requester_id="admin", workspace="ws-1", project="proj-1"),
    )
    assert retrieved is not None


def test_kernel_full_lifecycle() -> None:
    kernel, src, col = make_kernel()
    doc = make_document(
        identifier="lifecycle-doc",
        source_id=src.source_id,
        collection_ids=(col.collection_id,),
        title="Architecture Decision Record",
        summary="Decision to use domain-driven design",
        content_reference="/docs/adr-001.md",
        tags=frozenset({"architecture", "ddd"}),
    )

    registered = kernel.register_knowledge(doc)
    assert registered.metadata.version == 1

    linked = kernel.link_knowledge(
        source_identifier="lifecycle-doc",
        target_identifier="lifecycle-doc",
        relationship_type=KnowledgeRelationshipType.REFERENCE,
    )
    assert len(linked.metadata.relationships) >= 1

    updated = kernel.update_knowledge(
        "lifecycle-doc",
        summary="Updated: Use tactical DDD patterns",
        changed_by="user-1",
        change_summary="Refined guidance",
    )
    assert updated.metadata.version == 2

    report = kernel.validate_knowledge("lifecycle-doc")
    assert report.is_valid

    citation = kernel.create_citation(
        from_document_id="lifecycle-doc",
        to_reference="https://example.com/ddd",
        citation_type=KnowledgeCitationType.EXTERNAL,
    )
    assert citation is not None

    results = kernel.search_knowledge(
        KnowledgeSearchQuery(terms=("architecture",), workspace="ws-1", project="proj-1"),
        access=KnowledgeAccessContext(requester_id="user-1", workspace="ws-1", project="proj-1"),
    )
    assert len(results) >= 1


# ---------------------------------------------------------------------------
# Default Classification Helper
# ---------------------------------------------------------------------------


def test_default_classification_helper() -> None:
    cls = default_classification(workspace="ws-helper", project="proj-helper", language="en")
    assert cls.workspace == "ws-helper"
    assert cls.project == "proj-helper"
    assert cls.language == "en"
    assert cls.importance == KnowledgeImportance.NORMAL
    assert cls.sensitivity == KnowledgeSensitivity.INTERNAL


# ---------------------------------------------------------------------------
# Knowledge Metadata
# ---------------------------------------------------------------------------


def test_knowledge_metadata_touch_increments_version() -> None:
    now = datetime.now(UTC)
    meta = KnowledgeMetadata(
        identifier="meta-1",
        title="Test",
        description="d",
        owner="u",
        workspace="ws",
        project="proj",
        classification=default_classification(workspace="ws", project="proj", language="en"),
        tags=frozenset(),
        language="en",
        version=1,
        visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8,
        relationships=(),
        created_at=now,
        updated_at=now,
    )
    touched = meta.touch()
    assert touched.version == 2
    assert touched.updated_at > now


def test_knowledge_metadata_touch_preserves_explicit() -> None:
    now = datetime.now(UTC)
    meta = KnowledgeMetadata(
        identifier="meta-2",
        title="Test",
        description="d",
        owner="u",
        workspace="ws",
        project="proj",
        classification=default_classification(workspace="ws", project="proj", language="en"),
        tags=frozenset(),
        language="en",
        version=5,
        visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8,
        relationships=(),
        created_at=now,
        updated_at=now,
    )
    result = meta.touch(version=10)
    assert result.version == 10


# ---------------------------------------------------------------------------
# Knowledge Document with_update / with_relationship
# ---------------------------------------------------------------------------


def test_document_with_update() -> None:
    doc = make_document(identifier="upd-doc", summary="Original", confidence=0.5)
    updated = doc.with_update(summary="New Summary", confidence=0.9)
    assert updated.summary == "New Summary"
    assert updated.metadata.confidence == 0.9
    assert updated.metadata.version == doc.metadata.version + 1


def test_document_with_relationship() -> None:
    doc = make_document(identifier="rel-doc")
    rel = KnowledgeRelationship(
        target_id="some-target",
        relationship_type=KnowledgeRelationshipType.REFERENCE,
    )
    updated = doc.with_relationship(rel)
    assert len(updated.metadata.relationships) == 1
    assert updated.metadata.relationships[0].target_id == "some-target"


def test_document_with_update_preserves_specified_fields() -> None:
    doc = make_document(
        identifier="upd2",
        summary="S1",
        content_reference="ref1",
        tags=frozenset({"a"}),
        confidence=0.5,
    )
    updated = doc.with_update(summary="S2")
    assert updated.summary == "S2"
    assert updated.content_reference == "ref1"
    assert updated.metadata.tags == frozenset({"a"})
    assert updated.metadata.confidence == 0.5


# ---------------------------------------------------------------------------
# KnowledgeClassification with_overrides
# ---------------------------------------------------------------------------


def test_classification_with_overrides() -> None:
    cls = default_classification(workspace="ws", project="proj", language="en")
    overridden = cls.with_overrides(domain="engineering", tags=frozenset({"new-tag"}))
    assert overridden.domain == "engineering"
    assert overridden.workspace == "ws"
    assert overridden.tags == frozenset({"new-tag"})


def test_classification_with_overrides_none_keeps_original() -> None:
    cls = default_classification(workspace="ws", project="proj", language="en")
    overridden = cls.with_overrides(domain="science")
    assert overridden.topic == cls.topic
    assert overridden.category == cls.category
