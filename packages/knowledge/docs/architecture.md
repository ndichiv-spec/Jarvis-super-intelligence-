# Knowledge Architecture

## Overview

The Knowledge Platform is a permanent subsystem of the JARVIS AI Ecosystem responsible for acquiring, organizing, indexing, classifying, validating, searching, and reasoning over knowledge. It is independent from the Memory Engine: Memory stores experiences, Knowledge stores information.

## Design Principles

- **Domain-Driven Design**: Models are aligned with the knowledge domain
- **Clean Architecture**: Dependency inversion ensures framework independence
- **Protocol-based**: All engines are defined as Python Protocols
- **No infrastructure coupling**: No dependency on PostgreSQL, Redis, Qdrant, FastAPI, SQLAlchemy, HTTP, or any external service
- **Immutable models**: All knowledge data models are frozen dataclasses

## Architecture Diagram

```
                    +-------------------+
                    |  KnowledgeKernel  |
                    +--------+----------+
                             |
            +----------------+----------------+
            |                |                |
            v                v                v
    +-------+-------+  +----+--------+  +----+--------+
    |  Knowledge    |  |  Engines    |  |  Knowledge  |
    |  Catalog      |  | (Classify,  |  |  Graph      |
    |               |  |  Validate,  |  |             |
    |               |  |  Search,    |  |             |
    |               |  |  Rank,      |  |             |
    |               |  |  Cite,      |  |             |
    |               |  |  Version,   |  |             |
    |               |  |  Policy)    |  |             |
    +---------------+  +-------------+  +-------------+
```

## Layer Structure

```
jarvis_knowledge/
    __init__.py      # Public API exports
    models.py        # Domain dataclasses
    protocols.py     # Protocol interfaces
    catalog.py       # In-memory catalog implementation
    engines.py       # Default engine implementations
    graph.py         # In-memory knowledge graph
    kernel.py        # Central coordinator
    py.typed         # PEP 561 marker
```

## Component Relationships

The KnowledgeKernel orchestrates all operations by delegating to:

1. **KnowledgeCatalog** — manages sources, collections, and documents
2. **KnowledgeClassificationEngine** — assigns domain, topic, category, tags
3. **KnowledgeValidationEngine** — evaluates completeness, consistency, integrity
4. **KnowledgeSearchEngine** — filters documents by query criteria
5. **KnowledgeRankingEngine** — scores and orders results
6. **KnowledgeGraph** — manages entity relationships
7. **CitationEngine** — manages internal/external references
8. **KnowledgeVersionManager** — tracks document versions
9. **KnowledgePolicyEngine** — enforces access and governance rules

## Dependency Inversion

All components depend on abstractions (Protocols), not concrete implementations. The KnowledgeKernel accepts any implementation fulfilling the protocol contract, enabling future infrastructure adapters.

```python
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
    ) -> None: ...
```
