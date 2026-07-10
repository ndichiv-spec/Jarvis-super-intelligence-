"""Tests for Operations Dashboard."""

from jarvis_cloud.dashboard.operations import OperationsDashboard, ServiceStatus


class TestOperationsDashboard:
    def setup_method(self):
        self.dash = OperationsDashboard()

    def test_initial_state(self):
        assert len(self.dash.state.services) == 0
        assert len(self.dash.state.alerts) == 0

    def test_update_service_health(self):
        self.dash.update_service_health("api", ServiceStatus.running, 3, 3)
        assert "api" in self.dash.state.services
        assert self.dash.state.services["api"].status == ServiceStatus.running

    def test_add_deployment(self):
        self.dash.add_deployment("production", "1.0.0", 8, 8)
        assert len(self.dash.state.deployments) == 1

    def test_add_alert(self):
        self.dash.add_alert("critical", "API Down", "API service is unreachable")
        assert len(self.dash.state.alerts) == 1
        assert self.dash.state.alerts[0]["severity"] == "critical"

    def test_summary(self):
        self.dash.update_service_health("api", ServiceStatus.running, 3, 3)
        self.dash.update_service_health("brain", ServiceStatus.running, 3, 3)
        self.dash.add_alert("warning", "High memory", "Memory > 80%")
        summary = self.dash.summary()
        assert summary["services"]["total"] == 2
        assert summary["services"]["healthy"] == 2
        assert summary["active_alerts"] >= 0
