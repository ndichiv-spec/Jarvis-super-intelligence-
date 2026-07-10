### Relationship Model

- Supported relationship types:
  - Parent
  - Child
  - Reference
  - Conversation
  - Project
  - Workflow
  - Semantic
  - Temporal
  - Dependency
  - Association

### Model Rules

- Relationships are explicit edges stored in `MemoryMetadata.relationships`.
- Relationship updates are immutable through `MemoryKernel.add_relationship`.
- Relationship-aware retrieval is available through `RetrievalQuery.relationship_type`.
