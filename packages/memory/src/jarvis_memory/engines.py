from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import UTC, datetime

from jarvis_memory.models import (
    ForgetDecision,
    MemoryPolicy,
    MemoryRecord,
    MemoryRelationship,
    PolicyScope,
    RankingContext,
    RetrievalQuery,
    ScoredMemory,
    TimelineEvent,
)


class DefaultRetrievalEngine:
    def search(
        self, memories: tuple[MemoryRecord, ...], query: RetrievalQuery
    ) -> tuple[MemoryRecord, ...]:
        result: list[MemoryRecord] = []
        for memory in memories:
            if query.identifier is not None and memory.metadata.identifier != query.identifier:
                continue
            if (
                query.conversation_id is not None
                and memory.conversation_id != query.conversation_id
            ):
                continue
            if query.project_id is not None and memory.project_id != query.project_id:
                continue
            if query.intent is not None and memory.intent != query.intent:
                continue
            if (
                query.min_importance is not None
                and memory.metadata.importance < query.min_importance
            ):
                continue
            if query.relationship_type is not None and not any(
                relation.relationship_type == query.relationship_type
                for relation in memory.metadata.relationships
            ):
                continue
            if query.context is not None:
                context_value = (memory.context or "") + " " + memory.content
                if query.context.casefold() not in context_value.casefold():
                    continue
            if query.tags and not query.tags.issubset(memory.metadata.tags):
                continue

            occurred_at = memory.event_time or memory.metadata.created_at
            if query.from_time is not None and occurred_at < query.from_time:
                continue
            if query.to_time is not None and occurred_at > query.to_time:
                continue
            result.append(memory)
        return tuple(result)


class DefaultRankingEngine:
    def rank(
        self, memories: tuple[MemoryRecord, ...], context: RankingContext
    ) -> tuple[ScoredMemory, ...]:
        scored = tuple(
            ScoredMemory(memory=memory, score=self._score(memory=memory, context=context))
            for memory in memories
        )
        return tuple(sorted(scored, key=lambda item: item.score, reverse=True))

    def _score(self, *, memory: MemoryRecord, context: RankingContext) -> float:
        age_days = max((context.now - memory.metadata.updated_at).total_seconds() / 86_400, 0.0)
        recency_score = max(0.0, 1.0 - (age_days / 30.0))
        frequency_score = min(memory.metadata.access_count / 10.0, 1.0)
        feedback_score = min(max((memory.metadata.user_feedback + 1.0) / 2.0, 0.0), 1.0)

        project_score = (
            1.0
            if context.project_id is not None and memory.project_id == context.project_id
            else 0.0
        )
        conversation_score = (
            1.0
            if context.conversation_id is not None
            and memory.conversation_id == context.conversation_id
            else 0.0
        )
        workflow_score = (
            1.0
            if context.workflow_id is not None and memory.workflow_id == context.workflow_id
            else 0.0
        )

        return (
            memory.metadata.importance * 0.25
            + recency_score * 0.2
            + frequency_score * 0.1
            + memory.metadata.confidence * 0.2
            + feedback_score * 0.1
            + project_score * 0.05
            + conversation_score * 0.05
            + workflow_score * 0.05
        )


class DefaultConsolidationEngine:
    def consolidate(self, memories: tuple[MemoryRecord, ...]) -> tuple[MemoryRecord, ...]:
        grouped: dict[tuple[str, str, str | None, str | None, str | None], list[MemoryRecord]] = (
            defaultdict(list)
        )
        for memory in memories:
            key = (
                memory.memory_type.value,
                memory.content.strip().casefold(),
                memory.project_id,
                memory.conversation_id,
                memory.workflow_id,
            )
            grouped[key].append(memory)

        consolidated: list[MemoryRecord] = []
        for group in grouped.values():
            if len(group) == 1:
                consolidated.append(group[0])
                continue
            consolidated.append(self._merge_group(group))
        return tuple(sorted(consolidated, key=lambda memory: memory.metadata.created_at))

    def _merge_group(self, group: list[MemoryRecord]) -> MemoryRecord:
        sorted_group = sorted(group, key=lambda memory: memory.metadata.created_at)
        base = sorted_group[0]
        latest_update = max(memory.metadata.updated_at for memory in sorted_group)

        relationships: dict[tuple[str, str], MemoryRelationship] = {}
        for memory in sorted_group:
            for relationship in memory.metadata.relationships:
                relationships[(relationship.target_id, relationship.relationship_type.value)] = (
                    relationship
                )

        merged_tags = frozenset(tag for memory in sorted_group for tag in memory.metadata.tags)
        merged_lineage = tuple(
            dict.fromkeys(
                item
                for memory in sorted_group
                for item in (*memory.metadata.lineage, memory.metadata.identifier)
            )
        )
        merged_access_count = sum(memory.metadata.access_count for memory in sorted_group)
        merged_feedback = sum(memory.metadata.user_feedback for memory in sorted_group) / len(
            sorted_group
        )

        merged_metadata = replace(
            base.metadata,
            updated_at=latest_update,
            confidence=max(memory.metadata.confidence for memory in sorted_group),
            importance=max(memory.metadata.importance for memory in sorted_group),
            tags=merged_tags,
            relationships=tuple(relationships.values()),
            version=max(memory.metadata.version for memory in sorted_group) + 1,
            lineage=merged_lineage,
            access_count=merged_access_count,
            user_feedback=merged_feedback,
        )
        return replace(base, metadata=merged_metadata)


class DefaultForgettingEngine:
    def evaluate(self, memory: MemoryRecord, policy: MemoryPolicy, now: datetime) -> ForgetDecision:
        if memory.retention_until is not None and now < memory.retention_until:
            return ForgetDecision(reason="record_retention_lock")

        if policy.legal_retention is not None:
            if memory.metadata.created_at + policy.legal_retention > now:
                return ForgetDecision(reason="legal_retention")

        if memory.is_expired(now=now):
            return ForgetDecision(archive=True, reason="expired")

        age_days = max((now - memory.metadata.updated_at).total_seconds() / 86_400, 0.0)
        decayed_confidence = memory.metadata.confidence - (policy.confidence_decay_rate * age_days)
        decayed_relevance = memory.metadata.importance - (policy.relevance_decay_rate * age_days)

        if (
            policy.archive_after is not None
            and memory.metadata.created_at + policy.archive_after <= now
        ):
            if policy.allow_manual_deletion and policy.allow_permanent_deletion:
                if decayed_confidence <= 0 and decayed_relevance <= 0:
                    return ForgetDecision(delete=True, reason="fully_decayed")
            return ForgetDecision(archive=True, reason="archive_window_reached")

        if decayed_confidence <= 0:
            return ForgetDecision(archive=True, reason="confidence_decay")
        return ForgetDecision(reason="retained")


class DefaultMemoryPolicyEngine:
    def __init__(self, *, default_policy: MemoryPolicy | None = None) -> None:
        self._default_policy = default_policy or MemoryPolicy(policy_id="default", name="default")
        self._workspace_policies: dict[str, MemoryPolicy] = {}
        self._project_policies: dict[str, MemoryPolicy] = {}
        self._agent_policies: dict[str, MemoryPolicy] = {}
        self._enterprise_policy: MemoryPolicy | None = None
        self._temporary_policy: MemoryPolicy | None = None

    def set_workspace_policy(self, workspace_id: str, policy: MemoryPolicy) -> None:
        self._workspace_policies[workspace_id] = policy

    def set_project_policy(self, project_id: str, policy: MemoryPolicy) -> None:
        self._project_policies[project_id] = policy

    def set_agent_policy(self, agent_id: str, policy: MemoryPolicy) -> None:
        self._agent_policies[agent_id] = policy

    def set_enterprise_policy(self, policy: MemoryPolicy) -> None:
        self._enterprise_policy = policy

    def set_temporary_session_policy(self, policy: MemoryPolicy) -> None:
        self._temporary_policy = policy

    def resolve(self, scope: PolicyScope) -> MemoryPolicy:
        if scope.is_temporary_session and self._temporary_policy is not None:
            return self._temporary_policy
        if scope.agent_id is not None and scope.agent_id in self._agent_policies:
            return self._agent_policies[scope.agent_id]
        if scope.project_id is not None and scope.project_id in self._project_policies:
            return self._project_policies[scope.project_id]
        if scope.workspace_id is not None and scope.workspace_id in self._workspace_policies:
            return self._workspace_policies[scope.workspace_id]
        if scope.is_enterprise and self._enterprise_policy is not None:
            return self._enterprise_policy
        return self._default_policy


class DefaultTimelineEngine:
    def build(self, memories: tuple[MemoryRecord, ...]) -> tuple[TimelineEvent, ...]:
        timeline = [
            TimelineEvent(
                identifier=memory.metadata.identifier,
                occurred_at=memory.event_time or memory.metadata.created_at,
                memory_type=memory.memory_type,
                summary=memory.content[:140],
                project_id=memory.project_id,
                conversation_id=memory.conversation_id,
            )
            for memory in memories
        ]
        return tuple(sorted(timeline, key=lambda event: event.occurred_at))


def utc_now() -> datetime:
    return datetime.now(UTC)
