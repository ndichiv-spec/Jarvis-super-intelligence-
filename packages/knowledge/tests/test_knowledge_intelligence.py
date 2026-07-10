from __future__ import annotations

from jarvis_knowledge.ingestion import DefaultIngestionEngine, IngestionManifest
from jarvis_knowledge.models import KnowledgeSourceType
from jarvis_knowledge.parser import MarkdownParser, PlainTextParser
from jarvis_knowledge.chunking import FixedSizeChunker, ParagraphChunker, HeadingAwareChunker
from jarvis_knowledge.embeddings import TfidfEmbeddingEngine, RandomEmbeddingEngine
from jarvis_knowledge.indexing import DefaultIndexingEngine, SearchIndex
from jarvis_knowledge.retrieval import SimilarityRetrievalEngine
from jarvis_knowledge.reranking import PassThroughReranker, DiversityReranker
from jarvis_knowledge.search import HybridSearchEngine, FuzzySearchEngine
from jarvis_knowledge.ranking import BoostedRankingEngine, RecencyWeightedRankingEngine
from jarvis_knowledge.validation import DeepValidationEngine, BatchValidationEngine
from jarvis_knowledge.citations import TrackedCitationEngine, CrossReferenceEngine
from jarvis_knowledge.summarization import ExtractiveSummarizer, FirstSentenceSummarizer
from jarvis_knowledge.semantic import TfidfSemanticEngine
from jarvis_knowledge.entities import RegexEntityExtractor, CapitalizedPhraseExtractor
from jarvis_knowledge.provenance import DefaultProvenanceTracker, ProvenanceEventType
from jarvis_knowledge.metrics import InMemoryMetricsCollector
from jarvis_knowledge.synchronization import DefaultSyncEngine, SyncStatus
from jarvis_knowledge.taxonomy import KeywordTaxonomyEngine, TaxonomyTree, TaxonomyNode
from jarvis_knowledge.ontology import KeywordOntologyEngine, OntologyStore, OntologyClass, OntologyRelation
from jarvis_knowledge.engine import IntelligencePipeline
from jarvis_knowledge.graph import InMemoryKnowledgeGraph
from jarvis_knowledge.models import KnowledgeRelationshipType


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------


def test_ingestion_manifest_creation() -> None:
    manifest = IngestionManifest(
        manifest_id="m-1",
        source_name="Test Source",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="Hello world",
        owner="user-1",
        workspace="ws-1",
        project="proj-1",
    )
    assert manifest.manifest_id == "m-1"
    assert manifest.raw_content == "Hello world"


def test_ingestion_engine_success() -> None:
    engine = DefaultIngestionEngine()
    manifest = IngestionManifest(
        manifest_id="m-2",
        source_name="Docs",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="# Title\n\nSome content here",
        owner="user-1",
        workspace="ws-1",
        project="proj-1",
    )
    result = engine.ingest(manifest)
    assert result.success
    assert result.manifest_id == "m-2"
    assert result.document is not None
    assert result.errors == ()


def test_ingestion_engine_empty_content() -> None:
    engine = DefaultIngestionEngine()
    manifest = IngestionManifest(
        manifest_id="m-3",
        source_name="Empty",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="   ",
        owner="user-1",
        workspace="ws-1",
        project="proj-1",
    )
    result = engine.ingest(manifest)
    assert not result.success


def test_ingestion_batch() -> None:
    engine = DefaultIngestionEngine()
    m1 = IngestionManifest(
        manifest_id="batch-1",
        source_name="A",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="Doc A",
        owner="u1",
        workspace="ws-1",
        project="proj-1",
    )
    m2 = IngestionManifest(
        manifest_id="batch-2",
        source_name="B",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="Doc B",
        owner="u1",
        workspace="ws-1",
        project="proj-1",
    )
    results = engine.ingest_batch((m1, m2))
    assert len(results) == 2
    assert all(r.success for r in results)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def test_markdown_parser_headings() -> None:
    parser = MarkdownParser()
    content = "# Main Title\n\n## Section 1\n\nParagraph 1\n\n## Section 2\n\nParagraph 2"
    result = parser.parse(content, "doc-1")
    assert "Main Title" in result.headings
    assert "Section 1" in result.headings
    assert "Section 2" in result.headings


def test_markdown_parser_code_blocks() -> None:
    parser = MarkdownParser()
    content = "# Doc\n\n```python\nprint('hello')\n```"
    result = parser.parse(content, "doc-2")
    assert len(result.code_blocks) == 1
    assert "print" in result.code_blocks[0]


def test_plain_text_parser() -> None:
    parser = PlainTextParser()
    content = "Line one\n\nLine two\n\nLine three"
    result = parser.parse(content, "doc-text")
    assert len(result.paragraphs) >= 2


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def test_fixed_size_chunker() -> None:
    chunker = FixedSizeChunker(chunk_size=10, overlap=2)
    text = "Hello world this is a test document for chunking"
    chunks = chunker.chunk(text, "doc-chunk")
    assert len(chunks) >= 2
    for c in chunks:
        assert c.document_id == "doc-chunk"


def test_paragraph_chunker() -> None:
    chunker = ParagraphChunker()
    text = "Para one.\n\nPara two.\n\nPara three."
    chunks = chunker.chunk(text, "doc-para")
    assert len(chunks) == 3


def test_heading_aware_chunker() -> None:
    chunker = HeadingAwareChunker()
    text = "# Title\n\nIntro\n\n## Section 1\n\nContent here"
    chunks = chunker.chunk(text, "doc-h")
    assert len(chunks) >= 1
    headings = [c.heading for c in chunks if c.heading]
    assert "Section 1" in headings


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------


def test_tfidf_embedding() -> None:
    engine = TfidfEmbeddingEngine(max_features=64)
    vec = engine.embed("Hello world test document")
    assert vec.dimension == 64
    assert vec.model == "tfidf"


def test_tfidf_similarity() -> None:
    engine = TfidfEmbeddingEngine(max_features=64)
    a = engine.embed("Python programming language")
    b = engine.embed("Python is a programming language")
    sim = engine.similarity(a, b)
    assert 0.0 <= sim <= 1.0


def test_random_embedding() -> None:
    engine = RandomEmbeddingEngine(dimension=16)
    vec = engine.embed("test")
    assert len(vec.values) == 16
    assert vec.model == "random"


def test_embedding_batch() -> None:
    engine = TfidfEmbeddingEngine(max_features=32)
    vecs = engine.embed_batch(("one", "two", "three"))
    assert len(vecs) == 3


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------


def test_indexing_engine() -> None:
    chunker = FixedSizeChunker(chunk_size=20, overlap=2)
    embedder = TfidfEmbeddingEngine(max_features=32)
    indexer = DefaultIndexingEngine()

    chunks = chunker.chunk("Hello world this is a test", "doc-idx")
    for chunk in chunks:
        vec = embedder.embed(chunk.text)
        entry = indexer.index(chunk, vec)
        assert entry.chunk_id == chunk.chunk_id

    assert len(indexer.search_index) == len(chunks)


def test_index_batch() -> None:
    chunker = FixedSizeChunker(chunk_size=10, overlap=2)
    embedder = TfidfEmbeddingEngine(max_features=16)
    indexer = DefaultIndexingEngine()

    chunks = chunker.chunk("One two three four five six seven eight nine ten", "doc-batch")
    embeddings = embedder.embed_batch(tuple(c.text for c in chunks))
    entries = indexer.index_batch(chunks, embeddings)
    assert len(entries) == len(chunks)


def test_search_index_operations() -> None:
    idx = SearchIndex()
    assert len(idx) == 0
    from jarvis_knowledge.indexing import IndexEntry
    from jarvis_knowledge.embeddings import EmbeddingVector
    entry = IndexEntry(
        document_id="d1",
        chunk_id="c1",
        text="test",
        embedding=EmbeddingVector(values=(0.1, 0.2), dimension=2, model="test"),
    )
    idx.add(entry)
    assert len(idx) == 1
    assert idx.get("c1") is not None
    idx.remove("c1")
    assert len(idx) == 0
    idx.clear()
    assert len(idx) == 0


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------


def test_similarity_retrieval() -> None:
    embedder = TfidfEmbeddingEngine(max_features=32)
    indexer = DefaultIndexingEngine()
    chunker = FixedSizeChunker(chunk_size=20, overlap=2)
    chunks = chunker.chunk("Python is great for data science and machine learning", "doc-ret")
    for c in chunks:
        indexer.index(c, embedder.embed(c.text))

    retriever = SimilarityRetrievalEngine(embedder)
    query_vec = embedder.embed("Python data science")
    results = retriever.retrieve(query_vec, indexer.search_index, top_k=5)
    assert len(results) >= 1


# ---------------------------------------------------------------------------
# Reranking
# ---------------------------------------------------------------------------


def test_pass_through_reranker() -> None:
    reranker = PassThroughReranker()
    from jarvis_knowledge.retrieval import RetrievalResult
    from jarvis_knowledge.indexing import IndexEntry
    from jarvis_knowledge.embeddings import EmbeddingVector
    entry = IndexEntry(
        document_id="d1",
        chunk_id="c1",
        text="test",
        embedding=EmbeddingVector(values=(0.1,), dimension=1, model="t"),
    )
    results = (
        RetrievalResult(entry=entry, score=0.9),
        RetrievalResult(entry=entry, score=0.5),
    )
    reranked = reranker.rerank(results, "query")
    assert len(reranked) == 2


def test_diversity_reranker() -> None:
    reranker = DiversityReranker(similarity_threshold=0.1)
    from jarvis_knowledge.retrieval import RetrievalResult
    from jarvis_knowledge.indexing import IndexEntry
    from jarvis_knowledge.embeddings import EmbeddingVector
    e1 = IndexEntry(
        document_id="d1", chunk_id="c1", text="Python is great",
        embedding=EmbeddingVector(values=(0.1,), dimension=1, model="t"),
    )
    e2 = IndexEntry(
        document_id="d2", chunk_id="c2", text="Rust is fast",
        embedding=EmbeddingVector(values=(0.2,), dimension=1, model="t"),
    )
    results = (
        RetrievalResult(entry=e1, score=0.9),
        RetrievalResult(entry=e2, score=0.8),
    )
    reranked = reranker.rerank(results, "programming")
    assert len(reranked) >= 1


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def test_hybrid_search_ranked() -> None:
    from jarvis_knowledge.models import (
        KnowledgeDocument, KnowledgeSearchQuery, KnowledgeMetadata,
        KnowledgeClassification, KnowledgeImportance, KnowledgeSensitivity,
        KnowledgeVisibility,
    )
    from datetime import UTC, datetime
    cls = KnowledgeClassification(
        domain="d", topic="t", category="c",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language="en", workspace="ws", project="proj",
    )
    meta = KnowledgeMetadata(
        identifier="d1", title="Python Guide", description="Learn Python",
        owner="u", workspace="ws", project="proj",
        classification=cls, tags=frozenset(), language="en",
        version=1, visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8, relationships=(),
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    doc = KnowledgeDocument(
        metadata=meta, summary="Guide to Python programming",
        content_reference="/docs/python.md", source_id="src-1",
    )
    engine = HybridSearchEngine()
    results = engine.search_ranked(
        (doc,),
        KnowledgeSearchQuery(terms=("python",), workspace="ws", project="proj"),
    )
    assert len(results) == 1


def test_fuzzy_search() -> None:
    from jarvis_knowledge.models import (
        KnowledgeDocument, KnowledgeSearchQuery, KnowledgeMetadata,
        KnowledgeClassification, KnowledgeImportance, KnowledgeSensitivity,
        KnowledgeVisibility,
    )
    from datetime import UTC, datetime
    cls = KnowledgeClassification(
        domain="d", topic="t", category="c",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language="en", workspace="ws", project="proj",
    )
    meta = KnowledgeMetadata(
        identifier="d1", title="Machine Learning", description="ML concepts",
        owner="u", workspace="ws", project="proj",
        classification=cls, tags=frozenset(), language="en",
        version=1, visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8, relationships=(),
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    doc = KnowledgeDocument(
        metadata=meta, summary="About machine learning and AI",
        content_reference="/docs/ml.md", source_id="src-1",
    )
    engine = FuzzySearchEngine(threshold=0.1)
    results = engine.search((doc,), KnowledgeSearchQuery(terms=("learning",)))
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def test_boosted_ranking() -> None:
    engine = BoostedRankingEngine()
    from jarvis_knowledge.models import (
        KnowledgeDocument, KnowledgeRankingContext, KnowledgeMetadata,
        KnowledgeClassification, KnowledgeImportance, KnowledgeSensitivity,
        KnowledgeVisibility,
    )
    from datetime import UTC, datetime
    cls = KnowledgeClassification(
        domain="d", topic="t", category="c",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language="en", workspace="ws", project="proj",
    )
    meta = KnowledgeMetadata(
        identifier="d1", title="Python", description="d",
        owner="u", workspace="ws", project="proj",
        classification=cls, tags=frozenset(), language="en",
        version=1, visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8, relationships=(),
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    doc = KnowledgeDocument(
        metadata=meta, summary="Python programming",
        content_reference="/docs/py.md", source_id="src-1",
    )
    context = KnowledgeRankingContext(
        requester_id="u", workspace="ws", project="proj",
    )
    results = engine.rank_with_boosts((doc,), context, boosts={"python": 2.0})
    assert len(results) == 1


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_deep_validation() -> None:
    engine = DeepValidationEngine()
    from jarvis_knowledge.models import (
        KnowledgeDocument, KnowledgeMetadata, KnowledgeClassification,
        KnowledgeImportance, KnowledgeSensitivity, KnowledgeVisibility,
    )
    from datetime import UTC, datetime
    cls = KnowledgeClassification(
        domain="d", topic="t", category="c",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language="en", workspace="ws", project="proj",
    )
    meta = KnowledgeMetadata(
        identifier="d1", title="Test", description="d",
        owner="u", workspace="ws", project="proj",
        classification=cls, tags=frozenset(), language="en",
        version=1, visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8, relationships=(),
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    doc = KnowledgeDocument(
        metadata=meta, summary="Valid summary here",
        content_reference="/docs/t.md", source_id="src-1",
    )
    from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog
    catalog = InMemoryKnowledgeCatalog()
    report = engine.deep_validate(document=doc, catalog=catalog)
    assert report.document_id == "d1"


def test_batch_validation() -> None:
    engine = BatchValidationEngine()
    from jarvis_knowledge.models import (
        KnowledgeDocument, KnowledgeMetadata, KnowledgeClassification,
        KnowledgeImportance, KnowledgeSensitivity, KnowledgeVisibility,
    )
    from datetime import UTC, datetime
    cls = KnowledgeClassification(
        domain="d", topic="t", category="c",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language="en", workspace="ws", project="proj",
    )
    meta = KnowledgeMetadata(
        identifier="d1", title="Test", description="d",
        owner="u", workspace="ws", project="proj",
        classification=cls, tags=frozenset(), language="en",
        version=1, visibility=KnowledgeVisibility.WORKSPACE,
        confidence=0.8, relationships=(),
        created_at=datetime.now(UTC), updated_at=datetime.now(UTC),
    )
    doc = KnowledgeDocument(
        metadata=meta, summary="Summary",
        content_reference="/docs/t.md", source_id="src-1",
    )
    from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog
    catalog = InMemoryKnowledgeCatalog()
    reports = engine.validate_batch((doc,), catalog)
    assert len(reports) == 1


# ---------------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------------


def test_tracked_citation_engine() -> None:
    engine = TrackedCitationEngine()
    from jarvis_knowledge.models import KnowledgeCitationType
    cit = engine.create_citation(
        from_document_id="doc-a",
        to_reference="https://example.com",
        citation_type=KnowledgeCitationType.EXTERNAL,
    )
    assert cit.from_document_id == "doc-a"
    assert engine.count_citations("doc-a") == 1
    assert len(engine.citations_by_type(KnowledgeCitationType.EXTERNAL)) == 1


def test_cross_reference_engine() -> None:
    engine = CrossReferenceEngine()
    from jarvis_knowledge.models import KnowledgeCitationType
    engine.create_citation(
        from_document_id="doc-a",
        to_reference="doc-b",
        citation_type=KnowledgeCitationType.INTERNAL,
    )
    assert engine.backlink_count("doc-b") == 1
    backlinks = engine.backlinks("doc-b")
    assert len(backlinks) == 1


# ---------------------------------------------------------------------------
# Summarization
# ---------------------------------------------------------------------------


def test_extractive_summarizer() -> None:
    engine = ExtractiveSummarizer()
    text = "This is the first sentence. Here is the second one. And the third."
    result = engine.summarize(text, "doc-sum", max_sentences=2)
    assert result.document_id == "doc-sum"
    assert result.sentences == 2


def test_first_sentence_summarizer() -> None:
    engine = FirstSentenceSummarizer()
    text = "First sentence here. Second sentence. Third sentence."
    result = engine.summarize(text, "doc-fs", max_sentences=1)
    assert result.sentences == 1


def test_summarizer_empty() -> None:
    engine = ExtractiveSummarizer()
    result = engine.summarize("", "doc-empty")
    assert result.sentences == 0


# ---------------------------------------------------------------------------
# Semantic
# ---------------------------------------------------------------------------


def test_semantic_analysis() -> None:
    engine = TfidfSemanticEngine()
    text = "Python is a programming language used for data science and machine learning."
    result = engine.analyze(text, "doc-sem")
    assert result.document_id == "doc-sem"
    assert len(result.keywords) > 0
    assert len(result.topics) > 0


# ---------------------------------------------------------------------------
# Entity Extraction
# ---------------------------------------------------------------------------


def test_regex_entity_extractor() -> None:
    extractor = RegexEntityExtractor()
    text = "Contact admin@example.com for version 1.2.3 of the system."
    result = extractor.extract(text, "doc-ent")
    assert len(result.entities) >= 2
    types = {e.entity_type for e in result.entities}
    assert "email" in types or "version" in types


def test_capitalized_phrase_extractor() -> None:
    extractor = CapitalizedPhraseExtractor()
    text = "Alice and Bob worked on the Jarvis Project with Azure Cloud."
    result = extractor.extract(text, "doc-cap")
    assert len(result.entities) >= 1


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_provenance_tracker() -> None:
    tracker = DefaultProvenanceTracker()
    event = tracker.track(
        "doc-1",
        ProvenanceEventType.CREATED,
        "user-1",
        description="Document created",
    )
    assert event.document_id == "doc-1"
    assert event.event_type == "created"
    assert event.actor == "user-1"
    history = tracker.history("doc-1")
    assert len(history) == 1


def test_provenance_multiple_events() -> None:
    tracker = DefaultProvenanceTracker()
    tracker.track("doc-1", ProvenanceEventType.CREATED, "user-1")
    tracker.track("doc-1", ProvenanceEventType.UPDATED, "user-1")
    tracker.track("doc-1", ProvenanceEventType.VALIDATED, "user-2")
    assert len(tracker.history("doc-1")) == 3


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_metrics_collector_record() -> None:
    collector = InMemoryMetricsCollector()
    collector.record("document.count", 5.0)
    collector.record("search.count", 3.0)
    snapshot = collector.snapshot()
    assert snapshot.total_documents == 5
    assert snapshot.total_searches == 3


def test_metrics_collector_snapshot() -> None:
    collector = InMemoryMetricsCollector()
    snapshot = collector.snapshot()
    assert snapshot.total_documents == 0
    assert snapshot.avg_confidence == 0.0


def test_metrics_samples() -> None:
    collector = InMemoryMetricsCollector()
    collector.record("test.metric", 1.0, env="prod")
    samples = collector.samples("test.metric")
    assert len(samples) == 1
    assert samples[0].labels.get("env") == "prod"


# ---------------------------------------------------------------------------
# Synchronization
# ---------------------------------------------------------------------------


def test_sync_engine_success() -> None:
    engine = DefaultSyncEngine()
    result = engine.sync("doc-1", local_version=1, remote_version=2)
    assert result.success
    assert result.new_version == 2


def test_sync_engine_local_ahead() -> None:
    engine = DefaultSyncEngine()
    result = engine.sync("doc-1", local_version=3, remote_version=1)
    assert result.success
    assert result.new_version == 3


def test_sync_engine_no_conflict() -> None:
    engine = DefaultSyncEngine()
    result = engine.sync("doc-1", local_version=2, remote_version=2)
    assert result.success


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------


def test_taxonomy_tree() -> None:
    tree = TaxonomyTree()
    root = TaxonomyNode(node_id="root", name="Root", parent_id=None)
    child = TaxonomyNode(node_id="child", name="Child", parent_id="root")
    tree.add_node(root)
    tree.add_node(child)
    assert tree.get_node("root") is not None
    assert tree.get_node("child") is not None
    children = tree.get_children("root")
    assert len(children) == 1


def test_taxonomy_search() -> None:
    tree = TaxonomyTree()
    tree.add_node(TaxonomyNode(node_id="n1", name="Python", description="Programming language"))
    tree.add_node(TaxonomyNode(node_id="n2", name="Java", description="Another language"))
    results = tree.search("python")
    assert len(results) == 1


def test_keyword_taxonomy_engine() -> None:
    engine = KeywordTaxonomyEngine()
    tree = TaxonomyTree()
    tree.add_node(TaxonomyNode(node_id="root", name="Technology"))
    tree.add_node(TaxonomyNode(node_id="prog", name="Programming", parent_id="root"))
    tree.add_node(TaxonomyNode(node_id="ml", name="Machine Learning", parent_id="root"))
    classifications = engine.classify("I love programming in Python", tree)
    assert len(classifications) >= 1


# ---------------------------------------------------------------------------
# Ontology
# ---------------------------------------------------------------------------


def test_ontology_store() -> None:
    store = OntologyStore()
    cls = OntologyClass(class_id="Person", name="Person", description="A person")
    store.add_class(cls)
    assert store.get_class("Person") is not None


def test_ontology_relations() -> None:
    store = OntologyStore()
    store.add_class(OntologyClass(class_id="Animal", name="Animal"))
    store.add_class(OntologyClass(class_id="Dog", name="Dog", parent_class_id="Animal"))
    engine = KeywordOntologyEngine()
    inferred = engine.infer_relations(store)
    assert len(inferred) >= 1


def test_ontology_mapping() -> None:
    store = OntologyStore()
    store.add_class(OntologyClass(class_id="Python", name="Python"))
    engine = KeywordOntologyEngine()
    mappings = engine.map_document("Python is great", store)
    assert len(mappings) >= 1


# ---------------------------------------------------------------------------
# Graph Enhanced
# ---------------------------------------------------------------------------


def test_graph_reverse_neighbors() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    rev = graph.reverse_neighbors(target_id="b")
    assert len(rev) == 1


def test_graph_degree() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.link(source_id="a", target_id="c", relationship_type=KnowledgeRelationshipType.REFERENCE)
    assert graph.degree("a") == 2


def test_graph_has_path() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.link(source_id="b", target_id="c", relationship_type=KnowledgeRelationshipType.REFERENCE)
    assert graph.has_path("a", "c")
    assert not graph.has_path("a", "z")


def test_graph_shortest_path() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.link(source_id="b", target_id="c", relationship_type=KnowledgeRelationshipType.REFERENCE)
    path = graph.shortest_path("a", "c")
    assert len(path) == 3


def test_graph_all_nodes() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.link(source_id="b", target_id="c", relationship_type=KnowledgeRelationshipType.REFERENCE)
    nodes = graph.all_nodes()
    assert "a" in nodes
    assert "b" in nodes
    assert "c" in nodes


def test_graph_subgraph() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.link(source_id="b", target_id="c", relationship_type=KnowledgeRelationshipType.REFERENCE)
    sub = graph.subgraph(("a", "b"))
    assert sub.degree("a") == 1
    assert sub.degree("b") == 1


def test_graph_clear() -> None:
    graph = InMemoryKnowledgeGraph()
    graph.link(source_id="a", target_id="b", relationship_type=KnowledgeRelationshipType.REFERENCE)
    graph.clear()
    assert len(graph.neighbors(source_id="a")) == 0


# ---------------------------------------------------------------------------
# IntelligencePipeline
# ---------------------------------------------------------------------------


def test_pipeline_ingest_and_index() -> None:
    pipeline = IntelligencePipeline()
    manifest = IngestionManifest(
        manifest_id="pipe-1",
        source_name="Pipeline Test",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="# Test\n\nHello from pipeline",
        owner="user-1",
        workspace="ws-1",
        project="proj-1",
    )
    result = pipeline.ingest_and_index(manifest)
    assert result.success
    assert result.document is not None


def test_pipeline_process_text() -> None:
    pipeline = IntelligencePipeline()
    text = "Python is a programming language. It is used for data science. Machine learning is popular."
    results = pipeline.process_text(text, "doc-proc")
    assert "entities" in results
    assert "summary" in results
    assert "semantic" in results


def test_pipeline_search() -> None:
    pipeline = IntelligencePipeline()
    manifest = IngestionManifest(
        manifest_id="pipe-s",
        source_name="Search Test",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="Python for data science and machine learning",
        owner="user-1",
        workspace="ws-1",
        project="proj-1",
    )
    pipeline.ingest_and_index(manifest)
    results = pipeline.search("Python data science", top_k=5)
    assert len(results) >= 1


def test_pipeline_metrics() -> None:
    pipeline = IntelligencePipeline()
    metrics = pipeline.get_metrics()
    assert metrics.total_documents >= 0


# ---------------------------------------------------------------------------
# Kernel Integration
# ---------------------------------------------------------------------------


def test_kernel_ingest_knowledge() -> None:
    from jarvis_knowledge.kernel import KnowledgeKernel
    kernel = KnowledgeKernel()
    from jarvis_knowledge.models import KnowledgeSource, KnowledgeSourceType
    kernel.register_source(KnowledgeSource(
        source_id="kern-1",
        name="Kernel Source",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        owner="u", workspace="ws", project="proj",
        description="test", quality_score=0.8,
    ))
    manifest = IngestionManifest(
        manifest_id="kern-1",
        source_name="Kernel Test",
        source_type=KnowledgeSourceType.DOCUMENTATION,
        raw_content="# Hello\nWorld",
        owner="u",
        workspace="ws",
        project="proj",
    )
    result = kernel.ingest_knowledge(manifest)
    assert result is not None


def test_kernel_parse_document() -> None:
    from jarvis_knowledge.kernel import KnowledgeKernel
    kernel = KnowledgeKernel()
    result = kernel.parse_document("# Title\n\nContent", "doc-parse")
    assert "Title" in result.headings


def test_kernel_embed_text() -> None:
    from jarvis_knowledge.kernel import KnowledgeKernel
    kernel = KnowledgeKernel()
    vec = kernel.embed_text("Hello")
    assert vec.dimension > 0


def test_kernel_metrics() -> None:
    from jarvis_knowledge.kernel import KnowledgeKernel
    kernel = KnowledgeKernel()
    metrics = kernel.metrics_snapshot()
    assert metrics is not None


def test_kernel_sync() -> None:
    from jarvis_knowledge.kernel import KnowledgeKernel
    kernel = KnowledgeKernel()
    result = kernel.sync_document("doc-1", remote_version=2)
    assert result is not None


def test_kernel_citation_count() -> None:
    from jarvis_knowledge.kernel import KnowledgeKernel
    kernel = KnowledgeKernel()
    count = kernel.citation_counts("doc-1")
    assert count == 0
