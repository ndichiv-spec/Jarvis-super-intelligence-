from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class SemanticAnalysis:
    document_id: str
    topics: tuple[str, ...] = field(default_factory=tuple)
    keywords: tuple[str, ...] = field(default_factory=tuple)
    sentiment: float = 0.0
    language_detected: str = "en"
    entities_mentioned: tuple[str, ...] = field(default_factory=tuple)
    summary_sentence: str = ""


class SemanticEngine(Protocol):
    def analyze(self, text: str, document_id: str) -> SemanticAnalysis: ...


class TfidfSemanticEngine:
    def analyze(self, text: str, document_id: str) -> SemanticAnalysis:
        import re
        words = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        freq: dict[str, int] = {}
        for word in words:
            if len(word) > 2:
                freq[word] = freq.get(word, 0) + 1
        sorted_keywords = sorted(freq, key=lambda w: -freq[w])[:10]
        topics = sorted(freq, key=lambda w: -freq[w])[:3]
        entities = [
            word for word in sorted_keywords
            if word[0].isupper() and len(word) > 2
        ]
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        summary = sentences[0] if sentences else text[:200]
        return SemanticAnalysis(
            document_id=document_id,
            topics=tuple(topics),
            keywords=tuple(sorted_keywords),
            language_detected="en",
            entities_mentioned=tuple(entities[:5]),
            summary_sentence=summary[:200],
        )
