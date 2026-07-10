from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, IntEnum, auto

from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class TrustLevel(IntEnum):
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4


class TrustRelationshipType(Enum):
    USER_TO_AGENT = auto()
    USER_TO_EXTENSION = auto()
    AGENT_TO_TOOL = auto()
    EXTENSION_TO_SERVICE = auto()
    SERVICE_TO_ORGANIZATION = auto()
    EXTERNAL_SYSTEM = auto()


@dataclass(frozen=True, slots=True)
class TrustRelationship:
    metadata: SecurityMetadata
    source_identifier: str
    target_identifier: str
    relationship_type: TrustRelationshipType
    level: TrustLevel
    rationale: str
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.TRUST_RELATIONSHIP:
            raise ValueError("metadata.object_type must be trust_relationship")
        if not self.source_identifier.strip():
            raise ValueError("source_identifier cannot be empty")
        if not self.target_identifier.strip():
            raise ValueError("target_identifier cannot be empty")
        if not self.rationale.strip():
            raise ValueError("rationale cannot be empty")

    def is_active(self, at: datetime | None = None) -> bool:
        if self.expires_at is None:
            return True
        evaluation_time = at if at is not None else datetime.now(tz=UTC)
        return self.expires_at >= evaluation_time

    @classmethod
    def create(
        cls,
        *,
        source_identifier: str,
        target_identifier: str,
        relationship_type: TrustRelationshipType,
        level: TrustLevel,
        rationale: str,
        owner_identifier: str,
        expires_at: datetime | None = None,
    ) -> TrustRelationship:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.TRUST_RELATIONSHIP,
                owner_identifier=owner_identifier,
            ),
            source_identifier=source_identifier,
            target_identifier=target_identifier,
            relationship_type=relationship_type,
            level=level,
            rationale=rationale,
            expires_at=expires_at,
        )


@dataclass(slots=True)
class TrustModel:
    _relationships: dict[tuple[str, str], TrustRelationship] = field(default_factory=dict)

    def establish(self, relationship: TrustRelationship) -> TrustRelationship:
        key = (relationship.source_identifier, relationship.target_identifier)
        self._relationships[key] = relationship
        return relationship

    def get(self, source_identifier: str, target_identifier: str) -> TrustRelationship | None:
        return self._relationships.get((source_identifier, target_identifier))

    def evaluate(
        self,
        source_identifier: str,
        target_identifier: str,
        at: datetime | None = None,
    ) -> TrustLevel:
        relationship = self.get(source_identifier, target_identifier)
        if relationship is None:
            return TrustLevel.UNTRUSTED
        return relationship.level if relationship.is_active(at=at) else TrustLevel.UNTRUSTED

    def list_relationships(self) -> tuple[TrustRelationship, ...]:
        return tuple(self._relationships.values())
