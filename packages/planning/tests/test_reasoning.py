from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.reasoning import ReasoningChain, ReasoningEngine, ReasoningStep
from jarvis_planning.scheduler import Scheduler


class TestReasoningStep:
    def test_creation(self) -> None:
        step = ReasoningStep("analysis", "Analyzed the goal", {"key": "value"})
        assert step.type == "analysis"
        assert step.content == "Analyzed the goal"

    def test_to_dict(self) -> None:
        step = ReasoningStep("test", "content", {"a": 1})
        d = step.to_dict()
        assert d["type"] == "test"
        assert d["details"]["a"] == 1


class TestReasoningChain:
    def test_add_step(self) -> None:
        chain = ReasoningChain()
        chain.add("analysis", "Analyzed", {"score": 5})
        assert len(chain.steps) == 1
        assert chain.steps[0].type == "analysis"

    def test_to_dict(self) -> None:
        chain = ReasoningChain()
        chain.add("step1", "First step")
        chain.add("step2", "Second step")
        d = chain.to_dict()
        assert len(d) == 2


class TestReasoningEngine:
    def test_analyze_goal(self) -> None:
        engine = ReasoningEngine()
        goal = Goal(objective="Build a web app", category="web", risk_level="low")
        chain = engine.analyze_goal(goal)
        step_types = [s.type for s in chain.steps]
        assert "objective_analysis" in step_types
        assert "category_detection" in step_types

    def test_analyze_goal_with_ambiguity(self) -> None:
        engine = ReasoningEngine()
        goal = Goal(objective="Build something", ambiguity=["vague"])
        chain = engine.analyze_goal(goal)
        assert any(s.type == "ambiguity_detection" for s in chain.steps)

    def test_analyze_task_decomposition(self) -> None:
        engine = ReasoningEngine()
        tasks = [
            Task(id="t1", title="Task 1", description="", estimated_effort_hours=2.0),
            Task(id="t2", title="Task 2", description="", estimated_effort_hours=3.0),
        ]
        chain = engine.analyze_task_decomposition(tasks)
        assert any(s.type == "decomposition" for s in chain.steps)
        assert any(s.type == "effort_estimation" for s in chain.steps)

    def test_analyze_dependency_graph(self) -> None:
        engine = ReasoningEngine()
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="Task 1", description=""))
        g.add_task(Task(id="t2", title="Task 2", description="", dependencies=["t1"]))
        s = Scheduler(g)
        chain = engine.analyze_dependency_graph(g, s)
        assert any(s.type == "dependency_structure" for s in chain.steps)

    def test_analyze_schedule(self) -> None:
        engine = ReasoningEngine()
        g = DependencyGraph()
        g.add_task(Task(id="t1", title="Task 1", description=""))
        s = Scheduler(g)
        chain = engine.analyze_schedule(s)
        assert any(s.type == "schedule" for s in chain.steps)
        assert any(s.type == "capacity" for s in chain.steps)

    def test_get_chain(self) -> None:
        engine = ReasoningEngine()
        goal = Goal(objective="Test")
        engine.analyze_goal(goal)
        chain = engine.get_chain("goal_analysis")
        assert chain is not None
        assert len(chain.steps) > 0

    def test_get_chain_not_found(self) -> None:
        engine = ReasoningEngine()
        assert engine.get_chain("nonexistent") is None

    def test_get_all_chains(self) -> None:
        engine = ReasoningEngine()
        goal = Goal(objective="Test")
        engine.analyze_goal(goal)
        chains = engine.get_all_chains()
        assert "goal_analysis" in chains

    def test_clear(self) -> None:
        engine = ReasoningEngine()
        engine.analyze_goal(Goal(objective="Test"))
        engine.clear()
        assert engine.get_all_chains() == {}
