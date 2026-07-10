from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

from jarvis_knowledge.models import (
    KnowledgeAccessContext,
    KnowledgeCitation,
    KnowledgeCitationType,
    KnowledgeClassification,
    KnowledgeCollection,
    KnowledgeDocument,
    KnowledgeImportance,
    KnowledgePolicy,
    KnowledgePolicyScope,
    KnowledgeRankingContext,
    KnowledgeSearchQuery,
    KnowledgeSensitivity,
    KnowledgeSource,
    KnowledgeValidationIssue,
    KnowledgeValidationReport,
    KnowledgeVersion,
    KnowledgeVisibility,
    ScoredKnowledge,
    ValidationSeverity,
)
from jarvis_knowledge.protocols import KnowledgeCatalog


def utc_now() -> datetime:
    return datetime.now(UTC)


class DefaultKnowledgeClassificationEngine:
    def classify(
        self,
        *,
        document: KnowledgeDocument,
        source: KnowledgeSource,
        collections: tuple[KnowledgeCollection, ...],
    ) -> KnowledgeClassification:
        base = document.metadata.classification
        primary_collection = collections[0] if collections else None
        domain = primary_collection.domain if primary_collection is not None else base.domain
        category = primary_collection.name if primary_collection is not None else base.category
        return base.with_overrides(
            domain=domain,
            category=category,
            workspace=document.metadata.workspace,
            project=document.metadata.project,
            tags=frozenset({*document.metadata.tags, *base.tags, source.source_type.value}),
        )


class DefaultKnowledgeValidationEngine:
    def validate(
        self,
        *,
        document: KnowledgeDocument,
        catalog: KnowledgeCatalog,
    ) -> KnowledgeValidationReport:
        issues: list[KnowledgeValidationIssue] = []

        required_text_values = (
            document.metadata.title,
            document.summary,
            document.content_reference,
            document.metadata.owner,
            document.metadata.workspace,
            document.metadata.project,
        )
        completeness = 1.0 if all(value.strip() for value in required_text_values) else 0.4
        if completeness < 1.0:
            issues.append(
                KnowledgeValidationIssue(
                    code="incomplete_document",
                    message="Knowledge document has required fields missing.",
                    severity=ValidationSeverity.ERROR,
                )
            )

        consistency = 1.0
        classification = document.metadata.classification
        if (
            classification.workspace != document.metadata.workspace
            or classification.project != document.metadata.project
        ):
            consistency = 0.4
            issues.append(
                KnowledgeValidationIssue(
                    code="classification_consistency",
                    message="Classification workspace/project is inconsistent with metadata.",
                    severity=ValidationSeverity.ERROR,
                )
            )

        integrity = 1.0
        if not (0.0 <= document.metadata.confidence <= 1.0) or document.metadata.version < 1:
            integrity = 0.3
            issues.append(
                KnowledgeValidationIssue(
                    code="integrity_violation",
                    message="Confidence or version violates integrity constraints.",
                    severity=ValidationSeverity.ERROR,
                )
            )

        source = catalog.get_source(document.source_id)
        source_quality = source.quality_score if source is not None else 0.0
        if source is None:
            issues.append(
                KnowledgeValidationIssue(
                    code="missing_source",
                    message="Knowledge source is not registered.",
                    severity=ValidationSeverity.ERROR,
                )
            )
        elif source_quality < 0.3:
            issues.append(
                KnowledgeValidationIssue(
                    code="low_source_quality",
                    message="Knowledge source quality is below policy threshold.",
                    severity=ValidationSeverity.WARNING,
                )
            )

        version_validity = 1.0 if document.metadata.version >= 1 else 0.0

        relationship_integrity = 1.0
        if document.metadata.relationships:
            unresolved = [
                relationship
                for relationship in document.metadata.relationships
                if catalog.get_document(relationship.target_id) is None
            ]
            if unresolved:
                relationship_integrity = 0.3
                issues.append(
                    KnowledgeValidationIssue(
                        code="relationship_integrity",
                        message="Document contains relationships to unknown targets.",
                        severity=ValidationSeverity.ERROR,
                    )
                )

        is_valid = all(issue.severity != ValidationSeverity.ERROR for issue in issues)
        return KnowledgeValidationReport(
            document_id=document.metadata.identifier,
            is_valid=is_valid,
            completeness=completeness,
            consistency=consistency,
            integrity=integrity,
            source_quality=source_quality,
            version_validity=version_validity,
            relationship_integrity=relationship_integrity,
            issues=tuple(issues),
        )


class DefaultKnowledgeSearchEngine:
    def search(
        self,
        documents: tuple[KnowledgeDocument, ...],
        query: KnowledgeSearchQuery,
    ) -> tuple[KnowledgeDocument, ...]:
        matches = tuple(document for document in documents if self._matches(document, query))
        return matches[: max(query.limit, 0)]

    def _matches(self, document: KnowledgeDocument, query: KnowledgeSearchQuery) -> bool:
        metadata = document.metadata
        classification = metadata.classification
        if query.identifier is not None and metadata.identifier != query.identifier:
            return False
        if query.title is not None and query.title.lower() not in metadata.title.lower():
            return False
        if query.category is not None and classification.category != query.category:
            return False
        if query.topic is not None and classification.topic != query.topic:
            return False
        if query.workspace is not None and metadata.workspace != query.workspace:
            return False
        if query.project is not None and metadata.project != query.project:
            return False
        if query.owner is not None and metadata.owner != query.owner:
            return False
        if query.language is not None and metadata.language != query.language:
            return False
        if query.tags and not query.tags.issubset(metadata.tags):
            return False
        if query.relationship_type is not None and not any(
            relationship.relationship_type == query.relationship_type
            for relationship in metadata.relationships
        ):
            return False
        if query.metadata_filters and not all(
            document.attributes.get(key) == value for key, value in query.metadata_filters.items()
        ):
            return False
        if query.terms:
            searchable_text = " ".join(
                (
                    metadata.title,
                    metadata.description,
                    document.summary,
                    document.content_reference,
                    classification.domain,
                    classification.topic,
                    classification.category,
                    " ".join(metadata.tags),
                )
            ).lower()
            if not all(term.lower() in searchable_text for term in query.terms):
                return False
        return True


class DefaultKnowledgeRankingEngine:
    def rank(
        self,
        documents: tuple[KnowledgeDocument, ...],
        context: KnowledgeRankingContext,
    ) -> tuple[ScoredKnowledge, ...]:
        scored = tuple(self._score_document(document, context) for document in documents)
        return tuple(sorted(scored, key=lambda item: item.score, reverse=True))

    def _score_document(
        self,
        document: KnowledgeDocument,
        context: KnowledgeRankingContext,
    ) -> ScoredKnowledge:
        metadata = document.metadata

        relevance = self._relevance(metadata.title, document.summary, context.query_terms)
        authority = metadata.confidence

        age_days = (context.now - metadata.updated_at).days
        freshness = max(0.0, 1.0 - (age_days / 3650.0))

        relationship_strength = min(1.0, len(metadata.relationships) / 8.0)
        workspace_context = 1.0 if metadata.workspace == context.workspace else 0.0
        project_context = 1.0 if metadata.project == context.project else 0.0
        confidence = metadata.confidence

        score = (
            (0.28 * relevance)
            + (0.20 * authority)
            + (0.14 * freshness)
            + (0.13 * relationship_strength)
            + (0.13 * workspace_context)
            + (0.12 * project_context)
        )
        return ScoredKnowledge(
            document=document,
            score=round(score, 6),
            confidence=confidence,
            reasons=(
                "relevance",
                "authority",
                "freshness",
                "relationship_strength",
                "workspace_context",
                "project_context",
            ),
        )

    def _relevance(self, title: str, summary: str, terms: tuple[str, ...]) -> float:
        if not terms:
            return 0.5
        haystack = f"{title} {summary}".lower()
        hits = sum(1 for term in terms if term.lower() in haystack)
        return hits / len(terms)


class InMemoryCitationEngine:
    def __init__(self) -> None:
        self._by_document: dict[str, tuple[KnowledgeCitation, ...]] = {}

    def create_citation(
        self,
        *,
        from_document_id: str,
        to_reference: str,
        citation_type: KnowledgeCitationType,
        metadata: dict[str, str] | None = None,
    ) -> KnowledgeCitation:
        citation = KnowledgeCitation(
            citation_id=f"cit-{uuid4().hex}",
            from_document_id=from_document_id,
            to_reference=to_reference,
            citation_type=citation_type,
            metadata=metadata or {},
        )
        existing = self._by_document.get(from_document_id, ())
        self._by_document[from_document_id] = (*existing, citation)
        return citation

    def list_citations(self, document_id: str) -> tuple[KnowledgeCitation, ...]:
        return self._by_document.get(document_id, ())


class InMemoryKnowledgeVersionManager:
    def __init__(self) -> None:
        self._history: dict[str, tuple[KnowledgeVersion, ...]] = {}

    def register_initial(self, document: KnowledgeDocument) -> None:
        if document.metadata.identifier in self._history:
            return
        initial = KnowledgeVersion(
            version_id=f"ver-{uuid4().hex}",
            document_id=document.metadata.identifier,
            number=document.metadata.version,
            changed_by=document.metadata.owner,
            change_summary="Initial registration",
            compatible_with=(document.metadata.version,),
        )
        self._history[document.metadata.identifier] = (initial,)

    def record_version(
        self,
        *,
        document: KnowledgeDocument,
        changed_by: str,
        change_summary: str,
        compatible_with: tuple[int, ...] = (),
        deprecated: bool = False,
    ) -> KnowledgeDocument:
        current = self.current_version(document.metadata.identifier)
        next_version_number = 1 if current is None else current.number + 1
        updated_document = replace(
            document,
            metadata=document.metadata.touch(version=next_version_number),
        )
        new_version = KnowledgeVersion(
            version_id=f"ver-{uuid4().hex}",
            document_id=updated_document.metadata.identifier,
            number=next_version_number,
            changed_by=changed_by,
            change_summary=change_summary,
            compatible_with=(compatible_with or (next_version_number,)),
            deprecated=deprecated,
            supersedes_version=current.number if current is not None else None,
        )
        history = self._history.get(updated_document.metadata.identifier, ())
        self._history[updated_document.metadata.identifier] = (*history, new_version)
        return updated_document

    def current_version(self, document_id: str) -> KnowledgeVersion | None:
        history = self._history.get(document_id, ())
        return history[-1] if history else None

    def history(self, document_id: str) -> tuple[KnowledgeVersion, ...]:
        return self._history.get(document_id, ())

    def is_compatible(self, document_id: str, required_version: int) -> bool:
        current = self.current_version(document_id)
        if current is None:
            return False
        return required_version in current.compatible_with


class DefaultKnowledgePolicyEngine:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str, str], KnowledgePolicy] = {}

    def register_policy(self, scope: KnowledgePolicyScope, policy: KnowledgePolicy) -> None:
        self._policies[(scope.owner, scope.workspace, scope.project)] = policy

    def resolve(self, scope: KnowledgePolicyScope) -> KnowledgePolicy:
        policy = self._policies.get((scope.owner, scope.workspace, scope.project))
        if policy is not None:
            return policy
        if scope.is_enterprise:
            return KnowledgePolicy(
                policy_id="enterprise-default",
                name="Enterprise Default",
                allowed_visibility=(
                    KnowledgeVisibility.PRIVATE,
                    KnowledgeVisibility.WORKSPACE,
                    KnowledgeVisibility.PROJECT,
                    KnowledgeVisibility.ENTERPRISE,
                ),
                workspace_isolation=True,
                enterprise_governance=True,
                enforce_project_ownership=True,
            )
        return KnowledgePolicy(policy_id="default", name="Default Knowledge Policy")

    def can_access(
        self,
        *,
        document: KnowledgeDocument,
        access: KnowledgeAccessContext,
        policy: KnowledgePolicy,
    ) -> bool:
        visibility = document.metadata.visibility
        if visibility not in policy.allowed_visibility:
            return False
        if policy.workspace_isolation and document.metadata.workspace != access.workspace:
            return False
        if policy.enforce_project_ownership and document.metadata.project != access.project:
            return False
        if visibility == KnowledgeVisibility.PRIVATE:
            if document.metadata.owner != access.requester_id:
                return False
        return True


def default_classification(
    *,
    workspace: str,
    project: str,
    language: str,
) -> KnowledgeClassification:
    return KnowledgeClassification(
        domain="general",
        topic="general",
        category="general",
        importance=KnowledgeImportance.NORMAL,
        sensitivity=KnowledgeSensitivity.INTERNAL,
        visibility=KnowledgeVisibility.WORKSPACE,
        language=language,
        workspace=workspace,
        project=project,
    )
