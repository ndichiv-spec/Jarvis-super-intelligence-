"""Tests for Container Platform."""

from jarvis_cloud.container.platform import ContainerPlatform


class TestContainerPlatform:
    def test_list_services(self):
        platform = ContainerPlatform()
        services = platform.list_services()
        assert "api" in services
        assert "brain" in services
        assert "ai" in services
        assert "memory" in services
        assert "knowledge" in services
        assert "automation" in services
        assert "agents" in services
        assert "orchestration" in services

    def test_get_build_config(self):
        platform = ContainerPlatform()
        config = platform.get_build_config("api")
        assert config.service_name == "api"
        assert config.target == "production"

    def test_unknown_service(self):
        platform = ContainerPlatform()
        try:
            platform.get_build_config("nonexistent")
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_generate_dockerfile(self):
        platform = ContainerPlatform()
        dockerfile = platform.generate_dockerfile("api")
        assert "python:3.13-slim" in dockerfile
        assert "production" in dockerfile

    def test_generate_compose_service(self):
        platform = ContainerPlatform()
        svc = platform.generate_compose_service("api", "1.0.0")
        assert svc["image"] == "jarvis/api:1.0.0"
        assert "healthcheck" in svc
