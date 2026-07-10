from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from jarvis_knowledge.models import (
    KnowledgeDocument,
    KnowledgeValidationIssue,
    KnowledgeValidationReport,
    ValidationSeverity,
)
from jarvis_knowledge.protocols import KnowledgeCatalog
from jarvis_knowledge.engines import DefaultKnowledgeValidationEngine


class EnhancedValidationEngine(Protocol):
    def validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport: ...
    def deep_validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport: ...


class DeepValidationEngine:
    def __init__(self) -> None:
        self._base = DefaultKnowledgeValidationEngine()

    def validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport:
        return self._base.validate(document=document, catalog=catalog)

    def deep_validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport:
        base_report = self._base.validate(document=document, catalog=catalog)
        issues: list[KnowledgeValidationIssue] = list(base_report.issues)
        completeness = base_report.completeness
        consistency = base_report.consistency
        integrity = base_report.integrity
        source_quality = base_report.source_quality
        version_validity = base_report.version_validity
        relationship_integrity = base_report.relationship_integrity

        if document.metadata.title and len(document.metadata.title) < 3:
            issues.append(
                KnowledgeValidationIssue(
                    code="title_too_short",
                    message="Document title is too short (min 3 characters).",
                    severity=ValidationSeverity.WARNING,
                )
            )
            consistency = min(consistency, 0.7)

        if document.summary and len(document.summary) < 10:
            issues.append(
                KnowledgeValidationIssue(
                    code="summary_too_short",
                    message="Document summary is too short (min 10 characters).",
                    severity=ValidationSeverity.WARNING,
                )
            )
            completeness = min(completeness, 0.7)

        if document.metadata.confidence > 1.0 or document.metadata.confidence < 0.0:
            issues.append(
                KnowledgeValidationIssue(
                    code="confidence_out_of_range",
                    message="Confidence must be between 0.0 and 1.0.",
                    severity=ValidationSeverity.ERROR,
                )
            )
            integrity = min(integrity, 0.3)

        if document.metadata.tags:
            low_quality_tags = [t for t in document.metadata.tags if len(t) < 2]
            if low_quality_tags:
                issues.append(
                    KnowledgeValidationIssue(
                        code="low_quality_tags",
                        message=f"Tags too short: {low_quality_tags}",
                        severity=ValidationSeverity.WARNING,
                    )
                )

        if document.attributes:
            known_attrs = {"raw_length", "format", "encoding"}
            unknown = set(document.attributes.keys()) - known_attrs
            if unknown:
                issues.append(
                    KnowledgeValidationIssue(
                        code="unknown_attributes",
                        message=f"Unknown attributes: {unknown}",
                        severity=ValidationSeverity.INFO,
                    )
                )

        is_valid = all(issue.severity != ValidationSeverity.ERROR for issue in issues)
        return KnowledgeValidationReport(
            document_id=document.metadata.identifier,
            is_valid=is_valid,
            completeness=round(completeness, 4),
            consistency=round(consistency, 4),
            integrity=round(integrity, 4),
            source_quality=round(source_quality, 4),
            version_validity=round(version_validity, 4),
            relationship_integrity=round(relationship_integrity, 4),
            issues=tuple(issues),
        )


class BatchValidationEngine:
    def __init__(self) -> None:
        self._base = DeepValidationEngine()

    def validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport:
        return self._base.validate(document=document, catalog=catalog)

    def deep_validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport:
        return self._base.deep_validate(document=document, catalog=catalog)

    def validate_batch(
        self,
        documents: tuple[KnowledgeDocument, ...],
        catalog: KnowledgeCatalog,
    ) -> tuple[KnowledgeValidationReport, ...]:
        return tuple(
            self._base.deep_validate(document=document, catalog=catalog)
            for document in documents
        )
