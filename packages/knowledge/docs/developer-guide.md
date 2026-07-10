# Developer Guide

## Getting Started

The Knowledge Platform is a dependency-free Python package.

### Installation

```bash
cd packages/knowledge
pip install -e .
```

### Running Tests

```bash
# From workspace root
pytest packages/knowledge/tests/ -v

# With coverage
pytest packages/knowledge/tests/ --cov=jarvis_knowledge -v
```

### Type Checking

```bash
mypy -p jarvis_knowledge
```

### Linting

```bash
ruff check src/jarvis_knowledge/
```

## Package Structure

```
packages/knowledge/
    pyproject.toml
    src/
        jarvis_knowledge/
            __init__.py         # Public API
            models.py           # Domain dataclasses
            protocols.py        # Protocol interfaces
            catalog.py          # In-memory catalog
            engines.py          # Engine implementations
            graph.py            # In-memory graph
            kernel.py           # Central coordinator
            py.typed            # PEP 561 marker
    tests/
        test_knowledge_platform.py  # Comprehensive tests
    docs/
        architecture.md
        taxonomy.md
        lifecycle.md
        entity-relationships.md
        classification-model.md
        versioning-strategy.md
        developer-guide.md
        extension-guide.md
```

## Using the KnowledgeKernel

### Basic Usage

```python
from jarvis_knowledge import (
    KnowledgeKernel,
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeCollection,
    KnowledgeDocument,
    KnowledgeMetadata,
    KnowledgeClassification,
    KnowledgeVisibility,
    KnowledgeAccessContext,
    default_classification,
)

kernel = KnowledgeKernel()

# Register a source
source = KnowledgeSource(
    source_id="docs-1",
    name="Technical Documentation",
    source_type=KnowledgeSourceType.DOCUMENTATION,
    owner="user-1",
    workspace="ws-1",
    project="proj-1",
    description="Project technical docs",
    quality_score=0.9,
)
kernel.register_source(source)

# Register a collection
collection = KnowledgeCollection(
    collection_id="backend",
    name="Backend",
    domain="engineering",
    owner="user-1",
    workspace="ws-1",
    project="proj-1",
)
kernel.register_collection(collection)

# Create a document
classification = default_classification(
    workspace="ws-1", project="proj-1", language="en"
)
metadata = KnowledgeMetadata(
    identifier="doc-1",
    title="API Design Guide",
    description="Best practices for API design",
    owner="user-1",
    workspace="ws-1",
    project="proj-1",
    classification=classification,
    tags=frozenset({"api", "design"}),
    language="en",
    version=1,
    visibility=KnowledgeVisibility.WORKSPACE,
    confidence=0.8,
    relationships=(),
    created_at=...,
    updated_at=...,
)
document = KnowledgeDocument(
    metadata=metadata,
    summary="Guidelines for REST API design",
    content_reference="/docs/api-design.md",
    source_id="docs-1",
    collection_ids=("backend",),
)

# Register the knowledge
registered = kernel.register_knowledge(document)

# Retrieve knowledge
doc = kernel.retrieve_knowledge(
    "doc-1",
    access=KnowledgeAccessContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
    ),
)

# Search knowledge
results = kernel.search_knowledge(
    KnowledgeSearchQuery(
        workspace="ws-1",
        project="proj-1",
        tags=frozenset({"api"}),
    ),
    access=KnowledgeAccessContext(
        requester_id="user-1",
        workspace="ws-1",
        project="proj-1",
    ),
)
```

## Important Design Rules

1. **Never import infrastructure**: The package must not import PostgreSQL, Redis, Qdrant, FastAPI, SQLAlchemy
2. **Never store implementations**: The kernel delegates to protocols
3. **Models are frozen**: All dataclasses use `frozen=True` and `slots=True`
4. **No placeholder implementations**: All engines have working default implementations
5. **Access control is logical**: Real auth belongs in the Security subsystem
6. **Framework independence**: No framework dependencies allowed
