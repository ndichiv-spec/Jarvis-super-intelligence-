from jarvis_intelligence.decision import DecisionEngine, DecisionType


class TestDecisionEngine:
    def test_select_strategy_simple(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.SELECT_STRATEGY, {"complexity": "simple", "goal_id": "g1"})
        assert decision.type == DecisionType.SELECT_STRATEGY
        assert decision.confidence >= 0.8
        assert decision.target_id == "g1"

    def test_select_strategy_complex(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.SELECT_STRATEGY, {"complexity": "complex", "goal_id": "g2"})
        assert decision.confidence == 0.70
        assert decision.parameters["strategy"] == "hierarchical"

    def test_assign_agent_with_agents(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.ASSIGN_AGENT, {
            "required_capabilities": ["python"], "available_agents": ["agent-1", "agent-2"], "task_id": "t1",
        })
        assert decision.type == DecisionType.ASSIGN_AGENT
        assert decision.confidence == 0.75

    def test_assign_agent_no_agents(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.ASSIGN_AGENT, {
            "required_capabilities": ["python"], "available_agents": [], "task_id": "t2",
        })
        assert decision.confidence == 0.40
        assert len(decision.risks) > 0

    def test_execute_task_ready(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.EXECUTE_TASK, {"task_id": "t1", "task_ready": True})
        assert decision.confidence == 0.90

    def test_execute_task_not_ready(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.EXECUTE_TASK, {"task_id": "t1", "task_ready": False})
        assert decision.confidence == 0.30

    def test_retry_task_can_retry(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.RETRY_TASK, {"task_id": "t1", "retry_count": 1, "max_retries": 3})
        assert decision.confidence == 0.60
        assert "2/3" in decision.reasoning

    def test_retry_task_max_reached(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.RETRY_TASK, {"task_id": "t1", "retry_count": 3, "max_retries": 3})
        assert decision.confidence == 0.10

    def test_replan_with_failures(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.REPLAN, {"plan_id": "p1", "failure_count": 2})
        assert decision.confidence == 0.65

    def test_replan_no_failures(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.REPLAN, {"plan_id": "p1", "failure_count": 0})
        assert decision.confidence == 0.20

    def test_unknown_decision_type_falls_to_default(self):
        engine = DecisionEngine()
        decision = engine.decide(DecisionType.CANCEL_GOAL, {"goal_id": "g1"})
        assert decision.confidence == 0.50

    def test_get_history(self):
        engine = DecisionEngine()
        assert engine.get_history() == []
        engine.decide(DecisionType.SELECT_STRATEGY, {"complexity": "simple"})
        engine.decide(DecisionType.EXECUTE_TASK, {"task_id": "t1", "task_ready": True})
        assert len(engine.get_history()) == 2
