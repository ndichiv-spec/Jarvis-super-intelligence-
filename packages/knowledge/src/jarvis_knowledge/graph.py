from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from jarvis_knowledge.models import KnowledgeRelationship, KnowledgeRelationshipType


@dataclass(slots=True)
class InMemoryKnowledgeGraph:
    _adjacency: dict[str, tuple[KnowledgeRelationship, ...]] = field(default_factory=dict)
    _reverse_index: dict[str, tuple[KnowledgeRelationship, ...]] = field(default_factory=dict)

    def link(
        self,
        *,
        source_id: str,
        target_id: str,
        relationship_type: KnowledgeRelationshipType,
    ) -> None:
        relationship = KnowledgeRelationship(
            target_id=target_id,
            relationship_type=relationship_type,
        )
        existing = self._adjacency.get(source_id, ())
        if any(
            rel.target_id == target_id and rel.relationship_type == relationship_type
            for rel in existing
        ):
            return
        self._adjacency[source_id] = (*existing, relationship)
        rev_existing = self._reverse_index.get(target_id, ())
        rev_rel = KnowledgeRelationship(
            target_id=source_id,
            relationship_type=relationship_type,
            metadata={"reverse": "true"},
        )
        if not any(
            rel.target_id == source_id and rel.relationship_type == relationship_type
            for rel in rev_existing
        ):
            self._reverse_index[target_id] = (*rev_existing, rev_rel)

    def neighbors(
        self,
        *,
        source_id: str,
        relationship_type: KnowledgeRelationshipType | None = None,
    ) -> tuple[KnowledgeRelationship, ...]:
        relationships = self._adjacency.get(source_id, ())
        if relationship_type is None:
            return relationships
        return tuple(
            relationship
            for relationship in relationships
            if relationship.relationship_type == relationship_type
        )

    def reverse_neighbors(
        self,
        *,
        target_id: str,
        relationship_type: KnowledgeRelationshipType | None = None,
    ) -> tuple[KnowledgeRelationship, ...]:
        relationships = self._reverse_index.get(target_id, ())
        if relationship_type is None:
            return relationships
        return tuple(
            relationship
            for relationship in relationships
            if relationship.relationship_type == relationship_type
        )

    def degree(self, node_id: str) -> int:
        out_deg = len(self._adjacency.get(node_id, ()))
        in_deg = len(self._reverse_index.get(node_id, ()))
        return out_deg + in_deg

    def has_path(self, source_id: str, target_id: str, max_depth: int = 5) -> bool:
        if source_id == target_id:
            return True
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(source_id, 0)]
        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)
            for rel in self._adjacency.get(current, ()):
                if rel.target_id == target_id:
                    return True
                if rel.target_id not in visited and depth + 1 <= max_depth:
                    queue.append((rel.target_id, depth + 1))
        return False

    def shortest_path(self, source_id: str, target_id: str) -> tuple[str, ...]:
        if source_id == target_id:
            return (source_id,)
        visited: set[str] = {source_id}
        queue: list[tuple[str, tuple[str, ...]]] = [(source_id, (source_id,))]
        while queue:
            current, path = queue.pop(0)
            for rel in self._adjacency.get(current, ()):
                if rel.target_id == target_id:
                    return (*path, rel.target_id)
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    queue.append((rel.target_id, (*path, rel.target_id)))
        return ()

    def all_nodes(self) -> tuple[str, ...]:
        nodes: set[str] = set()
        for source, rels in self._adjacency.items():
            nodes.add(source)
            for rel in rels:
                nodes.add(rel.target_id)
        for target, rels in self._reverse_index.items():
            nodes.add(target)
            for rel in rels:
                nodes.add(rel.target_id)
        return tuple(sorted(nodes))

    def subgraph(
        self,
        node_ids: tuple[str, ...],
    ) -> InMemoryKnowledgeGraph:
        sub = InMemoryKnowledgeGraph()
        node_set = set(node_ids)
        for node_id in node_ids:
            for rel in self._adjacency.get(node_id, ()):
                if rel.target_id in node_set:
                    sub.link(
                        source_id=node_id,
                        target_id=rel.target_id,
                        relationship_type=rel.relationship_type,
                    )
        return sub

    def clear(self) -> None:
        self._adjacency.clear()
        self._reverse_index.clear()
