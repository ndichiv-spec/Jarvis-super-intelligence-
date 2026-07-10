# Entity Relationship Diagram

## Core Entities

```
+------------------+       +------------------+       +-------------------+
| KnowledgeSource  |       | KnowledgeDocument|       | KnowledgeCollection|
+------------------+       +------------------+       +-------------------+
| source_id (PK)   |<------| source_id (FK)   |       | collection_id (PK)|
| name             |       | metadata         |       | name              |
| source_type      |       | summary          |       | domain            |
| owner            |       | content_reference|       | owner             |
| workspace        |       | collection_ids   |       | workspace         |
| project          |       | attributes       |       | project           |
| description      |       +------------------+       | visibility        |
| quality_score    |            |      |              +-------------------+
| uri              |            |      |                    |
+------------------+            |      +--------------------+
                                |                 (many-to-many)
                                v
                     +---------------------+
                     | KnowledgeMetadata   |
                     +---------------------+
                     | identifier (PK)     |
                     | title               |
                     | description         |
                     | owner               |
                     | workspace           |
                     | project             |
                     | classification      |
                     | tags                |
                     | language            |
                     | version             |
                     | visibility          |
                     | confidence          |
                     | relationships       |
                     | created_at          |
                     | updated_at          |
                     +---------------------+
```

## Relationships

```
+---------------------+       +------------------------+
| KnowledgeDocument   |------>| KnowledgeRelationship  |
| (source)            |       +------------------------+
+---------------------+       | target_id              |
                              | relationship_type      |
                              | metadata               |
                              | created_at             |
                              +------------------------+
                                     |
                                     v
                              +---------------------+
                              | KnowledgeDocument   |
                              | (target)            |
                              +---------------------+
```

## Versioning

```
+---------------------+       +---------------------+
| KnowledgeDocument   |<------| KnowledgeVersion    |
+---------------------+       +---------------------+
| version (current)   |       | version_id (PK)     |
                              | document_id (FK)    |
                              | number              |
                              | changed_by          |
                              | change_summary      |
                              | changed_at          |
                              | compatible_with     |
                              | deprecated          |
                              | supersedes_version  |
                              +---------------------+
```

## Citations

```
+---------------------+       +---------------------+
| KnowledgeDocument   |<------| KnowledgeCitation   |
| (from_document)     |       +---------------------+
+---------------------+       | citation_id (PK)    |
                              | from_document_id(FK)|
                              | to_reference        |
                              | citation_type       |
                              | metadata            |
                              | created_at          |
                              +---------------------+
```

## Graph

```
+---------------------+       +---------------------+
| KnowledgeDocument   |------>| KnowledgeGraph      |
| (node)              |       | (adjacency list)    |
+---------------------+       +---------------------+
                              | source_id ->        |
                              |   (target_id,       |
                              |    relationship_type)|
                              +---------------------+
```

## Policy

```
+---------------------+       +---------------------+
| KnowledgePolicy     |       | KnowledgePolicyScope|
+---------------------+       +---------------------+
| policy_id (PK)      |       | owner               |
| name                |       | workspace           |
| retention_days      |       | project             |
| allowed_visibility  |       | is_enterprise       |
| workspace_isolation |       +---------------------+
| enterprise_govern   |                |
| enforce_project_own |                |
| compliance_tags     |                v
+---------------------+       +---------------------+
                              | KnowledgeAccessContext|
                              +---------------------+
                              | requester_id        |
                              | workspace           |
                              | project             |
                              +---------------------+
```

## Validation

```
+---------------------+
| KnowledgeValidation |
| Report              |
+---------------------+
| document_id         |
| is_valid            |
| completeness        |
| consistency         |
| integrity           |
| source_quality      |
| version_validity    |
| relationship_int    |
| issues[]            |
+---------------------+
        |
        v
+---------------------+
| KnowledgeValidation |
| Issue               |
+---------------------+
| code                |
| message             |
| severity            |
+---------------------+
```
