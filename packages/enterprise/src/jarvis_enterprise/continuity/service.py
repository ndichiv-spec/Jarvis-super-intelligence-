"""Business continuity service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from jarvis_enterprise.continuity.models import (
    BackupValidation,
    IncidentResponsePlan,
    IncidentResponsePhase,
    RecoveryProcedure,
    Runbook,
    RunbookCategory,
)


class BusinessContinuityService:
    def __init__(self) -> None:
        self._runbooks: dict[UUID, Runbook] = {}
        self._incident_plans: dict[UUID, IncidentResponsePlan] = {}
        self._recovery_procedures: dict[UUID, RecoveryProcedure] = {}
        self._backup_validations: dict[UUID, BackupValidation] = {}

    def create_runbook(
        self, title: str, category: RunbookCategory = RunbookCategory.maintenance,
        description: str = "", steps: tuple[str, ...] = (), owner: str = "",
    ) -> Runbook:
        runbook = Runbook(title=title, category=category, description=description, steps=steps, owner=owner)
        self._runbooks[runbook.id] = runbook
        return runbook

    def list_runbooks(self, category: RunbookCategory | None = None) -> list[Runbook]:
        if category:
            return [r for r in self._runbooks.values() if r.category == category]
        return list(self._runbooks.values())

    def create_incident_plan(
        self, name: str, description: str = "",
        severity: str = "medium", owners: tuple[str, ...] = (),
    ) -> IncidentResponsePlan:
        plan = IncidentResponsePlan(
            name=name, description=description, severity=severity,
            phases=tuple(IncidentResponsePhase),
            owners=owners,
        )
        self._incident_plans[plan.id] = plan
        return plan

    def list_incident_plans(self) -> list[IncidentResponsePlan]:
        return list(self._incident_plans.values())

    def create_recovery_procedure(
        self, name: str, target: str = "",
        steps: tuple[str, ...] = (),
        estimated_rto_minutes: int = 60,
        estimated_rpo_minutes: int = 60,
    ) -> RecoveryProcedure:
        procedure = RecoveryProcedure(
            name=name, target=target, steps=steps,
            estimated_rto_minutes=estimated_rto_minutes,
            estimated_rpo_minutes=estimated_rpo_minutes,
        )
        self._recovery_procedures[procedure.id] = procedure
        return procedure

    def verify_recovery_procedure(self, procedure_id: UUID) -> RecoveryProcedure | None:
        procedure = self._recovery_procedures.get(procedure_id)
        if procedure is None:
            return None
        updated = RecoveryProcedure(
            id=procedure.id, name=procedure.name, target=procedure.target,
            steps=procedure.steps, estimated_rto_minutes=procedure.estimated_rto_minutes,
            estimated_rpo_minutes=procedure.estimated_rpo_minutes,
            verified=True, last_tested=datetime.now(timezone.utc),
        )
        self._recovery_procedures[procedure_id] = updated
        return updated

    def list_recovery_procedures(self) -> list[RecoveryProcedure]:
        return list(self._recovery_procedures.values())

    def record_backup_validation(self, backup_name: str, validated: bool, size_bytes: int = 0, checksum: str = "") -> BackupValidation:
        validation = BackupValidation(
            backup_name=backup_name, validated=validated,
            size_bytes=size_bytes, checksum=checksum,
        )
        self._backup_validations[validation.id] = validation
        return validation

    def list_backup_validations(self) -> list[BackupValidation]:
        return list(self._backup_validations.values())
