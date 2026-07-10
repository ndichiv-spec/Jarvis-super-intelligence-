"""Tests for Deployment Manager."""

from jarvis_cloud.deployment.manager import DeploymentManager, DeploymentStatus
from jarvis_cloud.deployment.profiles import (
    DeploymentEnvironment,
    DeploymentProfile,
    ProfileLoader,
    ServiceProfile,
)


class TestDeploymentProfiles:
    def test_list_profiles(self):
        loader = ProfileLoader()
        profiles = loader.list_profiles()
        assert "development" in profiles
        assert "staging" in profiles
        assert "production" in profiles

    def test_load_development(self):
        loader = ProfileLoader()
        profile = loader.load("development")
        assert profile.environment == DeploymentEnvironment.development
        assert profile.name == "development"

    def test_load_production(self):
        loader = ProfileLoader()
        profile = loader.load("production")
        assert profile.environment == DeploymentEnvironment.production
        assert profile.name == "production"

    def test_unknown_profile(self):
        loader = ProfileLoader()
        try:
            loader.load("nonexistent")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_development_replicas(self):
        loader = ProfileLoader()
        profile = loader.load("development")
        for svc in profile.services.values():
            assert svc.replicas == 1

    def test_production_replicas(self):
        loader = ProfileLoader()
        profile = loader.load("production")
        for svc in profile.services.values():
            assert svc.replicas == 3

    def test_staging_replicas(self):
        loader = ProfileLoader()
        profile = loader.load("staging")
        for svc in profile.services.values():
            assert svc.replicas == 2

    def test_all_services_present(self):
        loader = ProfileLoader()
        profile = loader.load("production")
        expected = {"api", "brain", "ai", "memory", "knowledge", "automation", "agents", "orchestration"}
        assert set(profile.services.keys()) == expected

    def test_service_health_check(self):
        loader = ProfileLoader()
        profile = loader.load("production")
        for name, svc in profile.services.items():
            assert svc.health_check is not None, f"{name} missing health check"
            assert "path" in svc.health_check

    def test_service_ports(self):
        loader = ProfileLoader()
        profile = loader.load("production")
        for name, svc in profile.services.items():
            assert len(svc.ports) > 0, f"{name} has no ports"


class TestDeploymentManager:
    def test_plan(self):
        mgr = DeploymentManager()
        plan = mgr.plan("development", "latest")
        assert plan["profile"] == "development"
        assert plan["version"] == "latest"

    def test_deploy(self):
        mgr = DeploymentManager()
        record = mgr.deploy("development", "latest")
        assert record.status == DeploymentStatus.in_progress
        assert record.environment == DeploymentEnvironment.development

    def test_complete(self):
        mgr = DeploymentManager()
        record = mgr.deploy("production", "1.0.0")
        completed = mgr.complete(record.id, DeploymentStatus.completed)
        assert completed.status == DeploymentStatus.completed
        assert completed.completed_at is not None

    def test_rollback(self):
        mgr = DeploymentManager()
        record = mgr.deploy("staging", "1.0.0")
        rolled = mgr.rollback(record.id)
        assert rolled.status == DeploymentStatus.rolled_back

    def test_history(self):
        mgr = DeploymentManager()
        mgr.deploy("development", "v1")
        mgr.deploy("staging", "v2")
        assert len(mgr.history) == 2

    def test_list_deployments_by_env(self):
        mgr = DeploymentManager()
        mgr.deploy("development", "v1")
        mgr.deploy("production", "v2")
        dev = mgr.list_deployments("development")
        prod = mgr.list_deployments("production")
        assert len(dev) == 1
        assert len(prod) == 1

    def test_validate_valid_profile(self):
        mgr = DeploymentManager()
        issues = mgr.validate("development")
        assert len(issues) == 0

    def test_validate_invalid_profile(self):
        mgr = DeploymentManager()
        issues = mgr.validate("nonexistent")
        assert len(issues) > 0
