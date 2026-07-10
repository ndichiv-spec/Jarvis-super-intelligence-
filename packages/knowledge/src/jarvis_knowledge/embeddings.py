from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class EmbeddingVector:
    values: tuple[float, ...]
    dimension: int
    model: str = "default"


@dataclass(frozen=True, slots=True)
class DocumentEmbedding:
    document_id: str
    chunk_id: str | None
    vector: EmbeddingVector
    text: str


class EmbeddingEngine(Protocol):
    def embed(self, text: str) -> EmbeddingVector: ...
    def embed_batch(self, texts: tuple[str, ...]) -> tuple[EmbeddingVector, ...]: ...
    def similarity(self, a: EmbeddingVector, b: EmbeddingVector) -> float: ...


class TfidfEmbeddingEngine:
    def __init__(self, max_features: int = 256) -> None:
        self._max_features = max_features
        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._fitted = False

    def _tokenize(self, text: str) -> dict[str, int]:
        import re
        tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        freq: dict[str, int] = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        return freq

    def embed(self, text: str) -> EmbeddingVector:
        if not self._fitted:
            self._fit(text)
        freq = self._tokenize(text)
        total = sum(freq.values()) or 1
        values = [0.0] * self._max_features
        for token, count in freq.items():
            if token in self._vocabulary:
                idx = self._vocabulary[token]
                tf = count / total
                idf = self._idf.get(token, 1.0)
                values[idx] = tf * idf
        return EmbeddingVector(
            values=tuple(values),
            dimension=self._max_features,
            model="tfidf",
        )

    def embed_batch(self, texts: tuple[str, ...]) -> tuple[EmbeddingVector, ...]:
        return tuple(self.embed(t) for t in texts)

    def similarity(self, a: EmbeddingVector, b: EmbeddingVector) -> float:
        if a.dimension != b.dimension:
            return 0.0
        dot = sum(av * bv for av, bv in zip(a.values, b.values, strict=False))
        norm_a = sum(v * v for v in a.values) ** 0.5 or 1.0
        norm_b = sum(v * v for v in b.values) ** 0.5 or 1.0
        return dot / (norm_a * norm_b)

    def _fit(self, text: str) -> None:
        freq = self._tokenize(text)
        sorted_tokens = sorted(freq.items(), key=lambda x: -x[1])
        for i, (token, _) in enumerate(sorted_tokens[: self._max_features]):
            self._vocabulary[token] = i
            self._idf[token] = 1.0
        self._fitted = True


class RandomEmbeddingEngine:
    def __init__(self, dimension: int = 128) -> None:
        import random
        self._dimension = dimension
        self._rng = random.Random(42)

    def embed(self, text: str) -> EmbeddingVector:
        import math
        values = tuple(self._rng.gauss(0, 1) for _ in range(self._dimension))
        norm = math.sqrt(sum(v * v for v in values))
        values = tuple(v / norm for v in values)
        return EmbeddingVector(values=values, dimension=self._dimension, model="random")

    def embed_batch(self, texts: tuple[str, ...]) -> tuple[EmbeddingVector, ...]:
        return tuple(self.embed(t) for t in texts)

    def similarity(self, a: EmbeddingVector, b: EmbeddingVector) -> float:
        if a.dimension != b.dimension:
            return 0.0
        dot = sum(av * bv for av, bv in zip(a.values, b.values, strict=False))
        return max(-1.0, min(1.0, dot))
