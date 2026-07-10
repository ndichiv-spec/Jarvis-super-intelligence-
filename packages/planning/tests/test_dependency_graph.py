from jarvis_planning.dependency_graph import CycleError, DependencyGraph
from jarvis_planning.decomposer import Task


def _make_task(tid: str, deps: list[str] | None = None, effort: float = 1.0) -> Task:
    return Task(id=tid, title=f"Task {tid}", description="", dependencies=deps or [], estimated_effort_hours=effort)


class TestDependencyGraph:
    def test_add_task(self) -> None:
        g = DependencyGraph()
        t = _make_task("t1")
        g.add_task(t)
        assert "t1" in g.tasks

    def test_add_tasks(self) -> None:
        g = DependencyGraph()
        g.add_tasks([_make_task("t1"), _make_task("t2")])
        assert len(g.tasks) == 2

    def test_get_dependencies(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1", ["t2", "t3"]))
        deps = g.get_dependencies("t1")
        assert deps == ["t2", "t3"]

    def test_get_dependents(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.add_task(_make_task("t3", ["t1"]))
        deps = g.get_dependents("t1")
        assert "t2" in deps
        assert "t3" in deps

    def test_topological_sort_simple(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.add_task(_make_task("t3", ["t2"]))
        order = g.topological_sort()
        assert order.index("t1") < order.index("t2")
        assert order.index("t2") < order.index("t3")

    def test_topological_sort_no_deps(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2"))
        g.add_task(_make_task("t3"))
        order = g.topological_sort()
        assert len(order) == 3

    def test_cycle_detection(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1", ["t2"]))
        g.add_task(_make_task("t2", ["t3"]))
        g.add_task(_make_task("t3", ["t1"]))
        try:
            g.topological_sort()
            assert False, "Should have raised CycleError"
        except CycleError:
            pass

    def test_validate_no_cycles_passes(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.validate_no_cycles()

    def test_validate_no_cycles_raises(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1", ["t2"]))
        g.add_task(_make_task("t2", ["t1"]))
        try:
            g.validate_no_cycles()
            assert False
        except CycleError:
            pass

    def test_get_levels(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.add_task(_make_task("t3", ["t1"]))
        levels = g.get_levels()
        assert len(levels) >= 2
        assert "t1" in levels[0]

    def test_critical_path(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1", effort=2.0))
        g.add_task(_make_task("t2", ["t1"], effort=3.0))
        g.add_task(_make_task("t3", ["t1"], effort=1.0))
        g.add_task(_make_task("t4", ["t2", "t3"], effort=2.0))
        critical = g.critical_path()
        assert len(critical) >= 1
        assert "t1" in critical

    def test_get_all_dependencies(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.add_task(_make_task("t3", ["t2"]))
        all_deps = g.get_all_dependencies("t3")
        assert "t1" in all_deps
        assert "t2" in all_deps

    def test_get_all_dependents(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.add_task(_make_task("t3", ["t1"]))
        all_deps = g.get_all_dependents("t1")
        assert "t2" in all_deps
        assert "t3" in all_deps

    def test_subgraph(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        g.add_task(_make_task("t3"))
        sub = g.subgraph({"t1", "t2"})
        assert "t1" in sub.tasks
        assert "t2" in sub.tasks
        assert "t3" not in sub.tasks

    def test_merge(self) -> None:
        g1 = DependencyGraph()
        g1.add_task(_make_task("t1"))
        g2 = DependencyGraph()
        g2.add_task(_make_task("t2", ["t1"]))
        g1.merge(g2)
        assert "t2" in g1.tasks

    def test_to_dict(self) -> None:
        g = DependencyGraph()
        g.add_task(_make_task("t1"))
        g.add_task(_make_task("t2", ["t1"]))
        d = g.to_dict()
        assert "tasks" in d
        assert "edges" in d
        assert "levels" in d
        assert "critical_path" in d
        assert d["total_tasks"] == 2
