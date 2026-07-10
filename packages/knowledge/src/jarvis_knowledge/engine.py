from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from jarvis_knowledge.ingestion import (
    DefaultIngestionEngine,
    IngestionEngine,
    IngestionManifest,
    IngestionResult,
)
from jarvis_knowledge.parser import (
    DocumentParser,
    MarkdownParser,
    ParsedDocument,
)
from jarvis_knowledge.chunking import (
    ChunkingStrategy,
    FixedSizeChunker,
    KnowledgeChunk,
)
from jarvis_knowledge.embeddings import (
    DocumentEmbedding,
    EmbeddingEngine,
    EmbeddingVector,
    TfidfEmbeddingEngine,
)
from jarvis_knowledge.indexing import (
    DefaultIndexingEngine,
    IndexEntry,
    IndexingEngine,
    SearchIndex,
)
from jarvis_knowledge.retrieval import (
    RetrievalEngine,
    RetrievalResult,
    SimilarityRetrievalEngine,
)
from jarvis_knowledge.reranking import (
    PassThroughReranker,
    RerankingEngine,
)
from jarvis_knowledge.summarization import (
    ExtractiveSummarizer,
    SummarizationEngine,
    Summary,
)
from jarvis_knowledge.semantic import (
    SemanticAnalysis,
    SemanticEngine,
    TfidfSemanticEngine,
)
from jarvis_knowledge.entities import (
    Entity,
    EntityExtractionResult,
    EntityExtractor,
    RegexEntityExtractor,
)
from jarvis_knowledge.provenance import (
    DefaultProvenanceTracker,
    ProvenanceEvent,
    ProvenanceTracker,
)
from jarvis_knowledge.metrics import (
    InMemoryMetricsCollector,
    KnowledgeMetrics,
    MetricsCollector,
)
from jarvis_knowledge.validation import (
    DeepValidationEngine,
    EnhancedValidationEngine,
)
from jarvis_knowledge.citations import (
    EnhancedCitationEngine,
    TrackedCitationEngine,
)
from jarvis_knowledge.synchronization import (
    DefaultSyncEngine,
    SyncEngine,
    SyncResult,
)
from jarvis_knowledge.taxonomy import (
    KeywordTaxonomyEngine,
    TaxonomyEngine,
    TaxonomyTree,
)
from jarvis_knowledge.ontology import (
    KeywordOntologyEngine,
    OntologyEngine,
    OntologyStore,
)


@dataclass(slots=True)
class IntelligencePipeline:
    ingestion_engine: IngestionEngine = field(default_factory=DefaultIngestionEngine)
    parser: DocumentParser = field(default_factory=MarkdownParser)
    chunking_strategy: ChunkingStrategy = field(default_factory=FixedSizeChunker)
    embedding_engine: EmbeddingEngine = field(default_factory=TfidfEmbeddingEngine)
    indexing_engine: IndexingEngine = field(default_factory=DefaultIndexingEngine)
    retrieval_engine: RetrievalEngine | None = None
    reranking_engine: RerankingEngine = field(default_factory=PassThroughReranker)
    summarization_engine: SummarizationEngine = field(default_factory=ExtractiveSummarizer)
    semantic_engine: SemanticEngine = field(default_factory=TfidfSemanticEngine)
    entity_extractor: EntityExtractor = field(default_factory=RegexEntityExtractor)
    provenance_tracker: ProvenanceTracker = field(default_factory=DefaultProvenanceTracker)
    metrics_collector: MetricsCollector = field(default_factory=InMemoryMetricsCollector)
    validation_engine: EnhancedValidationEngine = field(default_factory=DeepValidationEngine)
    citation_engine: EnhancedCitationEngine = field(default_factory=TrackedCitationEngine)
    sync_engine: SyncEngine = field(default_factory=DefaultSyncEngine)
    taxonomy_engine: TaxonomyEngine = field(default_factory=KeywordTaxonomyEngine)
    ontology_engine: OntologyEngine = field(default_factory=KeywordOntologyEngine)

    def __post_init__(self) -> None:
        if self.retrieval_engine is None:
            object.__setattr__(self, "retrieval_engine", SimilarityRetrievalEngine(self.embedding_engine))

    def ingest_and_index(self, manifest: IngestionManifest) -> IngestionResult:
        result = self.ingestion_engine.ingest(manifest)
        self.metrics_collector.record("document.count", 1.0)
        if result.success:
            parsed = self.parser.parse(manifest.raw_content, result.document.metadata.identifier)
            chunks = self.chunking_strategy.chunk(parsed.text, result.document.metadata.identifier)
            self.metrics_collector.record("chunk.count", float(len(chunks)))
            for chunk in chunks:
                vector = self.embedding_engine.embed(chunk.text)
                self.indexing_engine.index(chunk, vector)
            self.provenance_tracker.track(
                document_id=result.document.metadata.identifier,
                event_type="imported",
                actor=manifest.owner,
                description=f"Ingested from {manifest.source_name}",
            )
        return result

    def process_text(
        self,
        text: str,
        document_id: str,
        *,
        extract_entities: bool = True,
        summarize: bool = True,
        analyze_semantics: bool = True,
    ) -> dict:
        results: dict = {}
        if extract_entities:
            entity_result = self.entity_extractor.extract(text, document_id)
            results["entities"] = entity_result
            self.metrics_collector.record("entity.count", float(len(entity_result.entities)))
        if summarize:
            summary = self.summarization_engine.summarize(text, document_id)
            results["summary"] = summary
        if analyze_semantics:
            analysis = self.semantic_engine.analyze(text, document_id)
            results["semantic"] = analysis
        return results

    def search(
        self,
        query_text: str,
        *,
        top_k: int = 10,
        rerank: bool = True,
    ) -> tuple[RetrievalResult, ...]:
        self.metrics_collector.record("search.count", 1.0)
        query_vector = self.embedding_engine.embed(query_text)
        results = self.retrieval_engine.retrieve(query_vector, self.indexing_engine.search_index, top_k=top_k)
        if rerank and results:
            results = self.reranking_engine.rerank(results, query_text, top_k=top_k)
        return results

    def get_metrics(self) -> KnowledgeMetrics:
        return self.metrics_collector.snapshot()
