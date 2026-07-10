from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from pathlib import PurePath
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainIdentifier:
    value: UUID

    @classmethod
    def new(cls) -> DomainIdentifier:
        return cls(value=uuid4())


@dataclass(frozen=True, slots=True)
class Timestamp:
    value: datetime

    @classmethod
    def now(cls) -> Timestamp:
        return cls(value=datetime.now(tz=UTC))


class PriorityLevel(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ImportanceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class Coordinates:
    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class Language:
    code: str


@dataclass(frozen=True, slots=True)
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True, slots=True)
class Email:
    value: str


@dataclass(frozen=True, slots=True)
class FileReference:
    path: PurePath


@dataclass(frozen=True, slots=True)
class DurationValue:
    value: timedelta


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str
