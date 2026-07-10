# Extension Guide

## Overview

The Knowledge Platform is designed to be extended through its protocol interfaces. All internal components depend on abstractions, enabling replacement of any engine without modifying the kernel or other components.

## Extension Points

### 1. Custom Classification Engine

Implement `KnowledgeClassificationEngine` protocol:

```python
from jarvis_knowledge.protocols import KnowledgeClassificationEngine
from jarvis_knowledge.models import KnowledgeClassification, KnowledgeDocument, KnowledgeSource, KnowledgeCollection

class MLClassificationEngine:
    def classify(
        self,
        *,
        document: KnowledgeDocument,
        source: KnowledgeSource,
        collections: tuple[KnowledgeCollection, ...],
    ) -> KnowledgeClassification:
        # Use ML model to classify the document
        ...
```

### 2. Custom Validation Engine

Implement `KnowledgeValidationEngine` protocol:

```python
class StrictValidationEngine:
    def validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport:
        # Enforce organization-specific validation rules
        ...
```

### 3. Custom Search Engine

Implement `KnowledgeSearchEngine` protocol:

```python
class FullTextSearchEngine:
    def search(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[KnowledgeDocument, ...]:
        # Use external search index
        ...
```

### 4. Custom Ranking Engine

Implement `KnowledgeRankingEngine` protocol:

```python
class LearningToRankEngine:
    def rank(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]:
        # Use trained ranking model
        ...
```

### 5. Custom Knowledge Graph

Implement `KnowledgeGraph` protocol:

```python
class Neo4jKnowledgeGraph:
    def link(
        self,
        *,
        source_id: str,
        target_id: str,
        relationship_type: KnowledgeRelationshipType,
    ) -> None: ...
    def neighbors(
        self,
        *,
        source_id: str,
        relationship_type: KnowledgeRelationshipType | None = None,
    ) -> tuple[KnowledgeRelationship, ...]: ...
```

### 6. Custom Catalog

Implement `KnowledgeCatalog` protocol:

```python
class PostgresKnowledgeCatalog:
    def register_source(self, source: KnowledgeSource) -> None: ...
    def get_source(self, source_id: str) -> KnowledgeSource | None: ...
    def register_collection(self, collection: KnowledgeCollection) -> None: ...
    def get_collection(self, collection_id: str) -> KnowledgeCollection | None: ...
    def register_document(self, document: KnowledgeDocument) -> None: ...
    def update_document(self, document: KnowledgeDocument) -> None: ...
    def get_document(self, identifier: str) -> KnowledgeDocument | None: ...
    def list_documents(self) -> tuple[KnowledgeDocument, ...]: ...
```

### 7. Custom Citation Engine

Implement `CitationEngine` protocol:

```python
class PersistentCitationEngine:
    def create_citation(
        self, *, from_document_id: str, to_reference: str,
        citation_type: KnowledgeCitationType, metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation: ...
    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]: ...
```

### 8. Custom Version Manager

Implement `KnowledgeVersionManager` protocol:

```python
class DatabaseVersionManager:
    def register_initial(self, document: KnowledgeDocument) -> None: ...
    def record_version(self, *, document: KnowledgeDocument,
        changed_by: str, change_summary: str,
        compatible_with: tuple[int, ...] = (), deprecated: bool = False,
    ) -> KnowledgeDocument: ...
    def current_version(self, document_id: str) -> KnowledgeVersion | None: ...
    def history(self, document_id: str) -> tuple[KnowledgeVersion, ...]: ...
    def is_compatible(self, document_id: str, required_version: int) -> bool: ...
```

### 9. Custom Policy Engine

Implement `KnowledgePolicyEngine` protocol:

```python
class RBACPolicyEngine:
    def register_policy(self, scope: KnowledgePolicyScope, policy: KnowledgePolicy) -> None: ...
    def resolve(self, scope: KnowledgePolicyScope) -> KnowledgePolicy: ...
    def can_access(self, *, document: KnowledgeDocument,
        access: KnowledgeAccessContext, policy: KnowledgePolicy) -> bool: ...
```

## Injection

Inject custom implementations into the KnowledgeKernel:

```python
kernel = KnowledgeKernel(
    catalog=PostgresKnowledgeCatalog(),
    graph=Neo4jKnowledgeGraph(),
    classification_engine=MLClassificationEngine(),
    validation_engine=StrictValidationEngine(),
    search_engine=FullTextSearchEngine(),
    ranking_engine=LearningToRankEngine(),
    citation_engine=PersistentCitationEngine(),
    version_manager=DatabaseVersionManager(),
    policy_engine=RBACPolicyEngine(),
)
```

## Adding New Relationship Types

Extend the `KnowledgeRelationshipType` enum:

```python
from jarvis_knowledge.models import KnowledgeRelationshipType

class CustomRelationshipType(KnowledgeRelationshipType):
    IMPLEMENTS = "implements"
    CONTRADICTS = "contradicts"
    VALIDATES = "validates"
```

## Adding New Source Types

Extend the `KnowledgeSourceType` enum:

```python
from jarvis_knowledge.models import KnowledgeSourceType

class CustomSourceType(KnowledgeSourceType):
    VIDEO = "video"
    PODCAST = "podcast"
    CODE_REPOSITORY = "code_repository"
```

## Architecture Adapters (Future)

The following adapters can be built without modifying the core:

| Adapter        | Technology       | Protocol                |
|----------------|------------------|-------------------------|
| Catalog        | PostgreSQL       | KnowledgeCatalog        |
| Graph          | Neo4j            | KnowledgeGraph          |
| Search         | Elasticsearch    | KnowledgeSearchEngine   |
| Ranking        | Custom ML Model  | KnowledgeRankingEngine  |
| Versioning     | PostgreSQL       | KnowledgeVersionManager |
| Citations      | PostgreSQL       | CitationEngine          |
| Policy         | Open Policy Agent| KnowledgePolicyEngine   |
| Classification | AI/ML Service    | KnowledgeClassificationEngine |
