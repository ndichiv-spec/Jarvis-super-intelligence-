from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Summary:
    document_id: str
    text: str
    compression_ratio: float = 0.0
    sentences: int = 0


class SummarizationEngine(Protocol):
    def summarize(self, text: str, document_id: str, *, max_sentences: int = 5) -> Summary: ...
    def summarize_batch(
        self,
        texts: tuple[str, ...],
        document_ids: tuple[str, ...],
        *,
        max_sentences: int = 5,
    ) -> tuple[Summary, ...]: ...


class ExtractiveSummarizer:
    def summarize(self, text: str, document_id: str, *, max_sentences: int = 5) -> Summary:
        import re
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if not sentences:
            return Summary(document_id=document_id, text="", compression_ratio=0.0, sentences=0)
        if len(sentences) <= max_sentences:
            full = ". ".join(sentences) + "."
            return Summary(
                document_id=document_id,
                text=full,
                compression_ratio=1.0,
                sentences=len(sentences),
            )
        scored: list[tuple[float, str]] = []
        all_words = text.lower().split()
        word_freq: dict[str, float] = {}
        for w in all_words:
            word_freq[w] = word_freq.get(w, 0) + 1
        max_freq = max(word_freq.values()) if word_freq else 1
        for w in word_freq:
            word_freq[w] /= max_freq
        for sentence in sentences:
            words = sentence.lower().split()
            if not words:
                scored.append((0.0, sentence))
                continue
            score = sum(word_freq.get(w, 0) for w in words) / len(words)
            position_bonus = 1.0 + (0.5 / (1 + len(scored)))
            scored.append((score * position_bonus, sentence))
        scored.sort(key=lambda x: -x[0])
        selected = [s for _, s in scored[:max_sentences]]
        selected.sort(key=lambda s: sentences.index(s))
        summary_text = ". ".join(selected) + "."
        return Summary(
            document_id=document_id,
            text=summary_text,
            compression_ratio=len(selected) / len(sentences),
            sentences=len(selected),
        )

    def summarize_batch(
        self,
        texts: tuple[str, ...],
        document_ids: tuple[str, ...],
        *,
        max_sentences: int = 5,
    ) -> tuple[Summary, ...]:
        if len(texts) != len(document_ids):
            msg = "texts and document_ids length mismatch"
            raise ValueError(msg)
        return tuple(
            self.summarize(t, d, max_sentences=max_sentences)
            for t, d in zip(texts, document_ids, strict=True)
        )


class FirstSentenceSummarizer:
    def summarize(self, text: str, document_id: str, *, max_sentences: int = 5) -> Summary:
        import re
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if not sentences:
            return Summary(document_id=document_id, text="", compression_ratio=0.0, sentences=0)
        selected = sentences[:max_sentences]
        summary_text = ". ".join(selected) + "."
        return Summary(
            document_id=document_id,
            text=summary_text,
            compression_ratio=len(selected) / len(sentences),
            sentences=len(selected),
        )

    def summarize_batch(
        self,
        texts: tuple[str, ...],
        document_ids: tuple[str, ...],
        *,
        max_sentences: int = 5,
    ) -> tuple[Summary, ...]:
        if len(texts) != len(document_ids):
            msg = "texts and document_ids length mismatch"
            raise ValueError(msg)
        return tuple(
            self.summarize(t, d, max_sentences=max_sentences)
            for t, d in zip(texts, document_ids, strict=True)
        )
