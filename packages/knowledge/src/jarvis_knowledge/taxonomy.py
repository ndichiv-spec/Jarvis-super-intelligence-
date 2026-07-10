from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class TaxonomyNode:
    node_id: str
    name: str
    parent_id: str | None = None
    description: str = ""
    children: tuple[str, ...] = field(default_factory=tuple)


@dataclass(slots=True)
class TaxonomyTree:
    _nodes: dict[str, TaxonomyNode] = field(default_factory=dict)

    def add_node(self, node: TaxonomyNode) -> None:
        self._nodes[node.node_id] = node
        if node.parent_id and node.parent_id in self._nodes:
            parent = self._nodes[node.parent_id]
            self._nodes[node.parent_id] = TaxonomyNode(
                node_id=parent.node_id,
                name=parent.name,
                parent_id=parent.parent_id,
                description=parent.description,
                children=(*parent.children, node.node_id),
            )

    def get_node(self, node_id: str) -> TaxonomyNode | None:
        return self._nodes.get(node_id)

    def get_children(self, node_id: str) -> tuple[TaxonomyNode, ...]:
        node = self._nodes.get(node_id)
        if node is None:
            return ()
        return tuple(
            child for child in self._nodes.values()
            if child.parent_id == node_id
        )

    def get_ancestors(self, node_id: str) -> tuple[TaxonomyNode, ...]:
        ancestors: list[TaxonomyNode] = []
        current = self._nodes.get(node_id)
        while current is not None and current.parent_id:
            parent = self._nodes.get(current.parent_id)
            if parent is not None:
                ancestors.append(parent)
                current = parent
            else:
                break
        return tuple(ancestors)

    def search(self, query: str) -> tuple[TaxonomyNode, ...]:
        q = query.lower()
        return tuple(
            node for node in self._nodes.values()
            if q in node.name.lower() or q in node.description.lower()
        )


class TaxonomyEngine(Protocol):
    def classify(self, text: str, taxonomy: TaxonomyTree) -> tuple[str, ...]: ...
    def suggest_parent(self, name: str, taxonomy: TaxonomyTree) -> str | None: ...


class KeywordTaxonomyEngine:
    def classify(self, text: str, taxonomy: TaxonomyTree) -> tuple[str, ...]:
        text_lower = text.lower()
        matches: list[tuple[str, int]] = []
        for node in taxonomy._nodes.values():
            if not node.parent_id:
                continue
            score = 0
            words = node.name.lower().split()
            for word in words:
                if word in text_lower:
                    score += text_lower.count(word)
            if score > 0:
                matches.append((node.node_id, score))
        matches.sort(key=lambda x: -x[1])
        return tuple(node_id for node_id, _ in matches[:5])

    def suggest_parent(self, name: str, taxonomy: TaxonomyTree) -> str | None:
        name_lower = name.lower()
        best_score = 0
        best_parent: str | None = None
        for node in taxonomy._nodes.values():
            if node.parent_id is not None:
                continue
            words = node.name.lower().split()
            score = sum(1 for w in words if w in name_lower or name_lower in w)
            if score > best_score:
                best_score = score
                best_parent = node.node_id
        return best_parent
