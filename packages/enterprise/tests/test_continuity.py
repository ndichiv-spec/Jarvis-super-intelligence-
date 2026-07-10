"""Tests for Business Continuity."""

from uuid import uuid4

from jarvis_enterprise.continuity.models import (
    BackupValidation,
    IncidentResponsePlan,
    IncidentResponsePhase,
    RecoveryProcedure,
    Runbook,
    RunbookCategory,
)
from jarvis_enterprise.continuity.service import BusinessContinuityService


class TestContinuityService:
    def setup_method(self):
        self.repo = BusinessContinuityService()

    def test_create_runbook(self):
        runbook = self.repo.create_runbook("Backup Procedure", RunbookCategory.backup, "Steps to backup", ("Step 1", "Step 2"), "ops-team")
        assert runbook.title == "Backup Procedure"
        assert len(runbook.steps) == 2

    def test_list_runbooks(self):
        self.repo.create_runbook("Backup", RunbookCategory.backup)
        self.repo.create_runbook("Recovery", RunbookCategory.recovery)
        assert len(self.repo.list_runbooks()) == 2
        assert len(self.repo.list_runbooks(RunbookCategory.backup)) == 1

    def test_create_incident_plan(self):
        plan = self.repo.create_incident_plan("Data Breach Plan", "Response plan for breaches", "critical", ("sec-team",))
        assert plan.severity == "critical"
        assert len(plan.phases) > 0

    def test_create_recovery_procedure(self):
        proc = self.repo.create_recovery_procedure("DB Recovery", "postgres", ("Stop app", "Restore dump", "Verify"), 30, 15)
        assert proc.estimated_rto_minutes == 30
        assert proc.estimated_rpo_minutes == 15

    def test_verify_recovery_procedure(self):
        proc = self.repo.create_recovery_procedure("DB Recovery", "postgres")
        verified = self.repo.verify_recovery_procedure(proc.id)
        assert verified is not None
        assert verified.verified is True
        assert verified.last_tested is not None

    def test_verify_nonexistent_procedure(self):
        result = self.repo.verify_recovery_procedure(uuid4())
        assert result is None

    def test_record_backup_validation(self):
        validation = self.repo.record_backup_validation("daily-db-backup", True, 1024, "abc123")
        assert validation.backup_name == "daily-db-backup"
        assert validation.validated is True

    def test_list_backup_validations(self):
        self.repo.record_backup_validation("backup-1", True)
        self.repo.record_backup_validation("backup-2", False)
        assert len(self.repo.list_backup_validations()) == 2
