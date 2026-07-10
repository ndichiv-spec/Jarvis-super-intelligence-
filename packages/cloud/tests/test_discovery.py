"""Tests for Service Discovery."""

from jarvis_cloud.discovery.registry import (
    InMemoryServiceRegistry,
    DnsServiceRegistry,
    ServiceRegistry,
    ServiceHealth,
    ServiceInstance,
)


class TestInMemoryServiceRegistry:
    def setup_method(self):
        self.registry = InMemoryServiceRegistry()

    def _make_instance(self, service, instance_id, host, port, **kw):
        return ServiceInstance(service_name=service, instance_id=instance_id, host=host, port=port, **kw)

    def test_register_and_resolve(self):
        self.registry.register(self._make_instance("api", "i1", "10.0.0.1", 8000))
        endpoints = self.registry.resolve("api")
        assert len(endpoints) == 1
        assert endpoints[0].url == "http://10.0.0.1:8000"

    def test_deregister(self):
        self.registry.register(self._make_instance("api", "i1", "10.0.0.1", 8000))
        self.registry.deregister("api", "i1")
        assert len(self.registry.resolve("api")) == 0

    def test_resolve_one(self):
        self.registry.register(self._make_instance("api", "i1", "10.0.0.1", 8000))
        ep = self.registry.resolve_one("api")
        assert ep is not None
        assert ep.url == "http://10.0.0.1:8000"

    def test_resolve_one_none(self):
        ep = self.registry.resolve_one("nonexistent")
        assert ep is None

    def test_list_services(self):
        self.registry.register(self._make_instance("api", "i1", "10.0.0.1", 8000))
        self.registry.register(self._make_instance("brain", "i2", "10.0.0.2", 8100))
        services = self.registry.list_services()
        assert "api" in services
        assert "brain" in services

    def test_health_unhealthy_excluded(self):
        from jarvis_cloud.discovery.registry import ServiceInstance
        from datetime import datetime, timezone
        self.registry.register(ServiceInstance("api", "i1", "10.0.0.1", 8000, health=ServiceHealth.unhealthy))
        assert len(self.registry.resolve("api")) == 0

    def test_multiple_instances(self):
        self.registry.register(self._make_instance("api", "i1", "10.0.0.1", 8000))
        self.registry.register(self._make_instance("api", "i2", "10.0.0.2", 8000))
        assert len(self.registry.resolve("api")) == 2


class TestDnsServiceRegistry:
    def setup_method(self):
        self.registry = DnsServiceRegistry(domain="jarvis.svc.cluster.local")

    def test_register_and_resolve(self):
        instance = ServiceInstance("api", "i1", "api.jarvis.svc.cluster.local", 8000)
        self.registry.register(instance)
        endpoints = self.registry.resolve("api")
        assert len(endpoints) > 0

    def test_resolve_without_register(self):
        endpoints = self.registry.resolve("api")
        assert len(endpoints) == 1
        assert "api.jarvis.svc.cluster.local" in endpoints[0].url


class TestServiceRegistry:
    def test_backend_default(self):
        registry = ServiceRegistry()
        assert registry.backend is not None
        assert isinstance(registry.backend, InMemoryServiceRegistry)

    def test_register_and_resolve_url(self):
        registry = ServiceRegistry()
        registry.register("api", "i1", "10.0.0.1", 8000)
        url = registry.resolve_url("api")
        assert url == "http://10.0.0.1:8000"

    def test_resolve_url_none(self):
        registry = ServiceRegistry()
        url = registry.resolve_url("nonexistent")
        assert url is None
