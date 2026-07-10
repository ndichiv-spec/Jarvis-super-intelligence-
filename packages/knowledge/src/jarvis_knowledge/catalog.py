from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_knowledge.models import KnowledgeCollection, KnowledgeDocument, KnowledgeSource


@dataclass(slots=True)
class InMemoryKnowledgeCatalog:
    _sources: dict[str, KnowledgeSource] = field(default_factory=dict)
    _collections: dict[str, KnowledgeCollection] = field(default_factory=dict)
    _documents: dict[str, KnowledgeDocument] = field(default_factory=dict)

    def register_source(self, source: KnowledgeSource) -> None:
        self._sources[source.source_id] = source

    def get_source(self, source_id: str) -> KnowledgeSource | None:
        return self._sources.get(source_id)

    def register_collection(self, collection: KnowledgeCollection) -> None:
        self._collections[collection.collection_id] = collection

    def get_collection(self, collection_id: str) -> KnowledgeCollection | None:
        return self._collections.get(collection_id)

    def register_document(self, document: KnowledgeDocument) -> None:
        self._documents[document.metadata.identifier] = document

    def update_document(self, document: KnowledgeDocument) -> None:
        if document.metadata.identifier not in self._documents:
            msg = f"Knowledge document is not registered: {document.metadata.identifier}"
            raise KeyError(msg)
        self._documents[document.metadata.identifier] = document

    def get_document(self, identifier: str) -> KnowledgeDocument | None:
        return self._documents.get(identifier)

    def list_documents(self) -> tuple[KnowledgeDocument, ...]:
        return tuple(self._documents.values())
