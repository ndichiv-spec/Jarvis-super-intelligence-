from jarvis_intelligence.cognition import CognitionEngine, CognitionState


class TestCognitionEngine:
    def test_process_build_goal(self):
        engine = CognitionEngine()
        state = engine.process("Build a scalable authentication platform")
        assert isinstance(state, CognitionState)
        assert "build" in state.understanding.lower()
        assert state.intent == "build_and_implement"
        assert state.complexity == "simple"
        assert "platform" in state.key_entities
        assert state.confidence > 0

    def test_process_design_goal(self):
        engine = CognitionEngine()
        state = engine.process("Design the system architecture")
        assert state.intent == "design_and_plan"

    def test_process_deploy_goal(self):
        engine = CognitionEngine()
        state = engine.process("Deploy the application to production")
        assert state.intent == "deploy_and_release"

    def test_process_test_goal(self):
        engine = CognitionEngine()
        state = engine.process("Test all API endpoints")
        assert state.intent == "test_and_validate"

    def test_process_analyze_goal(self):
        engine = CognitionEngine()
        state = engine.process("Analyze the performance data")
        assert state.intent == "analyze_and_research"

    def test_process_optimize_goal(self):
        engine = CognitionEngine()
        state = engine.process("Refactor the database queries")
        assert state.intent == "optimize_and_improve"

    def test_process_generic_goal(self):
        engine = CognitionEngine()
        state = engine.process("Run the report")
        assert state.intent == "general_execution"

    def test_assess_complexity_simple(self):
        engine = CognitionEngine()
        state = engine.process("Fix bug")
        assert state.complexity == "simple"

    def test_assess_complexity_complex(self):
        engine = CognitionEngine()
        state = engine.process(
            "Design, build, test, document, and deploy a complete inventory management platform "
            "with authentication, reporting, and analytics capabilities"
        )
        assert state.complexity == "complex"

    def test_extract_entities_multiple(self):
        engine = CognitionEngine()
        state = engine.process("Build a dashboard with an API backend and database integration")
        assert "dashboard" in state.key_entities
        assert "api" in state.key_entities
        assert "database" in state.key_entities

    def test_identify_constraints_with_context(self):
        engine = CognitionEngine()
        state = engine.process("Build app", {"deadline": "2026-08-01", "budget": "$10k"})
        assert any("Deadline" in c for c in state.constraints_identified)
        assert any("Budget" in c for c in state.constraints_identified)

    def test_identify_constraints_no_context(self):
        engine = CognitionEngine()
        state = engine.process("Build app")
        assert state.constraints_identified == []
