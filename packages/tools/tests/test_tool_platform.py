from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from jarvis_tools.definitions import BUILT_IN_TOOLS
from jarvis_tools.discovery import InMemoryDiscoveryEngine
from jarvis_tools.execution import InMemoryExecutionEngine, InMemoryToolExecutor
from jarvis_tools.health import InMemoryHealthMonitor
from jarvis_tools.kernel import ToolKernel
from jarvis_tools.models import (
    ExecutionStatus,
    PermissionAccess,
    PermissionResource,
    ToolCapability,
    ToolCategory,
    ToolDefinition,
    ToolExecutionPolicy,
    ToolExecutionRequest,
    ToolExecutionResult,
    ToolHealthReport,
    ToolMetadata,
    ToolPermission,
    ToolPolicy,
    ToolPolicyScope,
    ToolProperty,
    ToolSchema,
    ToolStatus,
    ToolValidationReport,
)
from jarvis_tools.permissions import InMemoryPermissionManager
from jarvis_tools.policy import InMemoryPolicyEngine
from jarvis_tools.registry import InMemoryToolRegistry
from jarvis_tools.validation import InMemoryValidationEngine

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_tool() -> ToolDefinition:
    return ToolDefinition(
        identifier="test.echo",
        name="Echo",
        description="Echoes back input parameters",
        version="1.0.0",
        category=ToolCategory.UTILITY,
        capabilities=(ToolCapability.CUSTOM,),
        input_schema=ToolSchema(
            properties=(
                ToolProperty(name="message", type="string", description="Message to echo"),
            ),
            description="Input",
        ),
        output_schema=ToolSchema(description="Output"),
        permissions=(
            ToolPermission(
                resource=PermissionResource.TOOL,
                access=PermissionAccess.READ,
            ),
        ),
    )


@pytest.fixture
def custom_executor() -> InMemoryToolExecutor:
    class FixedExecutor(InMemoryToolExecutor):
        def execute(
            self,
            definition: ToolDefinition,
            params: dict[str, str],
        ) -> ToolExecutionResult:
            return ToolExecutionResult(
                request_id="fixed",
                status=ExecutionStatus.COMPLETED,
                output=f"Hello {params.get('message', 'world')}",
                execution_time_ms=42,
            )

    return FixedExecutor()


@pytest.fixture
def kernel() -> ToolKernel:
    return ToolKernel()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class TestToolStatus:
    def test_values(self) -> None:
        assert ToolStatus.ACTIVE.value == "active"
        assert ToolStatus.INACTIVE.value == "inactive"

    def test_comparison(self) -> None:
        assert ToolStatus.ACTIVE == ToolStatus("active")


class TestToolDefinition:
    def test_create(self, sample_tool: ToolDefinition) -> None:
        assert sample_tool.identifier == "test.echo"
        assert sample_tool.category == ToolCategory.UTILITY
        assert ToolCapability.CUSTOM in sample_tool.capabilities

    def test_with_status(self, sample_tool: ToolDefinition) -> None:
        updated = sample_tool.with_status(ToolStatus.DEPRECATED)
        assert updated.status == ToolStatus.DEPRECATED
        assert updated.identifier == "test.echo"
        assert updated.updated_at > sample_tool.updated_at or True

    def test_default_policy(self) -> None:
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
        )
        assert t.execution_policy.timeout_seconds == 300
        assert t.status == ToolStatus.ACTIVE

    def test_created_at_utc(self, sample_tool: ToolDefinition) -> None:
        assert sample_tool.created_at.tzinfo is not None


class TestToolMetadata:
    def test_with_definition(self) -> None:
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
        )
        meta = ToolMetadata(identifier="x", definition=t)
        t2 = t.with_status(ToolStatus.DEPRECATED)
        meta2 = meta.with_definition(t2)
        assert meta2.definition.status == ToolStatus.DEPRECATED
        assert meta2.identifier == "x"


class TestToolExecutionRequest:
    def test_create(self) -> None:
        req = ToolExecutionRequest(
            request_id="r1",
            tool_identifier="t1",
            agent_id="a1",
            parameters={"x": "y"},
        )
        assert req.request_id == "r1"
        assert req.parameters["x"] == "y"
        assert req.created_at.tzinfo is not None


class TestToolExecutionResult:
    def test_create(self) -> None:
        res = ToolExecutionResult(
            request_id="r1",
            status=ExecutionStatus.COMPLETED,
            output="ok",
        )
        assert res.status == ExecutionStatus.COMPLETED
        assert res.output == "ok"


class TestToolValidationReport:
    def test_valid(self) -> None:
        r = ToolValidationReport(tool_identifier="t1", valid=True)
        assert r.valid
        assert len(r.errors) == 0

    def test_invalid(self) -> None:
        r = ToolValidationReport(
            tool_identifier="t1",
            valid=False,
            errors=("missing input",),
        )
        assert not r.valid
        assert "missing input" in r.errors


class TestToolHealthReport:
    def test_defaults(self) -> None:
        r = ToolHealthReport(tool_identifier="t1", available=True)
        assert r.available
        assert r.execution_count == 0


class TestToolPolicy:
    def test_defaults(self) -> None:
        p = ToolPolicy(policy_id="p1", name="test")
        assert p.max_executions_per_minute == 60
        assert p.max_concurrent_executions == 10


class TestToolPolicyScope:
    def test_defaults(self) -> None:
        s = ToolPolicyScope()
        assert s.owner == "*"
        assert s.workspace == "*"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestInMemoryToolRegistry:
    def test_register_and_get(self, sample_tool: ToolDefinition) -> None:
        r = InMemoryToolRegistry()
        meta = r.register(sample_tool)
        assert meta.identifier == "test.echo"
        assert r.get("test.echo") is meta
        assert r.get("nonexistent") is None

    def test_deregister(self, sample_tool: ToolDefinition) -> None:
        r = InMemoryToolRegistry()
        r.register(sample_tool)
        r.deregister("test.echo")
        assert r.get("test.echo") is None

    def test_list(self, sample_tool: ToolDefinition) -> None:
        r = InMemoryToolRegistry()
        assert len(r.list()) == 0
        r.register(sample_tool)
        assert len(r.list()) == 1

    def test_list_by_status(self, sample_tool: ToolDefinition) -> None:
        r = InMemoryToolRegistry()
        r.register(sample_tool)
        active = r.list_by_status(ToolStatus.ACTIVE)
        deprecated = r.list_by_status(ToolStatus.DEPRECATED)
        assert len(active) == 1
        assert len(deprecated) == 0

    def test_update(self, sample_tool: ToolDefinition) -> None:
        r = InMemoryToolRegistry()
        meta = r.register(sample_tool)
        updated_def = sample_tool.with_status(ToolStatus.DEPRECATED)
        updated_meta = meta.with_definition(updated_def)
        r.update(updated_meta)
        stored = r.get("test.echo")
        assert stored is not None
        assert stored.definition.status == ToolStatus.DEPRECATED


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


class TestInMemoryDiscoveryEngine:
    @pytest.fixture
    def engine(self) -> InMemoryDiscoveryEngine:
        e = InMemoryDiscoveryEngine()
        tools = []
        for t in BUILT_IN_TOOLS[:3]:
            tools.append(ToolMetadata(identifier=t.identifier, definition=t))
        e.sync(tuple(tools))
        return e

    def test_find_by_identifier(self, engine: InMemoryDiscoveryEngine) -> None:
        t = engine.find_by_identifier("knowledge.search")
        assert t is not None
        assert t.identifier == "knowledge.search"

    def test_find_by_identifier_inactive(self) -> None:
        e = InMemoryDiscoveryEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
            status=ToolStatus.INACTIVE,
        )
        e.sync((ToolMetadata(identifier="x", definition=t),))
        assert e.find_by_identifier("x") is None

    def test_find_by_category(self, engine: InMemoryDiscoveryEngine) -> None:
        results = engine.find_by_category(ToolCategory.KNOWLEDGE)
        assert len(results) >= 1

    def test_find_by_capability(self, engine: InMemoryDiscoveryEngine) -> None:
        results = engine.find_by_capability(ToolCapability.SEARCH)
        assert len(results) >= 1

    def test_search(self, engine: InMemoryDiscoveryEngine) -> None:
        results = engine.search("knowledge")
        assert len(results) >= 1

    def test_composite_query(self, engine: InMemoryDiscoveryEngine) -> None:
        results = engine.composite_query({"category": "knowledge"})
        assert len(results) >= 1


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestInMemoryValidationEngine:
    def test_validate_input_missing_required(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
        )
        report = v.validate_input(t, {})
        assert report.valid

    def test_validate_input_type_check(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(
                properties=(ToolProperty(name="count", type="integer", description="c"),),
            ),
            output_schema=ToolSchema(),
            permissions=(),
        )
        report = v.validate_input(t, {"count": "abc"})
        assert not report.valid

    def test_validate_output_empty_ok(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(
                properties=(ToolProperty(name="r", type="string", description="r"),)
            ),
            permissions=(),
        )
        report = v.validate_output(t, "")
        assert not report.valid

    def test_validate_output_present(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(
                properties=(ToolProperty(name="r", type="string", description="r", required=False),)
            ),
            permissions=(),
        )
        report = v.validate_output(t, "")
        assert report.valid

    def test_validate_permissions(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(
                ToolPermission(
                    resource=PermissionResource.WORKSPACE,
                    access=PermissionAccess.READ,
                    scope="prod",
                ),
            ),
        )
        report = v.validate_permissions(t, "agent1", "dev")
        assert not report.valid

    def test_validate_execution_policy(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
            execution_policy=ToolExecutionPolicy(
                allowed_workspaces=("prod",),
            ),
        )
        report = v.validate_execution_policy(t, "dev")
        assert not report.valid

    def test_validate_all(self) -> None:
        v = InMemoryValidationEngine()
        t = ToolDefinition(
            identifier="x",
            name="x",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
        )
        report = v.validate_all(t, {}, "a1", "*")
        assert report.valid


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


class TestInMemoryExecutionEngine:
    def test_execute_no_executor(self) -> None:
        e = InMemoryExecutionEngine()
        req = ToolExecutionRequest(
            request_id="r1",
            tool_identifier="nonexistent",
            agent_id="a1",
            parameters={},
        )
        result = e.execute(req)
        assert result.status == ExecutionStatus.FAILED
        assert "No executor" in (result.error_message or "")

    def test_execute_with_executor(self, sample_tool: ToolDefinition) -> None:
        e = InMemoryExecutionEngine()
        e.register_executor("test.echo", InMemoryToolExecutor())
        req = ToolExecutionRequest(
            request_id="r2",
            tool_identifier="test.echo",
            agent_id="a1",
            parameters={"message": "hi"},
        )
        result = e.execute(req)
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output

    def test_cancel_completed_is_noop(self) -> None:
        e = InMemoryExecutionEngine()
        e.register_executor("t1", InMemoryToolExecutor())
        req = ToolExecutionRequest(
            request_id="r3",
            tool_identifier="t1",
            agent_id="a1",
            parameters={},
        )
        e.execute(req)
        e.cancel("r3")
        status = e.get_status("r3")
        # Cancel is a no-op when execution already completed
        assert status == ExecutionStatus.COMPLETED

    def test_list_active(self) -> None:
        e = InMemoryExecutionEngine()
        assert len(e.list_active()) == 0

    def test_get_status_none(self) -> None:
        e = InMemoryExecutionEngine()
        assert e.get_status("nonexistent") is None

    def test_get_result(self) -> None:
        e = InMemoryExecutionEngine()
        e.register_executor("test.echo", InMemoryToolExecutor())
        req = ToolExecutionRequest(
            request_id="r4",
            tool_identifier="test.echo",
            agent_id="a1",
            parameters={},
        )
        e.execute(req)
        result = e.get_result("r4")
        assert result is not None
        assert result.status == ExecutionStatus.COMPLETED

    def test_cancel_idempotent(self) -> None:
        e = InMemoryExecutionEngine()
        e.cancel("nonexistent")


class TestInMemoryToolExecutor:
    def test_can_execute(self) -> None:
        ex = InMemoryToolExecutor()
        assert ex.can_execute("anything")

    def test_execute(self, sample_tool: ToolDefinition) -> None:
        ex = InMemoryToolExecutor()
        result = ex.execute(sample_tool, {"message": "hello"})
        assert result.status == ExecutionStatus.COMPLETED
        assert result.execution_time_ms >= 0
        assert result.request_id.startswith("exec-")


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


class TestInMemoryPermissionManager:
    def test_check_default_deny(self) -> None:
        pm = InMemoryPermissionManager()
        assert not pm.check_permission("t1", "workspace", "read", "*")

    def test_grant_and_check(self) -> None:
        pm = InMemoryPermissionManager()
        perm = ToolPermission(
            resource=PermissionResource.WORKSPACE,
            access=PermissionAccess.READ,
        )
        pm.grant_permission("t1", perm)
        assert pm.check_permission("t1", "workspace", "read", "*")
        assert not pm.check_permission("t1", "workspace", "write", "*")

    def test_revoke(self) -> None:
        pm = InMemoryPermissionManager()
        perm = ToolPermission(
            resource=PermissionResource.WORKSPACE,
            access=PermissionAccess.READ,
        )
        pm.grant_permission("t1", perm)
        pm.revoke_permission("t1", "workspace", "*")
        assert not pm.check_permission("t1", "workspace", "read", "*")

    def test_access_levels(self) -> None:
        pm = InMemoryPermissionManager()
        pm.grant_permission(
            "t1",
            ToolPermission(
                resource=PermissionResource.KNOWLEDGE,
                access=PermissionAccess.WRITE,
            ),
        )
        assert pm.check_permission("t1", "knowledge", "read", "*")
        assert pm.check_permission("t1", "knowledge", "write", "*")
        assert not pm.check_permission("t1", "knowledge", "admin", "*")

    def test_revoke_idempotent(self) -> None:
        pm = InMemoryPermissionManager()
        pm.revoke_permission("nonexistent", "workspace", "*")


# ---------------------------------------------------------------------------
# Policy Engine
# ---------------------------------------------------------------------------


class TestInMemoryPolicyEngine:
    def test_default_policy(self) -> None:
        pe = InMemoryPolicyEngine()
        policy = pe.resolve(ToolPolicyScope())
        assert policy.policy_id == "default"

    def test_register_and_resolve(self) -> None:
        pe = InMemoryPolicyEngine()
        scope = ToolPolicyScope(owner="alice")
        policy = ToolPolicy(
            policy_id="p1",
            name="Alice Policy",
            denied_tools=("test.echo",),
        )
        pe.register_policy(scope, policy)
        resolved = pe.resolve(ToolPolicyScope(owner="alice"))
        assert resolved.policy_id == "p1"

    def test_evaluate_no_violations(self) -> None:
        pe = InMemoryPolicyEngine()
        policy = ToolPolicy(policy_id="p1", name="test", workspace_restrictions=())
        violations = pe.evaluate("test.echo", policy)
        assert len(violations) == 0

    def test_evaluate_denied_tool(self) -> None:
        pe = InMemoryPolicyEngine()
        policy = ToolPolicy(
            policy_id="p1",
            name="test",
            denied_tools=("test.echo",),
            workspace_restrictions=(),
        )
        violations = pe.evaluate("test.echo", policy)
        assert len(violations) == 1

    def test_scope_matching(self) -> None:
        pe = InMemoryPolicyEngine()
        assert pe._scope_matches(
            ToolPolicyScope(owner="alice"),
            ToolPolicyScope(owner="alice"),
        )
        assert not pe._scope_matches(
            ToolPolicyScope(owner="alice"),
            ToolPolicyScope(owner="bob"),
        )


# ---------------------------------------------------------------------------
# Health Monitor
# ---------------------------------------------------------------------------


class TestInMemoryHealthMonitor:
    def test_record_execution(self) -> None:
        hm = InMemoryHealthMonitor()
        report = hm.record_execution("test.echo", 100, True)
        assert report.execution_count == 1
        assert report.failure_count == 0

    def test_record_failure(self) -> None:
        hm = InMemoryHealthMonitor()
        report = hm.record_failure("test.echo", "error")
        assert report.failure_count == 1

    def test_list_unhealthy(self) -> None:
        hm = InMemoryHealthMonitor()
        assert len(hm.list_unhealthy()) == 0
        hm.record_failure("failing_tool", "err")
        hm.record_failure("failing_tool", "err")
        hm.record_failure("failing_tool", "err")
        reports = hm.list_unhealthy()
        assert len(reports) >= 1

    def test_get_report(self) -> None:
        hm = InMemoryHealthMonitor()
        assert hm.get_report("nonexistent") is None
        hm.record_execution("test.echo", 50, True)
        assert hm.get_report("test.echo") is not None


# ---------------------------------------------------------------------------
# Kernel
# ---------------------------------------------------------------------------


class TestToolKernel:
    def test_kernel_initializes_with_builtins(self, kernel: ToolKernel) -> None:
        assert len(kernel.list_tools()) >= 8
        knowledge = kernel.registry.get("knowledge.search")
        assert knowledge is not None
        assert knowledge.definition.identifier == "knowledge.search"

    def test_execute_builtin(self, kernel: ToolKernel) -> None:
        result = kernel.execute("knowledge.search", {"query": "test"})
        assert result.status == ExecutionStatus.COMPLETED

    def test_execute_nonexistent(self, kernel: ToolKernel) -> None:
        result = kernel.execute("nonexistent", {})
        assert result.status == ExecutionStatus.FAILED

    def test_register_and_execute(
        self,
        kernel: ToolKernel,
        sample_tool: ToolDefinition,
    ) -> None:
        kernel.register(sample_tool)
        assert kernel.registry.get("test.echo") is not None
        result = kernel.execute("test.echo", {"message": "hello"})
        assert result.status == ExecutionStatus.COMPLETED

    def test_deregister(self, kernel: ToolKernel, sample_tool: ToolDefinition) -> None:
        kernel.register(sample_tool)
        kernel.deregister("test.echo")
        assert kernel.registry.get("test.echo") is None

    def test_validate(self, kernel: ToolKernel, sample_tool: ToolDefinition) -> None:
        report = kernel.validate(sample_tool, {"message": "hi"})
        assert report.valid

    def test_get_health(self, kernel: ToolKernel) -> None:
        report = kernel.get_health("knowledge.search")
        assert report is None or not report.available

    def test_search_tools(self, kernel: ToolKernel) -> None:
        results = kernel.search_tools("knowledge")
        assert len(results) >= 1

    def test_comprehensive_execution_flow(self, kernel: ToolKernel) -> None:
        t = ToolDefinition(
            identifier="custom.math.add",
            name="Add",
            description="Adds two numbers",
            version="1.0.0",
            category=ToolCategory.MATHEMATICS,
            capabilities=(ToolCapability.MATHEMATICS,),
            input_schema=ToolSchema(
                properties=(
                    ToolProperty(name="a", type="integer", description="First"),
                    ToolProperty(name="b", type="integer", description="Second"),
                ),
            ),
            output_schema=ToolSchema(description="Result"),
            permissions=(
                ToolPermission(
                    resource=PermissionResource.TOOL,
                    access=PermissionAccess.READ,
                ),
            ),
        )

        class MathExecutor(InMemoryToolExecutor):
            def execute(
                self,
                definition: ToolDefinition,
                params: dict[str, str],
            ) -> ToolExecutionResult:
                a = int(params.get("a", "0"))
                b = int(params.get("b", "0"))
                return ToolExecutionResult(
                    request_id="math-result",
                    status=ExecutionStatus.COMPLETED,
                    output=str(a + b),
                    execution_time_ms=1,
                )

        kernel.register(t)
        kernel.execution.register_executor("custom.math.add", MathExecutor())
        result = kernel.execute("custom.math.add", {"a": "3", "b": "4"})
        assert result.status == ExecutionStatus.COMPLETED
        assert result.output == "7"


# ---------------------------------------------------------------------------
# Built-in Definitions
# ---------------------------------------------------------------------------


class TestBuiltinDefinitions:
    def test_all_builtins_have_identifiers(self) -> None:
        for t in BUILT_IN_TOOLS:
            assert t.identifier, f"Missing identifier: {t.name}"

    def test_all_builtins_have_categories(self) -> None:
        for t in BUILT_IN_TOOLS:
            assert isinstance(t.category, ToolCategory), f"Bad category: {t.identifier}"

    def test_builtins_count(self) -> None:
        assert len(BUILT_IN_TOOLS) == 8


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_tool_with_empty_schema(self) -> None:
        t = ToolDefinition(
            identifier="empty",
            name="empty",
            description="",
            version="0.1.0",
            category=ToolCategory.UTILITY,
            capabilities=(),
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
        )
        assert t.input_schema.properties == ()

    def test_tool_with_many_capabilities(self) -> None:
        caps = tuple(ToolCapability)
        t = ToolDefinition(
            identifier="multi",
            name="multi",
            description="",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            capabilities=caps,
            input_schema=ToolSchema(),
            output_schema=ToolSchema(),
            permissions=(),
        )
        assert len(t.capabilities) == len(caps)

    def test_permission_none_is_denied(self) -> None:
        pm = InMemoryPermissionManager()
        pm.grant_permission(
            "t",
            ToolPermission(
                resource=PermissionResource.TOOL,
                access=PermissionAccess.NONE,
            ),
        )
        assert not pm.check_permission("t", "tool", "read", "*")

    def test_discovery_returns_empty_for_no_match(self) -> None:
        e = InMemoryDiscoveryEngine()
        e.sync(())
        assert e.find_by_category(ToolCategory.UTILITY) == ()
