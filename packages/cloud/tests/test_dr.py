"""Tests for Disaster Recovery."""

from jarvis_cloud.dr.plan import DisasterRecovery, DrTier, DR_PLANS


class TestDisasterRecovery:
    def test_default_tier(self):
        dr = DisasterRecovery()
        assert dr.plan.tier == DrTier.gold

    def test_gold_rpo_rto(self):
        plan = DR_PLANS[DrTier.gold]
        assert plan.objectives.rpo_minutes == 60
        assert plan.objectives.rto_minutes == 30

    def test_platinum_rpo_rto(self):
        plan = DR_PLANS[DrTier.platinum]
        assert plan.objectives.rpo_minutes == 5
        assert plan.objectives.rto_minutes == 5

    def test_runbooks(self):
        dr = DisasterRecovery()
        runbooks = dr.get_runbooks()
        assert len(runbooks) == 4

    def test_recovery_steps_region_failure(self):
        dr = DisasterRecovery()
        steps = dr.get_recovery_steps("region_failure")
        assert len(steps) > 0

    def test_recovery_steps_data_corruption(self):
        dr = DisasterRecovery()
        steps = dr.get_recovery_steps("data_corruption")
        assert len(steps) > 0

    def test_recovery_steps_unknown(self):
        dr = DisasterRecovery()
        steps = dr.get_recovery_steps("unknown_scenario")
        assert "No predefined steps" in steps[0]

    def test_validate_gold(self):
        dr = DisasterRecovery(DrTier.gold)
        issues = dr.validate()
        assert len(issues) == 0

    def test_validate_platinum(self):
        dr = DisasterRecovery(DrTier.platinum)
        issues = dr.validate()
        assert len(issues) == 0

    def test_bronze_rpo_rto(self):
        plan = DR_PLANS[DrTier.bronze]
        assert plan.objectives.rpo_minutes == 1440
        assert plan.objectives.rto_minutes == 480
