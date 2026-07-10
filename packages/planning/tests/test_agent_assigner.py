from jarvis_agents.definitions import DEFAULT_AGENT_DEFINITIONS
from jarvis_agents.kernel import AgentKernel

from jarvis_planning.agent_assigner import AgentAssigner, AssignmentStrategy
from jarvis_planning.decomposer import Task


def _make_kernel() -> AgentKernel:
    kernel = AgentKernel()
    for definition in DEFAULT_AGENT_DEFINITIONS:
        kernel.register_agent(
            definition,
            owner="test",
            workspace="test",
            agent_id=f"agent-{definition.role}",
            name=definition.role.title(),
        )
        kernel.activate_agent(f"agent-{definition.role}")
    return kernel


class TestAgentAssigner:
    def test_assign_task_by_capability(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel, AssignmentStrategy.CAPABILITY_MATCH)
        task = Task(id="t1", title="Develop Backend API", description="Build RESTful API")
        assignment = assigner.assign_task(task)
        assert assignment.task_id == "t1"
        assert assignment.agent_id is not None
        assert assignment.capability_matched is not None

    def test_assign_tasks_batch(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel)
        tasks = [
            Task(id="t1", title="Design Architecture", description="Create system design"),
            Task(id="t2", title="Develop Frontend", description="Build UI"),
        ]
        assignments = assigner.assign_tasks(tasks)
        assert len(assignments) == 2
        for t in tasks:
            assert t.assigned_agent != ""

    def test_strategy_workload_balance(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel, AssignmentStrategy.WORKLOAD_BALANCE)
        task = Task(id="t1", title="Testing", description="Run tests")
        assignment = assigner.assign_task(task)
        assert assignment.strategy == AssignmentStrategy.WORKLOAD_BALANCE

    def test_strategy_confidence_score(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel, AssignmentStrategy.CONFIDENCE_SCORE)
        task = Task(id="t1", title="Research Topic", description="Conduct research")
        assignment = assigner.assign_task(task)
        assert assignment.strategy == AssignmentStrategy.CONFIDENCE_SCORE

    def test_strategy_round_robin(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel, AssignmentStrategy.ROUND_ROBIN)
        task = Task(id="t1", title="General Task", description="Do something")
        assignment = assigner.assign_task(task)
        assert assignment.strategy == AssignmentStrategy.ROUND_ROBIN

    def test_assignment_to_dict(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel)
        task = Task(id="t1", title="Develop Backend", description="API development")
        assignment = assigner.assign_task(task)
        d = assignment.to_dict()
        assert d["task_id"] == "t1"
        assert "agent_id" in d
        assert "confidence" in d
        assert "strategy" in d

    def test_resolve_capability(self) -> None:
        kernel = _make_kernel()
        assigner = AgentAssigner(kernel)
        task = Task(id="t1", title="Design Database Schema", description="Create database design")
        capability = assigner._resolve_capability(task)
        assert capability in ("architecture", "design")

    def test_empty_agent_pool(self) -> None:
        kernel = AgentKernel()
        assigner = AgentAssigner(kernel)
        task = Task(id="t1", title="Task", description="")
        assignment = assigner.assign_task(task, available_agents=())
        assert assignment is not None
