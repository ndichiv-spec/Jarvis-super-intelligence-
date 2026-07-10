from jarvis_planning.analyzer import Goal
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.decomposer import Task
from jarvis_planning.explanation import Explanation, ExplanationEngine, ExplanationSection
from jarvis_planning.reasoning import ReasoningEngine
from jarvis_planning.scheduler import Scheduler


class TestExplanationSection:
    def test_creation(self) -> None:
        s = ExplanationSection("Title", "Content", ["detail1"])
        assert s.title == "Title"
        assert s.content == "Content"

    def test_to_dict(self) -> None:
        s = ExplanationSection("T", "C", ["d1", "d2"])
        d = s.to_dict()
        assert d["title"] == "T"
        assert len(d["details"]) == 2


class TestExplanation:
    def test_add_section(self) -> None:
        e = Explanation()
        e.add_section("Title", "Content", ["detail"])
        assert len(e.sections) == 1

    def test_to_text(self) -> None:
        e = Explanation()
        e.add_section("Goal", "Build something")
        text = e.to_text()
        assert "Goal" in text
        assert "Build something" in text

    def test_to_dict(self) -> None:
        e = Explanation()
        e.add_section("Title", "Content")
        d = e.to_dict()
        assert len(d) == 1
        assert d[0]["title"] == "Title"


class TestExplanationEngine:
    def test_generate_goal_summary(self) -> None:
        engine = ExplanationEngine(ReasoningEngine())
        goal = Goal(objective="Build a web app", category="web", risk_level="low")
        exp = engine.generate_goal_summary(goal)
        assert len(exp.sections) >= 1
        assert any("Objective" in s.content for s in exp.sections)

    def test_generate_goal_summary_with_knowledge(self) -> None:
        engine = ExplanationEngine(ReasoningEngine())
        goal = Goal(objective="Test", required_knowledge=["backend_development"])
        exp = engine.generate_goal_summary(goal)
        assert any("Required Knowledge" in s.title for s in exp.sections)

    def test_generate_plan_summary(self) -> None:
        engine = ExplanationEngine(ReasoningEngine())
        goal = Goal(objective="Build a web app")
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="Task 1", description="", estimated_effort_hours=2.0))
        g.add_task(Task(id="t2", title="Task 2", description="", dependencies=["t1"], estimated_effort_hours=3.0))
        s = Scheduler(g)
        exp = engine.generate_plan_summary(goal, g, s)
        assert len(exp.sections) >= 3

    def test_generate_completion_summary(self) -> None:
        from jarvis_planning.events import EventBus
        from jarvis_planning.executor import Executor

        engine = ExplanationEngine(ReasoningEngine())
        goal = Goal(objective="Build a web app")
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="T1", description="", estimated_effort_hours=1.0))
        s = Scheduler(g)
        eb = EventBus()
        ex = Executor(s, eb)
        ex.execute_next()
        exp = engine.generate_completion_summary(goal, g, ex)
        assert len(exp.sections) >= 1

    def test_explain_decision(self) -> None:
        engine = ExplanationEngine(ReasoningEngine())
        exp = engine.explain_decision("Agent Selection", "Selected engineering agent", ["best match"])
        assert len(exp.sections) == 1
        assert exp.sections[0].title == "Agent Selection"
