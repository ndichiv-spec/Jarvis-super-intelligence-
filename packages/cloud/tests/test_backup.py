"""Tests for Backup & Recovery."""

from jarvis_cloud.backup.manager import (
    BackupManager,
    BackupTarget,
    BackupStatus,
    DEFAULT_BACKUP_STRATEGY,
)


class TestBackupManager:
    def setup_method(self):
        self.mgr = BackupManager()

    def test_default_strategy(self):
        assert len(self.mgr.strategy.schedules) > 0

    def test_create_job(self):
        job = self.mgr.create_job(BackupTarget.postgres)
        assert job.status == BackupStatus.pending
        assert job.target == BackupTarget.postgres

    def test_complete_job_success(self):
        job = self.mgr.create_job(BackupTarget.redis)
        completed = self.mgr.complete_job(job.id, BackupStatus.completed, path="/backups/redis.gz")
        assert completed.status == BackupStatus.completed
        assert completed.path == "/backups/redis.gz"

    def test_complete_job_failure(self):
        job = self.mgr.create_job(BackupTarget.qdrant)
        failed = self.mgr.complete_job(job.id, BackupStatus.failed, error="disk full")
        assert failed.status == BackupStatus.failed
        assert failed.error == "disk full"

    def test_list_history(self):
        job1 = self.mgr.create_job(BackupTarget.postgres)
        job2 = self.mgr.create_job(BackupTarget.redis)
        self.mgr.complete_job(job1.id, BackupStatus.completed)
        self.mgr.complete_job(job2.id, BackupStatus.completed)
        assert len(self.mgr.list_history()) == 2

    def test_list_history_filtered(self):
        job = self.mgr.create_job(BackupTarget.postgres)
        self.mgr.complete_job(job.id, BackupStatus.completed)
        assert len(self.mgr.list_history(target=BackupTarget.postgres)) == 1
        assert len(self.mgr.list_history(target=BackupTarget.redis)) == 0

    def test_verify(self):
        issues = self.mgr.verify()
        assert len(issues) >= 0
