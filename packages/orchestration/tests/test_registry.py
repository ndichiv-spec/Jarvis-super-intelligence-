from jarvis_orchestration.models import Workflow, WorkflowPriority
from jarvis_orchestration.registry import WorkflowRegistry


class TestWorkflowRegistry:
    def test_add_and_get(self):
        r = WorkflowRegistry()
        wf = Workflow.create("Test")
        r.add(wf)
        assert r.get(wf.id) is wf

    def test_get_nonexistent(self):
        r = WorkflowRegistry()
        assert r.get("nonexistent") is None

    def test_remove(self):
        r = WorkflowRegistry()
        wf = Workflow.create("Remove me")
        r.add(wf)
        assert r.remove(wf.id) is True
        assert r.get(wf.id) is None

    def test_remove_nonexistent(self):
        r = WorkflowRegistry()
        assert r.remove("nonexistent") is False

    def test_list_all(self):
        r = WorkflowRegistry()
        r.add(Workflow.create("A"))
        r.add(Workflow.create("B"))
        assert len(r.list()) == 2

    def test_list_filter_priority(self):
        r = WorkflowRegistry()
        r.add(Workflow.create("Low", priority=WorkflowPriority.LOW))
        r.add(Workflow.create("High", priority=WorkflowPriority.HIGH))
        high = r.list(priority=WorkflowPriority.HIGH)
        assert len(high) == 1
        assert high[0].name == "High"

    def test_list_filter_owner(self):
        r = WorkflowRegistry()
        r.add(Workflow.create("A", owner="alice"))
        r.add(Workflow.create("B", owner="bob"))
        alice_wfs = r.list(owner="alice")
        assert len(alice_wfs) == 1

    def test_search(self):
        r = WorkflowRegistry()
        r.add(Workflow.create("Deploy pipeline"))
        r.add(Workflow.create("Build system"))
        r.add(Workflow.create("Test suite"))
        results = r.search("deploy")
        assert len(results) == 1
        assert results[0].name == "Deploy pipeline"

    def test_search_case_insensitive(self):
        r = WorkflowRegistry()
        r.add(Workflow.create("DEPLOY PRODUCTION"))
        results = r.search("deploy")
        assert len(results) == 1

    def test_count(self):
        r = WorkflowRegistry()
        assert r.count() == 0
        r.add(Workflow.create("A"))
        assert r.count() == 1
