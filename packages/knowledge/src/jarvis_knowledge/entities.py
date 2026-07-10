from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Entity:
    name: str
    entity_type: str
    confidence: float
    occurrences: int = 1
    context: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class EntityExtractionResult:
    document_id: str
    entities: tuple[Entity, ...] = field(default_factory=tuple)


class EntityExtractor(Protocol):
    def extract(self, text: str, document_id: str) -> EntityExtractionResult: ...
    def extract_batch(
        self, texts: tuple[str, ...], document_ids: tuple[str, ...]
    ) -> tuple[EntityExtractionResult, ...]: ...


class RegexEntityExtractor:
    def __init__(self) -> None:
        import re
        self._patterns: dict[str, str] = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "url": r"https?://[^\s]+",
            "version": r"\b\d+\.\d+\.\d+(?:[.-][a-zA-Z0-9]+)?\b",
            "path": r"(?:/[a-zA-Z0-9_.-]+)+",
        }

    def extract(self, text: str, document_id: str) -> EntityExtractionResult:
        import re
        found: dict[str, dict[str, int]] = {}
        contexts: dict[str, list[str]] = {}
        lines = text.split("\n")
        for entity_type, pattern in self._patterns.items():
            for match in re.finditer(pattern, text):
                name = match.group()
                if entity_type not in found:
                    found[entity_type] = {}
                    contexts[entity_type] = []
                found[entity_type][name] = found[entity_type].get(name, 0) + 1
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                contexts[entity_type].append(text[start:end].replace("\n", " "))

        entities: list[Entity] = []
        for entity_type, matches in found.items():
            for name, count in sorted(matches.items(), key=lambda x: -x[1]):
                ctx = contexts.get(entity_type, [])
                entity_ctx = tuple(ctx[:3]) if ctx else ()
                entities.append(
                    Entity(
                        name=name,
                        entity_type=entity_type,
                        confidence=0.9 if count > 1 else 0.6,
                        occurrences=count,
                        context=entity_ctx,
                    )
                )
        entities.sort(key=lambda e: -e.confidence)
        return EntityExtractionResult(
            document_id=document_id,
            entities=tuple(entities),
        )

    def extract_batch(
        self, texts: tuple[str, ...], document_ids: tuple[str, ...]
    ) -> tuple[EntityExtractionResult, ...]:
        if len(texts) != len(document_ids):
            msg = "texts and document_ids length mismatch"
            raise ValueError(msg)
        return tuple(
            self.extract(text, doc_id)
            for text, doc_id in zip(texts, document_ids, strict=True)
        )


class CapitalizedPhraseExtractor:
    def extract(self, text: str, document_id: str) -> EntityExtractionResult:
        import re
        phrases = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*", text)
        freq: dict[str, int] = {}
        for phrase in phrases:
            if len(phrase) > 2:
                freq[phrase] = freq.get(phrase, 0) + 1
        entities = [
            Entity(
                name=name,
                entity_type="proper_noun",
                confidence=min(1.0, count / 5),
                occurrences=count,
            )
            for name, count in sorted(freq.items(), key=lambda x: -x[1])
        ]
        return EntityExtractionResult(
            document_id=document_id,
            entities=tuple(entities),
        )

    def extract_batch(
        self, texts: tuple[str, ...], document_ids: tuple[str, ...]
    ) -> tuple[EntityExtractionResult, ...]:
        if len(texts) != len(document_ids):
            msg = "texts and document_ids length mismatch"
            raise ValueError(msg)
        return tuple(
            self.extract(text, doc_id)
            for text, doc_id in zip(texts, document_ids, strict=True)
        )
