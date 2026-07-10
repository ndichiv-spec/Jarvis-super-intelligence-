from __future__ import annotations

from dataclasses import replace

from jarvis_knowledge.catalog import InMemoryKnowledgeCatalog
from jarvis_knowledge.engines import (
    DefaultKnowledgeClassificationEngine,
    DefaultKnowledgePolicyEngine,
    DefaultKnowledgeRankingEngine,
    DefaultKnowledgeSearchEngine,
    DefaultKnowledgeValidationEngine,
    InMemoryCitationEngine,
    InMemoryKnowledgeVersionManager,
)
from jarvis_knowledge.graph import InMemoryKnowledgeGraph
from jarvis_knowledge.models import (
    KnowledgeAccessContext,
    KnowledgeCitation,
    KnowledgeCitationType,
    KnowledgeCollection,
    KnowledgeDocument,
    KnowledgePolicy,
    KnowledgePolicyScope,
    KnowledgeRankingContext,
    KnowledgeRelationship,
    KnowledgeRelationshipType,
    KnowledgeSearchQuery,
    KnowledgeSource,
    KnowledgeValidationReport,
    KnowledgeVersion,
    KnowledgeVisibility,
    ScoredKnowledge,
)
from jarvis_knowledge.protocols import (
    CitationEngine,
    KnowledgeCatalog,
    KnowledgeClassificationEngine,
    KnowledgeGraph,
    KnowledgePolicyEngine,
    KnowledgeRankingEngine,
    KnowledgeSearchEngine,
    KnowledgeValidationEngine,
    KnowledgeVersionManager,
)
from jarvis_knowledge.engine import IntelligencePipeline
from jarvis_knowledge.ingestion import IngestionManifest, IngestionEngine, DefaultIngestionEngine
from jarvis_knowledge.parser import DocumentParser, MarkdownParser, ParsedDocument
from jarvis_knowledge.chunking import ChunkingStrategy, FixedSizeChunker, KnowledgeChunk
from jarvis_knowledge.embeddings import EmbeddingEngine, TfidfEmbeddingEngine, EmbeddingVector, DocumentEmbedding
from jarvis_knowledge.indexing import IndexingEngine, DefaultIndexingEngine, SearchIndex, IndexEntry
from jarvis_knowledge.retrieval import RetrievalEngine, SimilarityRetrievalEngine, RetrievalResult
from jarvis_knowledge.reranking import RerankingEngine, PassThroughReranker
from jarvis_knowledge.search import EnhancedSearchEngine, HybridSearchEngine, FuzzySearchEngine
from jarvis_knowledge.ranking import EnhancedRankingEngine, BoostedRankingEngine, RecencyWeightedRankingEngine
from jarvis_knowledge.validation import EnhancedValidationEngine, DeepValidationEngine, BatchValidationEngine
from jarvis_knowledge.citations import EnhancedCitationEngine, TrackedCitationEngine, CrossReferenceEngine
from jarvis_knowledge.summarization import SummarizationEngine, ExtractiveSummarizer, Summary
from jarvis_knowledge.semantic import SemanticEngine, TfidfSemanticEngine, SemanticAnalysis
from jarvis_knowledge.entities import EntityExtractor, RegexEntityExtractor, EntityExtractionResult, Entity
from jarvis_knowledge.provenance import ProvenanceTracker, DefaultProvenanceTracker, ProvenanceEvent
from jarvis_knowledge.metrics import MetricsCollector, InMemoryMetricsCollector, KnowledgeMetrics
from jarvis_knowledge.synchronization import SyncEngine, DefaultSyncEngine, SyncResult
from jarvis_knowledge.taxonomy import TaxonomyEngine, KeywordTaxonomyEngine, TaxonomyTree
from jarvis_knowledge.ontology import OntologyEngine, KeywordOntologyEngine, OntologyStore


class KnowledgeKernel:
    def __init__(
        self,
        *,
        catalog: KnowledgeCatalog | None = None,
        graph: KnowledgeGraph | None = None,
        classification_engine: KnowledgeClassificationEngine | None = None,
        validation_engine: KnowledgeValidationEngine | None = None,
        search_engine: KnowledgeSearchEngine | None = None,
        ranking_engine: KnowledgeRankingEngine | None = None,
        citation_engine: CitationEngine | None = None,
        version_manager: KnowledgeVersionManager | None = None,
        policy_engine: KnowledgePolicyEngine | None = None,
        pipeline: IntelligencePipeline | None = None,
        enhanced_search: EnhancedSearchEngine | None = None,
        enhanced_ranking: EnhancedRankingEngine | None = None,
        enhanced_validation: EnhancedValidationEngine | None = None,
        enhanced_citation: EnhancedCitationEngine | None = None,
        parser: DocumentParser | None = None,
        chunking_strategy: ChunkingStrategy | None = None,
        embedding_engine: EmbeddingEngine | None = None,
        indexing_engine: IndexingEngine | None = None,
        retrieval_engine: RetrievalEngine | None = None,
        reranking_engine: RerankingEngine | None = None,
        summarization_engine: SummarizationEngine | None = None,
        semantic_engine: SemanticEngine | None = None,
        entity_extractor: EntityExtractor | None = None,
        provenance_tracker: ProvenanceTracker | None = None,
        metrics_collector: MetricsCollector | None = None,
        sync_engine: SyncEngine | None = None,
        taxonomy_engine: TaxonomyEngine | None = None,
        ontology_engine: OntologyEngine | None = None,
        ingestion_engine: IngestionEngine | None = None,
    ) -> None:
        self._catalog = catalog or InMemoryKnowledgeCatalog()
        self._graph = graph or InMemoryKnowledgeGraph()
        self._classification_engine = (
            classification_engine or DefaultKnowledgeClassificationEngine()
        )
        self._validation_engine = validation_engine or DefaultKnowledgeValidationEngine()
        self._search_engine = search_engine or DefaultKnowledgeSearchEngine()
        self._ranking_engine = ranking_engine or DefaultKnowledgeRankingEngine()
        self._citation_engine = citation_engine or InMemoryCitationEngine()
        self._version_manager = version_manager or InMemoryKnowledgeVersionManager()
        self._policy_engine = policy_engine or DefaultKnowledgePolicyEngine()
        self._pipeline = pipeline or IntelligencePipeline()
        self._enhanced_search = enhanced_search or HybridSearchEngine()
        self._enhanced_ranking = enhanced_ranking or BoostedRankingEngine()
        self._enhanced_validation = enhanced_validation or DeepValidationEngine()
        self._enhanced_citation = enhanced_citation or TrackedCitationEngine()
        self._parser = parser or MarkdownParser()
        self._chunking_strategy = chunking_strategy or FixedSizeChunker()
        self._embedding_engine = embedding_engine or TfidfEmbeddingEngine()
        self._indexing_engine = indexing_engine or DefaultIndexingEngine()
        self._retrieval_engine = retrieval_engine or SimilarityRetrievalEngine(self._embedding_engine)
        self._reranking_engine = reranking_engine or PassThroughReranker()
        self._summarization_engine = summarization_engine or ExtractiveSummarizer()
        self._semantic_engine = semantic_engine or TfidfSemanticEngine()
        self._entity_extractor = entity_extractor or RegexEntityExtractor()
        self._provenance_tracker = provenance_tracker or DefaultProvenanceTracker()
        self._metrics_collector = metrics_collector or InMemoryMetricsCollector()
        self._sync_engine = sync_engine or DefaultSyncEngine()
        self._taxonomy_engine = taxonomy_engine or KeywordTaxonomyEngine()
        self._ontology_engine = ontology_engine or KeywordOntologyEngine()
        self._ingestion_engine = ingestion_engine or DefaultIngestionEngine()

    def register_source(self, source: KnowledgeSource) -> None:
        self._catalog.register_source(source)

    def register_collection(self, collection: KnowledgeCollection) -> None:
        self._catalog.register_collection(collection)

    def register_policy(self, scope: KnowledgePolicyScope, policy: KnowledgePolicy) -> None:
        self._policy_engine.register_policy(scope, policy)

    def register_knowledge(self, document: KnowledgeDocument) -> KnowledgeDocument:
        source = self._catalog.get_source(document.source_id)
        if source is None:
            msg = f"Knowledge source is not registered: {document.source_id}"
            raise KeyError(msg)

        collections = tuple(
            collection
            for collection_id in document.collection_ids
            if (collection := self._catalog.get_collection(collection_id)) is not None
        )

        classification = self._classification_engine.classify(
            document=document,
            source=source,
            collections=collections,
        )
        prepared = replace(
            document,
            metadata=replace(
                document.metadata,
                classification=classification,
                visibility=classification.visibility,
                tags=frozenset({*document.metadata.tags, *classification.tags}),
            ),
        )

        report = self._validation_engine.validate(document=prepared, catalog=self._catalog)
        if not report.is_valid:
            msg = "; ".join(issue.code for issue in report.issues)
            raise ValueError(f"Knowledge validation failed: {msg}")

        self._catalog.register_document(prepared)
        self._version_manager.register_initial(prepared)
        for relationship in prepared.metadata.relationships:
            self._graph.link(
                source_id=prepared.metadata.identifier,
                target_id=relationship.target_id,
                relationship_type=relationship.relationship_type,
            )
        return prepared

    def retrieve_knowledge(
        self,
        identifier: str,
        *,
        access: KnowledgeAccessContext,
    ) -> KnowledgeDocument | None:
        document = self._catalog.get_document(identifier)
        if document is None:
            return None
        if not self._can_access(document=document, access=access):
            return None
        return document

    def update_knowledge(
        self,
        identifier: str,
        *,
        summary: str | None = None,
        content_reference: str | None = None,
        tags: frozenset[str] | None = None,
        confidence: float | None = None,
        changed_by: str,
        change_summary: str,
    ) -> KnowledgeDocument:
        current = self._catalog.get_document(identifier)
        if current is None:
            msg = f"Knowledge document was not found: {identifier}"
            raise KeyError(msg)

        updated = current.with_update(
            summary=summary,
            content_reference=content_reference,
            tags=tags,
            confidence=confidence,
        )
        versioned = self._version_manager.record_version(
            document=updated,
            changed_by=changed_by,
            change_summary=change_summary,
        )
        report = self._validation_engine.validate(document=versioned, catalog=self._catalog)
        if not report.is_valid:
            msg = "; ".join(issue.code for issue in report.issues)
            raise ValueError(f"Knowledge validation failed: {msg}")
        self._catalog.update_document(versioned)
        return versioned

    def classify_knowledge(self, identifier: str) -> KnowledgeDocument:
        document = self._catalog.get_document(identifier)
        if document is None:
            msg = f"Knowledge document was not found: {identifier}"
            raise KeyError(msg)
        source = self._catalog.get_source(document.source_id)
        if source is None:
            msg = f"Knowledge source is not registered: {document.source_id}"
            raise KeyError(msg)

        collections = tuple(
            collection
            for collection_id in document.collection_ids
            if (collection := self._catalog.get_collection(collection_id)) is not None
        )
        classification = self._classification_engine.classify(
            document=document,
            source=source,
            collections=collections,
        )
        updated = replace(
            document,
            metadata=replace(
                document.metadata,
                classification=classification,
                visibility=classification.visibility,
            ),
        )
        self._catalog.update_document(updated)
        return updated

    def validate_knowledge(self, identifier: str) -> KnowledgeValidationReport:
        document = self._catalog.get_document(identifier)
        if document is None:
            msg = f"Knowledge document was not found: {identifier}"
            raise KeyError(msg)
        return self._validation_engine.validate(document=document, catalog=self._catalog)

    def link_knowledge(
        self,
        *,
        source_identifier: str,
        target_identifier: str,
        relationship_type: KnowledgeRelationshipType,
    ) -> KnowledgeDocument:
        source_document = self._catalog.get_document(source_identifier)
        if source_document is None:
            msg = f"Knowledge document was not found: {source_identifier}"
            raise KeyError(msg)
        if self._catalog.get_document(target_identifier) is None:
            msg = f"Knowledge relationship target was not found: {target_identifier}"
            raise KeyError(msg)

        relationship = KnowledgeRelationship(
            target_id=target_identifier,
            relationship_type=relationship_type,
        )
        linked = source_document.with_relationship(relationship)
        self._catalog.update_document(linked)
        self._graph.link(
            source_id=source_identifier,
            target_id=target_identifier,
            relationship_type=relationship_type,
        )
        return linked

    def search_knowledge(
        self,
        query: KnowledgeSearchQuery,
        *,
        access: KnowledgeAccessContext,
    ) -> tuple[ScoredKnowledge, ...]:
        visible_documents = tuple(
            document
            for document in self._catalog.list_documents()
            if self._can_access(document=document, access=access)
        )
        matches = self._search_engine.search(visible_documents, query)
        context = KnowledgeRankingContext(
            requester_id=access.requester_id,
            workspace=access.workspace,
            project=access.project,
            query_terms=query.terms,
        )
        return self._ranking_engine.rank(matches, context)

    def rank_knowledge(
        self,
        documents: tuple[KnowledgeDocument, ...],
        *,
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]:
        return self._ranking_engine.rank(documents, context)

    def neighbors(
        self,
        source_identifier: str,
        *,
        relationship_type: KnowledgeRelationshipType | None = None,
    ) -> tuple[KnowledgeRelationship, ...]:
        return self._graph.neighbors(
            source_id=source_identifier,
            relationship_type=relationship_type,
        )

    def create_citation(
        self,
        *,
        from_document_id: str,
        to_reference: str,
        citation_type: KnowledgeCitationType,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation:
        if self._catalog.get_document(from_document_id) is None:
            msg = f"Knowledge document was not found: {from_document_id}"
            raise KeyError(msg)
        citation = self._citation_engine.create_citation(
            from_document_id=from_document_id,
            to_reference=to_reference,
            citation_type=citation_type,
            metadata=metadata,
        )
        if self._catalog.get_document(to_reference) is not None:
            linked = self.link_knowledge(
                source_identifier=from_document_id,
                target_identifier=to_reference,
                relationship_type=KnowledgeRelationshipType.CITATION,
            )
            self._catalog.update_document(linked)
        return citation

    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]:
        return self._citation_engine.list_citations(document_id)

    def version_history(self, document_id: str) -> tuple[KnowledgeVersion, ...]:
        return self._version_manager.history(document_id)

    def is_version_compatible(self, document_id: str, required_version: int) -> bool:
        return self._version_manager.is_compatible(document_id, required_version)

    def ingest_knowledge(self, manifest: IngestionManifest) -> KnowledgeDocument | None:
        result = self._ingestion_engine.ingest(manifest)
        self._metrics_collector.record("document.count", 1.0)
        if result.success:
            try:
                registered = self.register_knowledge(result.document)
                self._provenance_tracker.track(
                    document_id=registered.metadata.identifier,
                    event_type="imported",
                    actor=manifest.owner,
                    description=f"Ingested from {manifest.source_name}",
                )
                return registered
            except (KeyError, ValueError):
                return None
        return None

    def parse_document(self, content: str, identifier: str) -> ParsedDocument:
        return self._parser.parse(content, identifier)

    def chunk_document(self, text: str, document_id: str) -> tuple[KnowledgeChunk, ...]:
        return self._chunking_strategy.chunk(text, document_id)

    def embed_text(self, text: str) -> EmbeddingVector:
        return self._embedding_engine.embed(text)

    def index_chunk(self, chunk: KnowledgeChunk, embedding: EmbeddingVector) -> IndexEntry:
        self._metrics_collector.record("chunk.count", 1.0)
        return self._indexing_engine.index(chunk, embedding)

    def search_semantic(self, query_text: str, *, top_k: int = 10) -> tuple[RetrievalResult, ...]:
        self._metrics_collector.record("search.count", 1.0)
        query_vector = self._embedding_engine.embed(query_text)
        results = self._retrieval_engine.retrieve(query_vector, self._indexing_engine.search_index, top_k=top_k)
        results = self._reranking_engine.rerank(results, query_text, top_k=top_k)
        return results

    def search_enhanced(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[ScoredKnowledge, ...]:
        return self._enhanced_search.search_ranked(documents, query)

    def rank_enhanced(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
        *,
        boosts: dict[str, float] | None = None,
    ) -> tuple[ScoredKnowledge, ...]:
        return self._enhanced_ranking.rank_with_boosts(documents, context, boosts=boosts)

    def validate_deep(self, identifier: str) -> KnowledgeValidationReport:
        document = self._catalog.get_document(identifier)
        if document is None:
            msg = f"Knowledge document was not found: {identifier}"
            raise KeyError(msg)
        return self._enhanced_validation.deep_validate(document=document, catalog=self._catalog)

    def summarize_document(self, identifier: str, *, max_sentences: int = 5) -> Summary | None:
        document = self._catalog.get_document(identifier)
        if document is None:
            return None
        return self._summarization_engine.summarize(
            f"{document.metadata.title}. {document.summary}",
            identifier,
            max_sentences=max_sentences,
        )

    def analyze_semantics(self, identifier: str) -> SemanticAnalysis | None:
        document = self._catalog.get_document(identifier)
        if document is None:
            return None
        text = f"{document.metadata.title}. {document.summary} {document.metadata.description}"
        return self._semantic_engine.analyze(text, identifier)

    def extract_entities(self, identifier: str) -> EntityExtractionResult | None:
        document = self._catalog.get_document(identifier)
        if document is None:
            return None
        text = f"{document.metadata.title}. {document.summary} {document.metadata.description}"
        return self._entity_extractor.extract(text, identifier)

    def track_provenance(
        self,
        identifier: str,
        event_type: str,
        actor: str,
        *,
        description: str = "",
    ) -> ProvenanceEvent | None:
        if self._catalog.get_document(identifier) is None:
            return None
        return self._provenance_tracker.track(
            document_id=identifier,
            event_type=event_type,
            actor=actor,
            description=description,
        )

    def provenance_history(self, identifier: str) -> tuple[ProvenanceEvent, ...]:
        return self._provenance_tracker.history(identifier)

    def metrics_snapshot(self) -> KnowledgeMetrics:
        return self._metrics_collector.snapshot()

    def sync_document(self, identifier: str, remote_version: int) -> SyncResult:
        document = self._catalog.get_document(identifier)
        local_version = document.metadata.version if document else 0
        return self._sync_engine.sync(identifier, local_version, remote_version)

    def pipeline(self) -> IntelligencePipeline:
        return self._pipeline

    def knowledge_graph_all_nodes(self) -> tuple[str, ...]:
        return self._graph.all_nodes()

    def knowledge_graph_path(self, source_id: str, target_id: str) -> tuple[str, ...]:
        return self._graph.shortest_path(source_id, target_id)

    def citation_counts(self, document_id: str) -> int:
        return self._enhanced_citation.count_citations(document_id)

    def _can_access(self, *, document: KnowledgeDocument, access: KnowledgeAccessContext) -> bool:
        scope = KnowledgePolicyScope(
            owner=document.metadata.owner,
            workspace=document.metadata.workspace,
            project=document.metadata.project,
            is_enterprise=document.metadata.visibility == KnowledgeVisibility.ENTERPRISE,
        )
        policy = self._policy_engine.resolve(scope)
        return self._policy_engine.can_access(document=document, access=access, policy=policy)
