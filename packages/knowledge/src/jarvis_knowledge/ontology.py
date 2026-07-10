from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class OntologyClass:
    class_id: str
    name: str
    description: str = ""
    parent_class_id: str | None = None
    properties: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class OntologyRelation:
    relation_id: str
    name: str
    domain_class_id: str
    range_class_id: str
    description: str = ""


@dataclass(slots=True)
class OntologyStore:
    _classes: dict[str, OntologyClass] = field(default_factory=dict)
    _relations: dict[str, OntologyRelation] = field(default_factory=dict)

    def add_class(self, cls: OntologyClass) -> None:
        self._classes[cls.class_id] = cls

    def get_class(self, class_id: str) -> OntologyClass | None:
        return self._classes.get(class_id)

    def add_relation(self, relation: OntologyRelation) -> None:
        self._relations[relation.relation_id] = relation

    def get_relation(self, relation_id: str) -> OntologyRelation | None:
        return self._relations.get(relation_id)

    def list_classes(self) -> tuple[OntologyClass, ...]:
        return tuple(self._classes.values())

    def list_relations(self) -> tuple[OntologyRelation, ...]:
        return tuple(self._relations.values())

    def subclasses(self, class_id: str) -> tuple[OntologyClass, ...]:
        return tuple(
            cls for cls in self._classes.values()
            if cls.parent_class_id == class_id
        )


class OntologyEngine(Protocol):
    def map_document(
        self, text: str, ontology: OntologyStore,
    ) -> tuple[tuple[str, str], ...]: ...
    def infer_relations(
        self, ontology: OntologyStore,
    ) -> tuple[OntologyRelation, ...]: ...


class KeywordOntologyEngine:
    def map_document(
        self, text: str, ontology: OntologyStore,
    ) -> tuple[tuple[str, str], ...]:
        text_lower = text.lower()
        mappings: list[tuple[str, str]] = []
        for cls in ontology.list_classes():
            if cls.name.lower() in text_lower:
                mappings.append((cls.class_id, cls.name))
        return tuple(mappings)

    def infer_relations(
        self, ontology: OntologyStore,
    ) -> tuple[OntologyRelation, ...]:
        new_relations: list[OntologyRelation] = []
        for cls in ontology.list_classes():
            if cls.parent_class_id:
                existing = any(
                    r.domain_class_id == cls.class_id
                    and r.range_class_id == cls.parent_class_id
                    for r in ontology.list_relations()
                )
                if not existing:
                    new_relations.append(
                        OntologyRelation(
                            relation_id=f"rel-infer-{cls.class_id}-{cls.parent_class_id}",
                            name="is_subclass_of",
                            domain_class_id=cls.class_id,
                            range_class_id=cls.parent_class_id,
                            description="Inferred subclass relationship",
                        )
                    )
        return tuple(new_relations)
