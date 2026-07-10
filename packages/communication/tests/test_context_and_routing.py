from jarvis_communication.context import ExecutionContext, SecurityContext, WorkspaceContext
from jarvis_communication.messages import BaseMessage
from jarvis_communication.routing import DispatchMode, Route, RoutingEngine


def test_execution_context_creates_child_with_correlation_and_parent_link() -> None:
    parent = ExecutionContext.new(
        source="api",
        security_context=SecurityContext(principal_id="user-1", roles=("admin",)),
        workspace_context=WorkspaceContext(workspace_id="workspace-1", tenant_id="tenant-1"),
        metadata={"request_type": "query"},
    )

    child = parent.child(source="worker", metadata={"step": "projection"})

    assert child.correlation_id == parent.correlation_id
    assert child.request_id == parent.request_id
    assert child.parent_execution_id == parent.execution_id
    assert child.execution_id != parent.execution_id
    assert child.source == "worker"
    assert child.security_context == parent.security_context
    assert child.workspace_context == parent.workspace_context
    assert child.metadata == {"request_type": "query", "step": "projection"}


def test_routing_engine_supports_priority_grouping_directed_and_conditional_routes() -> None:
    routing = RoutingEngine()
    context = ExecutionContext.new(source="router")
    message = BaseMessage(
        message_name="notification.task",
        payload={"kind": "task", "priority": "high"},
    )

    routing.register(
        Route(handler_name="broadcast-low", message_name="notification.task", priority=1)
    )
    routing.register(
        Route(handler_name="broadcast-high", message_name="notification.task", priority=10)
    )
    routing.register(
        Route(
            handler_name="group-primary",
            message_name="notification.task",
            mode=DispatchMode.GROUPED,
            group="task-group",
            priority=5,
        )
    )
    routing.register(
        Route(
            handler_name="group-secondary",
            message_name="notification.task",
            mode=DispatchMode.GROUPED,
            group="task-group",
            priority=3,
        )
    )
    routing.register(
        Route(
            handler_name="directed-analytics",
            message_name="notification.task",
            mode=DispatchMode.DIRECTED,
            destination="analytics",
            priority=8,
        )
    )
    routing.register(
        Route(
            handler_name="conditional-high",
            message_name="notification.task",
            priority=7,
            condition=lambda routed_message, _context: routed_message.payload["priority"] == "high",
        )
    )

    decision = routing.resolve(message, context, target="analytics")

    assert decision.handlers == (
        "broadcast-high",
        "directed-analytics",
        "conditional-high",
        "group-primary",
        "broadcast-low",
    )
