"""Tests for registry."""

from __future__ import annotations

import pytest

from app.health import HealthStatus
from app.registry import ServiceHandle, ServiceRegistry, ServiceStatus


class TestServiceHandle:
    def test_create_minimal(self) -> None:
        h = ServiceHandle(id="test", name="Test Service", version="1.0")
        assert h.id == "test"
        assert h.name == "Test Service"
        assert h.version == "1.0"
        assert h.dependencies == ()
        assert h.capabilities == ()

    def test_create_full(self) -> None:
        h = ServiceHandle(
            id="full",
            name="Full Service",
            version="2.0",
            dependencies=("a", "b"),
            capabilities=("x", "y"),
        )
        assert h.dependencies == ("a", "b")
        assert h.capabilities == ("x", "y")

    def test_default_status(self) -> None:
        h = ServiceHandle(id="s", name="S", version="1")
        assert h.status == ServiceStatus.registered

    def test_default_health(self) -> None:
        h = ServiceHandle(id="s", name="S", version="1")
        assert h.health == HealthStatus.unknown


class TestServiceRegistry:
    def test_register(self) -> None:
        r = ServiceRegistry()
        h = ServiceHandle(id="s1", name="Service 1", version="1.0")
        r.register(h)
        assert r.count() == 1

    def test_register_duplicate_raises(self) -> None:
        r = ServiceRegistry()
        h = ServiceHandle(id="s1", name="Service 1", version="1.0")
        r.register(h)
        with pytest.raises(ValueError, match="already registered"):
            r.register(h)

    def test_get(self) -> None:
        r = ServiceRegistry()
        h = ServiceHandle(id="s1", name="Service 1", version="1.0")
        r.register(h)
        got = r.get("s1")
        assert got is not None
        assert got.id == "s1"

    def test_get_missing(self) -> None:
        r = ServiceRegistry()
        assert r.get("nonexistent") is None

    def test_list(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1"))
        r.register(ServiceHandle(id="b", name="B", version="1"))
        lst = r.list()
        assert len(lst) == 2

    def test_update_status(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="s", name="S", version="1"))
        r.update_status("s", ServiceStatus.running)
        assert r.get("s").status == ServiceStatus.running

    def test_update_status_nonexistent_raises(self) -> None:
        r = ServiceRegistry()
        with pytest.raises(ValueError, match="not found"):
            r.update_status("x", ServiceStatus.running)

    def test_resolve_startup_order_no_deps(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1"))
        r.register(ServiceHandle(id="b", name="B", version="1"))
        order = r.resolve_startup_order()
        assert set(order) == {"a", "b"}

    def test_resolve_startup_order_with_deps(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1", dependencies=()))
        r.register(ServiceHandle(id="b", name="B", version="1", dependencies=("a",)))
        order = r.resolve_startup_order()
        assert order.index("a") < order.index("b")

    def test_resolve_startup_order_unknown_dep_warning(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="b", name="B", version="1", dependencies=("a",)))
        order = r.resolve_startup_order()
        assert "b" in order

    def test_resolve_startup_order_circular(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1", dependencies=("b",)))
        r.register(ServiceHandle(id="b", name="B", version="1", dependencies=("a",)))
        with pytest.raises(ValueError, match="Circular"):
            r.resolve_startup_order()

    def test_get_dependency_graph(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1", dependencies=()))
        r.register(ServiceHandle(id="b", name="B", version="1", dependencies=("a",)))
        graph = r.get_dependency_graph()
        assert "a" in graph
        assert "b" in graph
        assert graph["a"] == []
        assert graph["b"] == ["a"]

    def test_count_empty(self) -> None:
        r = ServiceRegistry()
        assert r.count() == 0

    def test_count_after_register(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1"))
        assert r.count() == 1

    def test_resolve_chain_deps(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="a", name="A", version="1"))
        r.register(ServiceHandle(id="b", name="B", version="1", dependencies=("a",)))
        r.register(ServiceHandle(id="c", name="C", version="1", dependencies=("b",)))
        order = r.resolve_startup_order()
        idx = {s: i for i, s in enumerate(order)}
        assert idx["a"] < idx["b"] < idx["c"]

    def test_update_health(self) -> None:
        r = ServiceRegistry()
        r.register(ServiceHandle(id="s", name="S", version="1"))
        r.update_health("s", HealthStatus.ready)
        assert r.get("s").health == HealthStatus.ready

    def test_update_health_nonexistent(self) -> None:
        r = ServiceRegistry()
        result = r.update_health("x", HealthStatus.ready)
        assert result is None
