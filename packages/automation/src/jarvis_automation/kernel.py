from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from jarvis_automation.approval import InMemoryApprovalEngine
from jarvis_automation.compensation import InMemoryCompensationEngine
from jarvis_automation.context import InMemoryExecutionContext
from jarvis_automation.engine import InMemoryWorkflowEngine
from jarvis_automation.models import (
    TriggerType,
    WorkflowDefinition,
    WorkflowExecutionRequest,
    WorkflowExecutionResult,
    WorkflowExecutionState,
    WorkflowHealthReport,
    WorkflowMetadata,
)
from jarvis_automation.monitoring import InMemoryMonitoringEngine
from jarvis_automation.policies import InMemoryPolicyEngine
from jarvis_automation.registry import InMemoryWorkflowRegistry
from jarvis_automation.retry import InMemoryRetryManager
from jarvis_automation.scheduler import InMemorySchedulerEngine
from jarvis_automation.state import InMemoryStateManager
from jarvis_automation.templates import WORKFLOW_TEMPLATES
from jarvis_automation.triggers import InMemoryTriggerEngine
from jarvis_automation.variables import InMemoryVariableManager


@dataclass(slots=True)
class AutomationKernel:
    registry: InMemoryWorkflowRegistry = field(
        default_factory=InMemoryWorkflowRegistry,
    )
    engine: InMemoryWorkflowEngine = field(default_factory=InMemoryWorkflowEngine)
    triggers: InMemoryTriggerEngine = field(default_factory=InMemoryTriggerEngine)
    scheduler: InMemorySchedulerEngine = field(default_factory=InMemorySchedulerEngine)
    state_manager: InMemoryStateManager = field(default_factory=InMemoryStateManager)
    retry_manager: InMemoryRetryManager = field(default_factory=InMemoryRetryManager)
    compensation: InMemoryCompensationEngine = field(
        default_factory=InMemoryCompensationEngine,
    )
    approval: InMemoryApprovalEngine = field(default_factory=InMemoryApprovalEngine)
    variables: InMemoryVariableManager = field(default_factory=InMemoryVariableManager)
    context: InMemoryExecutionContext = field(default_factory=InMemoryExecutionContext)
    monitoring: InMemoryMonitoringEngine = field(default_factory=InMemoryMonitoringEngine)
    policies: InMemoryPolicyEngine = field(default_factory=InMemoryPolicyEngine)

    def __post_init__(self) -> None:
        self._register_templates()

    def _register_templates(self) -> None:
        for template in WORKFLOW_TEMPLATES:
            self.registry.register(template.definition)

    def register_workflow(self, definition: WorkflowDefinition) -> WorkflowMetadata:
        return self.registry.register(definition)

    def register_workflow_from_template(self, template_id: str) -> WorkflowMetadata | None:
        for template in WORKFLOW_TEMPLATES:
            if template.template_id == template_id:
                return self.registry.register(template.definition)
        return None

    def execute(
        self,
        workflow_id: str,
        inputs: dict[str, str],
        trigger_type: TriggerType = TriggerType.MANUAL,
    ) -> WorkflowExecutionResult:
        metadata = self.registry.get(workflow_id)
        if metadata is None:
            return WorkflowExecutionResult(
                execution_id=f"exec-{uuid4().hex[:8]}",
                workflow_id=workflow_id,
                status="failed",  # type: ignore[arg-type]
                error_message=f"Workflow not found: {workflow_id}",
            )

        definition = metadata.definition
        execution_id = f"exec-{uuid4().hex[:8]}"

        # Wire shared sub-systems before initialising execution
        self.engine.state_manager = self.state_manager
        self.engine.retry_manager = self.retry_manager
        self.engine.compensation_engine = self.compensation
        self.engine.approval_engine = self.approval
        self.engine.context = self.context
        self.engine.monitoring = self.monitoring

        request = WorkflowExecutionRequest(
            execution_id=execution_id,
            workflow_id=workflow_id,
            trigger_type=trigger_type,
            inputs=inputs,
            workspace=metadata.definition.workspace,
            requested_by=metadata.definition.owner,
        )

        # Initialize execution via engine
        self.engine.start(request)

        # Execute steps
        result = self.engine._execute_steps(
            definition, execution_id, inputs, definition.steps,
        )

        return result

    def pause(self, execution_id: str) -> WorkflowExecutionResult:
        return self.engine.pause(execution_id)

    def resume(self, execution_id: str) -> WorkflowExecutionResult:
        return self.engine.resume(execution_id)

    def cancel(self, execution_id: str) -> WorkflowExecutionResult:
        return self.engine.cancel(execution_id)

    def get_status(self, execution_id: str) -> WorkflowExecutionState | None:
        return self.engine.get_status(execution_id)

    def get_result(self, execution_id: str) -> WorkflowExecutionResult | None:
        return self.engine.get_result(execution_id)

    def get_health(self, workflow_id: str) -> WorkflowHealthReport | None:
        return self.monitoring.get_workflow_health(workflow_id)

    def list_workflows(self) -> tuple[WorkflowMetadata, ...]:
        return self.registry.list()

    def list_templates(self) -> tuple[str, ...]:
        return tuple(t.template_id for t in WORKFLOW_TEMPLATES)
