# Knowledge Lifecycle

## Stages

```
[Create] -> [Classify] -> [Validate] -> [Register] -> [Use] -> [Update] -> [Archive/Deprecate]
                                                                              |
                                                                              v
                                                                         [Version History]
```

## 1. Registration Flow

```
register_knowledge(document)
    |
    +---> Verify source exists in catalog
    +---> Resolve collections from catalog
    +---> ClassificationEngine.classify(document, source, collections)
    +---> ValidationEngine.validate(document, catalog)
    +---> If invalid -> raise ValueError
    +---> Catalog.register_document(document)
    +---> VersionManager.register_initial(document)
    +---> Graph.link(relationships)
    +---> Return registered document
```

## 2. Update Flow

```
update_knowledge(identifier, summary, content_reference, tags, confidence, ...)
    |
    +---> Retrieve current document from catalog
    +---> Apply updates via document.with_update()
    +---> VersionManager.record_version(document, changed_by, change_summary)
    +---> ValidationEngine.validate(document, catalog)
    +---> If invalid -> raise ValueError
    +---> Catalog.update_document(document)
    +---> Return updated document
```

## 3. Retrieval Flow

```
retrieve_knowledge(identifier, access)
    |
    +---> Get document from catalog
    +---> PolicyEngine.can_access(document, access, policy)
    +---> If denied -> return None
    +---> Return document
```

## 4. Search Flow

```
search_knowledge(query, access)
    |
    +---> List all documents from catalog
    +---> Filter by access permissions
    +---> SearchEngine.search(visible_docs, query)
    +---> RankingEngine.rank(matches, context)
    +---> Return scored results
```

## 5. Classification Flow

```
classify_knowledge(identifier)
    |
    +---> Retrieve document from catalog
    +---> Get source and collections
    +---> ClassificationEngine.classify(document, source, collections)
    +---> Update document with new classification
    +---> Return updated document
```

## 6. Linking Flow

```
link_knowledge(source_identifier, target_identifier, relationship_type)
    |
    +---> Verify both documents exist
    +---> Create KnowledgeRelationship
    +---> Update source document with relationship
    +---> Graph.link(source, target, type)
    +---> Return updated source document
```

## Versioning Strategy

- Versions start at 1
- Each update increments the version number
- Version history is maintained as an ordered sequence
- Compatibility is tracked via compatible_with tuples
- Versions can be marked as deprecated
- Supersedes links track which version replaced which
