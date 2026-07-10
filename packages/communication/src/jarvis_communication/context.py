from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any
from uuid import uuid4


def _freeze_mapping(values: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(values))


@dataclass(frozen=True, slots=True)
class SecurityContext:
    principal_id: str
    roles: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkspaceContext:
    workspace_id: str
    tenant_id: str | None = None
    environment: str = "default"


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    correlation_id: str
    request_id: str
    execution_id: str
    parent_execution_id: str | None
    source: str
    timestamp: datetime
    security_context: SecurityContext | None = None
    workspace_context: WorkspaceContext | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.correlation_id:
            raise ValueError("correlation_id must not be empty")
        if not self.request_id:
            raise ValueError("request_id must not be empty")
        if not self.execution_id:
            raise ValueError("execution_id must not be empty")
        if not self.source:
            raise ValueError("source must not be empty")
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def new(
        cls,
        source: str,
        *,
        security_context: SecurityContext | None = None,
        workspace_context: WorkspaceContext | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ExecutionContext:
        correlation_id = uuid4().hex
        request_id = uuid4().hex
        execution_id = uuid4().hex
        return cls(
            correlation_id=correlation_id,
            request_id=request_id,
            execution_id=execution_id,
            parent_execution_id=None,
            source=source,
            timestamp=datetime.now(UTC),
            security_context=security_context,
            workspace_context=workspace_context,
            metadata=metadata or {},
        )

    def child(
        self,
        source: str,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> ExecutionContext:
        merged_metadata = dict(self.metadata)
        if metadata:
            merged_metadata.update(metadata)
        return ExecutionContext(
            correlation_id=self.correlation_id,
            request_id=self.request_id,
            execution_id=uuid4().hex,
            parent_execution_id=self.execution_id,
            source=source,
            timestamp=datetime.now(UTC),
            security_context=self.security_context,
            workspace_context=self.workspace_context,
            metadata=merged_metadata,
        )
