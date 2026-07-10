"""Tests for High Availability Design."""

from jarvis_cloud.ha.design import HighAvailabilityDesign, PRODUCTION_HA, UpdateStrategy, FailoverStrategy


class TestHighAvailabilityDesign:
    def test_default_values(self):
        ha = HighAvailabilityDesign()
        assert ha.update_strategy == UpdateStrategy.rolling
        assert ha.redundancy.failover_strategy == FailoverStrategy.active_active
        assert ha.redundancy.availability_zones == 3

    def test_production_values(self):
        assert PRODUCTION_HA.update_strategy == UpdateStrategy.blue_green
        assert PRODUCTION_HA.blue_green is not None
        assert PRODUCTION_HA.blue_green.auto_promote_seconds == 300

    def test_pdb_config(self):
        ha = HighAvailabilityDesign()
        assert ha.pod_disruption_budget_min_available == 1

    def test_production_pdb(self):
        assert PRODUCTION_HA.pod_disruption_budget_min_available == "50%"

    def test_anti_affinity(self):
        ha = HighAvailabilityDesign()
        assert ha.anti_affinity is True

    def test_production_redundancy(self):
        assert PRODUCTION_HA.redundancy.replicas_per_az == 2
        assert PRODUCTION_HA.redundancy.availability_zones == 3
