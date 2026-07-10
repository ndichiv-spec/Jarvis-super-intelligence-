from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from jarvis_security.audit import AuditEvent, AuditEventType, AuditField, InMemoryAuditSink
from jarvis_security.metadata import SecurityMetadata, SecurityObjectType, SecurityStatus

logger = logging.getLogger(__name__)

DESKTOP_EVENT_TYPE_MAP: dict[str, AuditEventType] = {
    "file.open": AuditEventType.TOOL_USAGE,
    "file.save": AuditEventType.TOOL_USAGE,
    "file.import": AuditEventType.TOOL_USAGE,
    "file.export": AuditEventType.TOOL_USAGE,
    "permission.requested": AuditEventType.AUTHORIZATION,
    "permission.granted": AuditEventType.AUTHORIZATION,
    "permission.denied": AuditEventType.AUTHORIZATION,
    "permission.revoked": AuditEventType.AUTHORIZATION,
    "sync.start": AuditEventType.WORKFLOW_EXECUTION,
    "sync.complete": AuditEventType.WORKFLOW_EXECUTION,
    "sync.conflict": AuditEventType.WORKFLOW_EXECUTION,
    "notification.send": AuditEventType.AGENT_ACTIVITY,
    "notification.read": AuditEventType.AGENT_ACTIVITY,
    "clipboard.read": AuditEventType.TOOL_USAGE,
    "clipboard.write": AuditEventType.TOOL_USAGE,
    "integration.launch": AuditEventType.EXTENSION_LIFECYCLE,
    "integration.close": AuditEventType.EXTENSION_LIFECYCLE,
    "settings.change": AuditEventType.CONFIGURATION_CHANGE,
    "update.check": AuditEventType.CONFIGURATION_CHANGE,
    "update.apply": AuditEventType.CONFIGURATION_CHANGE,
    "offline.toggle": AuditEventType.CONFIGURATION_CHANGE,
    "offline.sync": AuditEventType.WORKFLOW_EXECUTION,
    "session.start": AuditEventType.AUTHENTICATION,
    "session.end": AuditEventType.AUTHENTICATION,
    "gateway.connect": AuditEventType.AUTHENTICATION,
    "gateway.disconnect": AuditEventType.AUTHENTICATION,
}


@dataclass(frozen=True)
class DesktopAuditEvent:
    id: str
    action: str
    module: str
    description: str
    success: bool
    timestamp: str
    permission: str | None = None
    resource: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class DesktopAuditBridge:
    def __init__(self, security_sink: InMemoryAuditSink | None = None) -> None:
        self._sink = security_sink or InMemoryAuditSink()
        self._desktop_events: list[DesktopAuditEvent] = []

    def record(
        self,
        action: str,
        module: str,
        description: str,
        success: bool,
        permission: str | None = None,
        resource: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> DesktopAuditEvent:
        event = DesktopAuditEvent(
            id=str(uuid4()),
            action=action,
            module=module,
            description=description,
            success=success,
            timestamp=datetime.now(UTC).isoformat(),
            permission=permission,
            resource=resource,
            details=details or {},
        )
        self._desktop_events.append(event)
        self._forward_to_security_platform(event)
        return event

    def _forward_to_security_platform(self, event: DesktopAuditEvent) -> None:
        audit_event_type = DESKTOP_EVENT_TYPE_MAP.get(event.action, AuditEventType.WORKFLOW_EXECUTION)

        details = [
            AuditField(key="action", value=event.action, field_type="string"),
            AuditField(key="module", value=event.module, field_type="string"),
            AuditField(key="desktop_event_id", value=event.id, field_type="string"),
        ]
        if event.permission:
            details.append(AuditField(key="permission", value=event.permission, field_type="string"))
        if event.resource:
            details.append(AuditField(key="resource", value=event.resource, field_type="string"))
        if event.details:
            import json
            details.append(AuditField(key="details", value=json.dumps(event.details), field_type="json"))

        security_event = AuditEvent(
            metadata=SecurityMetadata(
                object_id=event.id,
                object_type=SecurityObjectType.TOOL_EXECUTION,
                status=SecurityStatus.SUCCESS if event.success else SecurityStatus.FAILURE,
                domain="desktop",
            ),
            event_type=audit_event_type,
            actor_identifier="desktop-runtime",
            target_identifier=event.module,
            occurred_at=datetime.fromisoformat(event.timestamp),
            summary=event.description,
            details=tuple(details),
        )
        self._sink.record(security_event)

    def list_events(self) -> list[DesktopAuditEvent]:
        return list(self._desktop_events)

    def get_by_module(self, module: str) -> list[DesktopAuditEvent]:
        return [e for e in self._desktop_events if e.module == module]

    def get_by_action(self, action: str) -> list[DesktopAuditEvent]:
        return [e for e in self._desktop_events if e.action == action]

    @property
    def security_sink(self) -> InMemoryAuditSink:
        return self._sink
