from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Protocol

from jarvis_security.audit import AuditEvent
from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, new_metadata


class ComplianceFramework(Enum):
    GDPR = auto()
    ISO_27001 = auto()
    SOC_2 = auto()
    HIPAA = auto()
    ENTERPRISE_RETENTION = auto()


class ComplianceStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    PARTIALLY_COMPLIANT = auto()
    NEEDS_REVIEW = auto()


@dataclass(frozen=True, slots=True)
class ComplianceControl:
    metadata: SecurityMetadata
    framework: ComplianceFramework
    control_identifier: str
    description: str
    policy_reference: str
    required: bool = True

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.COMPLIANCE_CONTROL:
            raise ValueError("metadata.object_type must be compliance_control")
        if not self.control_identifier.strip():
            raise ValueError("control_identifier cannot be empty")
        if not self.description.strip():
            raise ValueError("description cannot be empty")
        if not self.policy_reference.strip():
            raise ValueError("policy_reference cannot be empty")

    @classmethod
    def create(
        cls,
        *,
        framework: ComplianceFramework,
        control_identifier: str,
        description: str,
        policy_reference: str,
        owner_identifier: str,
        required: bool = True,
    ) -> ComplianceControl:
        return cls(
            metadata=new_metadata(
                object_type=SecurityObjectType.COMPLIANCE_CONTROL,
                owner_identifier=owner_identifier,
                policy_references=(policy_reference,),
            ),
            framework=framework,
            control_identifier=control_identifier,
            description=description,
            policy_reference=policy_reference,
            required=required,
        )


@dataclass(frozen=True, slots=True)
class ComplianceAssessment:
    metadata: SecurityMetadata
    framework: ComplianceFramework
    status: ComplianceStatus
    generated_at: datetime
    controls_evaluated: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.metadata.object_type is not SecurityObjectType.COMPLIANCE_ASSESSMENT:
            raise ValueError("metadata.object_type must be compliance_assessment")


class ComplianceRegistryContract(Protocol):
    def register_control(self, control: ComplianceControl) -> ComplianceControl:
        ...

    def list_controls(
        self,
        framework: ComplianceFramework | None = None,
    ) -> tuple[ComplianceControl, ...]:
        ...


class AuditExportContract(Protocol):
    def export(self, *, framework: ComplianceFramework, events: tuple[AuditEvent, ...]) -> str:
        ...
