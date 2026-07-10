# Classification Model

## Default Classification Engine

The `DefaultKnowledgeClassificationEngine` implements a simple classification strategy:

### Algorithm

1. **Primary Collection**: If the document belongs to any collection, the first collection in `collection_ids` is used as the primary collection.
2. **Domain**: Set to the primary collection's domain, if available; otherwise falls back to the document's existing classification domain.
3. **Category**: Set to the primary collection's name, if available; otherwise falls back to the document's existing classification category.
4. **Workspace/Project**: Overridden from document metadata.
5. **Tags**: Merged from document tags, classification tags, and the source type value.

### Pseudocode

```
classify(document, source, collections):
    base = document.classification
    primary = collections.first()
    domain = primary.domain if primary else base.domain
    category = primary.name if primary else base.category
    tags = merge(document.tags, base.tags, source.type.value)
    return base.with_overrides(
        domain=domain,
        category=category,
        workspace=document.workspace,
        project=document.project,
        tags=tags,
    )
```

### Override Behavior

`with_overrides()` returns a new `KnowledgeClassification` with specified fields replaced:

```python
def with_overrides(
    self,
    *,
    domain: str | None = None,
    topic: str | None = None,
    category: str | None = None,
    workspace: str | None = None,
    project: str | None = None,
    tags: frozenset[str] | None = None,
) -> KnowledgeClassification
```

Fields set to `None` (default) retain their original values. Only explicitly provided fields are overridden.

### Default Classification Helper

The `default_classification()` function creates a baseline classification:

```python
def default_classification(
    *,
    workspace: str,
    project: str,
    language: str,
) -> KnowledgeClassification:
    return KnowledgeClassification(
        domain="general",
        topic="general",
        category="general",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language=language,
        workspace=workspace,
        project=project,
    )
```

## Extending Classification

To implement custom classification strategies, implement the `KnowledgeClassificationEngine` protocol:

```python
class KnowledgeClassificationEngine(Protocol):
    def classify(
        self,
        *,
        document: KnowledgeDocument,
        source: KnowledgeSource,
        collections: tuple[KnowledgeCollection, ...],
    ) -> KnowledgeClassification: ...
```
