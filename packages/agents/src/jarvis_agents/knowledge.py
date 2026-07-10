from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InMemoryKnowledgeInterface:
    _documents: dict[str, str] = field(default_factory=dict)
    _search_index: dict[str, list[str]] = field(default_factory=dict)

    def add_document(self, document_id: str, content: str, workspace: str = "*") -> None:
        self._documents[document_id] = content
        for token in content.lower().split():
            if token not in self._search_index:
                self._search_index[token] = []
            self._search_index[token].append(document_id)

    def query(self, agent_id: str, query: str) -> tuple[str, ...]:
        _ = agent_id
        tokens = query.lower().split()
        matched: set[str] = set()
        for token in tokens:
            for doc_id in self._search_index.get(token, []):
                matched.add(f"{doc_id}: {self._documents.get(doc_id, '')[:100]}")
        return tuple(sorted(matched))

    def get_document(self, agent_id: str, document_id: str) -> str | None:
        _ = agent_id
        return self._documents.get(document_id)

    def search(self, agent_id: str, query: str, workspace: str) -> tuple[str, ...]:
        _ = (agent_id, workspace)
        return self.query("", query)
