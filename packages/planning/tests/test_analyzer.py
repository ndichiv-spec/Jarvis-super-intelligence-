from jarvis_planning.analyzer import Goal, GoalAnalyzer
from jarvis_planning.estimator import Complexity


class TestGoal:
    def test_goal_creation(self) -> None:
        g = Goal(objective="Build an accounting application")
        assert g.objective == "Build an accounting application"
        assert g.complexity == Complexity.MODERATE
        assert g.risk_level == "low"
        assert g.ambiguity == []
        assert g.confidence == 0.0

    def test_goal_to_dict(self) -> None:
        g = Goal(objective="Test", category="web")
        d = g.to_dict()
        assert d["objective"] == "Test"
        assert d["category"] == "web"
        assert d["complexity"] == "moderate"


class TestGoalAnalyzer:
    def test_analyze_detects_category(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build a web portal for managing inventory")
        assert goal.category == "web"
        assert goal.complexity is not None
        assert goal.estimated_duration

    def test_analyze_mobile_app(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Create a cross-platform mobile solution for iOS and Android users")
        assert goal.category == "mobile"

    def test_analyze_data_pipeline(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build a data pipeline for analytics reporting")
        assert goal.category == "data"

    def test_analyze_ai_project(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Develop an AI machine learning model for predictions")
        assert goal.category == "ai-ml"

    def test_analyze_detects_ambiguity(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build something")
        assert len(goal.ambiguity) > 0
        assert "vague" in goal.ambiguity

    def test_analyze_clear_objective_no_ambiguity(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Develop a professional inventory management platform for retail stores")
        assert len(goal.ambiguity) == 0

    def test_analyze_suggests_knowledge(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build a web application")
        assert len(goal.required_knowledge) > 0

    def test_analyze_suggests_constraints(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build an application")
        assert len(goal.constraints) > 0

    def test_analyze_suggests_deliverables(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build a web application")
        assert "source_code" in goal.deliverables

    def test_analyze_general_category(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Do some work")
        assert goal.category == "general"

    def test_with_estimate(self) -> None:
        analyzer = GoalAnalyzer()
        goal = analyzer.analyze("Build a complex enterprise platform with microservices")
        assert goal.estimate is not None
        assert goal.estimate.complexity in (
            Complexity.COMPLEX, Complexity.VERY_COMPLEX
        )
