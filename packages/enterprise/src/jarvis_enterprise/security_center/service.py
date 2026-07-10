"""Enterprise security center service."""

from __future__ import annotations

from uuid import UUID

from jarvis_enterprise.security_center.models import (
    AccessReviewSummary,
    IncidentReport,
    IncidentSeverity,
    IncidentStatus,
    RiskLevel,
    RiskReport,
    SecurityDashboard,
    SecurityPolicy,
)


class SecurityCenterService:
    def __init__(self) -> None:
        self._policies: dict[UUID, SecurityPolicy] = {}
        self._incidents: dict[UUID, IncidentReport] = {}
        self._risks: dict[UUID, RiskReport] = {}

    def create_security_policy(self, org_id: UUID, name: str, description: str = "") -> SecurityPolicy:
        policy = SecurityPolicy(org_id=org_id, name=name, description=description)
        self._policies[policy.id] = policy
        return policy

    def list_security_policies(self, org_id: UUID) -> list[SecurityPolicy]:
        return [p for p in self._policies.values() if p.org_id == org_id]

    def report_incident(
        self, org_id: UUID, title: str, description: str,
        severity: IncidentSeverity = IncidentSeverity.medium,
        reported_by: str = "",
    ) -> IncidentReport:
        incident = IncidentReport(
            org_id=org_id, title=title, description=description,
            severity=severity, reported_by=reported_by,
        )
        self._incidents[incident.id] = incident
        return incident

    def resolve_incident(self, incident_id: UUID, resolution: str) -> IncidentReport | None:
        incident = self._incidents.get(incident_id)
        if incident is None:
            return None
        updated = IncidentReport(
            id=incident.id, org_id=incident.org_id, title=incident.title,
            description=incident.description, severity=incident.severity,
            status=IncidentStatus.resolved, reported_by=incident.reported_by,
            assigned_to=incident.assigned_to, resolution=resolution,
            created_at=incident.created_at,
        )
        self._incidents[incident_id] = updated
        return updated

    def list_incidents(self, org_id: UUID) -> list[IncidentReport]:
        return [i for i in self._incidents.values() if i.org_id == org_id]

    def create_risk_report(self, org_id: UUID, title: str, description: str, risk_level: RiskLevel) -> RiskReport:
        report = RiskReport(org_id=org_id, title=title, description=description, risk_level=risk_level)
        self._risks[report.id] = report
        return report

    def list_risk_reports(self, org_id: UUID) -> list[RiskReport]:
        return [r for r in self._risks.values() if r.org_id == org_id]

    def get_dashboard(self, org_id: UUID) -> SecurityDashboard:
        incidents = self.list_incidents(org_id)
        return SecurityDashboard(
            org_id=org_id,
            total_incidents=len(incidents),
            open_incidents=sum(1 for i in incidents if i.status == IncidentStatus.open),
            critical_incidents=sum(1 for i in incidents if i.severity == IncidentSeverity.critical),
            resolved_incidents=sum(1 for i in incidents if i.status == IncidentStatus.resolved),
        )
