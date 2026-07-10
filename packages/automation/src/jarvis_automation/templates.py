from __future__ import annotations

from jarvis_automation.models import (
    ApprovalGate,
    CompensationAction,
    CompensationStrategy,
    ExecutionMode,
    StepType,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowInput,
    WorkflowOutput,
    WorkflowStep,
    WorkflowTemplate,
)


def _task_step(
    step_id: str,
    name: str,
    description: str,
    tool_identifier: str = "",
    agent_identifier: str = "",
    timeout: int = 3600,
) -> WorkflowStep:
    return WorkflowStep(
        step_id=step_id,
        name=name,
        description=description,
        step_type=StepType.TASK,
        tool_identifier=tool_identifier,
        agent_identifier=agent_identifier,
        timeout_seconds=timeout,
    )


def _parallel_step(
    step_id: str,
    name: str,
    description: str,
    sub_steps: tuple[WorkflowStep, ...],
) -> WorkflowStep:
    return WorkflowStep(
        step_id=step_id,
        name=name,
        description=description,
        step_type=StepType.PARALLEL,
        execution_mode=ExecutionMode.PARALLEL,
        sub_steps=sub_steps,
    )


RESEARCH_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.research",
    name="Research Workflow",
    description="Conduct structured research using knowledge search and analysis tools.",
    category=WorkflowCategory.RESEARCH,
    definition=WorkflowDefinition(
        workflow_id="workflow.research",
        name="Research",
        description="Conduct structured research",
        version="1.0.0",
        category=WorkflowCategory.RESEARCH,
        steps=(
            _task_step("step.gather", "Gather Information", "Search knowledge bases"),
            _task_step("step.analyze", "Analyze Findings", "Analyze gathered information"),
            _task_step("step.synthesize", "Synthesize Results",
                       "Synthesize into conclusions"),
        ),
        inputs=(
            WorkflowInput(name="query", type="string", description="Research query"),
            WorkflowInput(name="depth", type="string", description="Research depth",
                          required=False),
        ),
        outputs=(
            WorkflowOutput(name="report", type="string", description="Research report"),
            WorkflowOutput(name="sources", type="string", description="Source references"),
        ),
        tags=("research", "analysis"),
    ),
    tags=("research", "template"),
)

ENGINEERING_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.engineering",
    name="Engineering Workflow",
    description="Execute engineering tasks using code execution and planning tools.",
    category=WorkflowCategory.ENGINEERING,
    definition=WorkflowDefinition(
        workflow_id="workflow.engineering",
        name="Engineering",
        description="Execute engineering tasks",
        version="1.0.0",
        category=WorkflowCategory.ENGINEERING,
        steps=(
            _task_step("step.plan", "Plan", "Create engineering plan"),
            _task_step("step.implement", "Implement", "Execute implementation"),
            _task_step("step.test", "Test", "Run tests"),
            _task_step("step.review", "Review", "Review results"),
        ),
        inputs=(
            WorkflowInput(name="task", type="string", description="Engineering task description"),
        ),
        outputs=(
            WorkflowOutput(name="result", type="string", description="Engineering result"),
            WorkflowOutput(name="test_report", type="string", description="Test results"),
        ),
        tags=("engineering", "development"),
    ),
    tags=("engineering", "template"),
)

KNOWLEDGE_PROCESSING_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.knowledge",
    name="Knowledge Processing Workflow",
    description="Process and index knowledge from documents and data sources.",
    category=WorkflowCategory.KNOWLEDGE_PROCESSING,
    definition=WorkflowDefinition(
        workflow_id="workflow.knowledge",
        name="Knowledge Processing",
        description="Process knowledge from documents",
        version="1.0.0",
        category=WorkflowCategory.KNOWLEDGE_PROCESSING,
        steps=(
            _task_step("step.extract", "Extract", "Extract content from sources"),
            _task_step("step.process", "Process", "Process and structure content"),
            _task_step("step.index", "Index", "Index processed knowledge"),
            _task_step("step.validate", "Validate", "Validate knowledge quality"),
        ),
        inputs=(
            WorkflowInput(name="source", type="string", description="Data source reference"),
        ),
        outputs=(
            WorkflowOutput(name="knowledge_id", type="string",
                           description="Knowledge base identifier"),
        ),
        tags=("knowledge", "processing"),
    ),
    tags=("knowledge", "template"),
)

DOCUMENT_ANALYSIS_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.docanalysis",
    name="Document Analysis Workflow",
    description="Analyze documents and extract structured information.",
    category=WorkflowCategory.DOCUMENT_ANALYSIS,
    definition=WorkflowDefinition(
        workflow_id="workflow.docanalysis",
        name="Document Analysis",
        description="Analyze documents and extract insights",
        version="1.0.0",
        category=WorkflowCategory.DOCUMENT_ANALYSIS,
        steps=(
            _task_step("step.load", "Load Document", "Load document content"),
            _task_step("step.analyze", "Analyze", "Analyze document structure and content"),
            _task_step("step.extract", "Extract Insights", "Extract key insights"),
            _task_step("step.summarize", "Summarize", "Generate analysis summary"),
        ),
        inputs=(
            WorkflowInput(name="document_id", type="string", description="Document identifier"),
            WorkflowInput(name="analysis_type", type="string",
                          description="Type of analysis", required=False),
        ),
        outputs=(
            WorkflowOutput(name="summary", type="string", description="Analysis summary"),
            WorkflowOutput(name="insights", type="string", description="Extracted insights"),
        ),
        tags=("document", "analysis"),
    ),
    tags=("document", "template"),
)

PROJECT_PLANNING_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.projectplan",
    name="Project Planning Workflow",
    description="Create structured project plans with tasks, milestones, and dependencies.",
    category=WorkflowCategory.PROJECT_PLANNING,
    definition=WorkflowDefinition(
        workflow_id="workflow.projectplan",
        name="Project Planning",
        description="Create project plans",
        version="1.0.0",
        category=WorkflowCategory.PROJECT_PLANNING,
        steps=(
            _task_step("step.define", "Define Scope", "Define project scope and objectives"),
            _parallel_step("step.parallel_tasks", "Create Tasks",
                           "Create project tasks and milestones", (
                _task_step("step.tasks", "Break Down Tasks", "Break work into tasks"),
                _task_step("step.milestones", "Define Milestones", "Define project milestones"),
            )),
            _task_step("step.schedule", "Create Schedule", "Build project schedule"),
        ),
        inputs=(
            WorkflowInput(name="project_name", type="string", description="Project name"),
            WorkflowInput(name="description", type="string", description="Project description"),
        ),
        outputs=(
            WorkflowOutput(name="plan", type="string", description="Project plan"),
        ),
        tags=("planning", "project"),
    ),
    tags=("planning", "template"),
)

TESTING_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.testing",
    name="Testing Workflow",
    description="Execute test suites and report results.",
    category=WorkflowCategory.TESTING,
    definition=WorkflowDefinition(
        workflow_id="workflow.testing",
        name="Testing",
        description="Execute tests and report results",
        version="1.0.0",
        category=WorkflowCategory.TESTING,
        steps=(
            _task_step("step.prepare", "Prepare", "Prepare test environment"),
            _parallel_step("step.run_tests", "Run Tests",
                           "Execute test suites in parallel", (
                _task_step("step.unit", "Unit Tests", "Run unit tests"),
                _task_step("step.integration", "Integration Tests", "Run integration tests"),
            )),
            _task_step("step.report", "Report", "Generate test report"),
        ),
        inputs=(
            WorkflowInput(name="test_suite", type="string", description="Test suite identifier"),
        ),
        outputs=(
            WorkflowOutput(name="report", type="string", description="Test results report"),
            WorkflowOutput(name="summary", type="string", description="Test summary"),
        ),
        tags=("testing", "quality"),
    ),
    tags=("testing", "template"),
)

NOTIFICATION_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.notification",
    name="Notification Workflow",
    description="Send notifications through configured channels.",
    category=WorkflowCategory.NOTIFICATION,
    definition=WorkflowDefinition(
        workflow_id="workflow.notification",
        name="Notification",
        description="Send notifications",
        version="1.0.0",
        category=WorkflowCategory.NOTIFICATION,
        steps=(
            _task_step("step.prepare", "Prepare Message", "Prepare notification content"),
            _task_step("step.send", "Send", "Deliver notification via channels"),
            _task_step("step.confirm", "Confirm", "Confirm delivery"),
        ),
        inputs=(
            WorkflowInput(name="message", type="string", description="Notification message"),
            WorkflowInput(name="channel", type="string",
                          description="Delivery channel", required=False),
        ),
        outputs=(
            WorkflowOutput(name="status", type="string", description="Delivery status"),
        ),
        tags=("notification", "communication"),
    ),
    tags=("notification", "template"),
)

APPROVAL_WORKFLOW: WorkflowTemplate = WorkflowTemplate(
    template_id="template.approval",
    name="Approval Workflow",
    description="Multi-stage approval workflow with escalation and compensation.",
    category=WorkflowCategory.APPROVAL,
    definition=WorkflowDefinition(
        workflow_id="workflow.approval",
        name="Approval",
        description="Multi-stage approval process",
        version="1.0.0",
        category=WorkflowCategory.APPROVAL,
        steps=(
            WorkflowStep(
                step_id="step.submit",
                name="Submit",
                description="Submit for approval",
                step_type=StepType.TASK,
                timeout_seconds=3600,
            ),
            WorkflowStep(
                step_id="step.review",
                name="Review",
                description="Review submission",
                step_type=StepType.APPROVAL,
                approval_gate=ApprovalGate(
                    gate_id="gate.review",
                    description="Review and approve submission",
                    required_approvers=1,
                    timeout_seconds=86400,
                ),
                timeout_seconds=86400,
            ),
            _task_step("step.execute", "Execute", "Execute approved action"),
            WorkflowStep(
                step_id="step.compensate",
                name="Compensate",
                description="Reverse action if rejected",
                step_type=StepType.COMPENSATION,
                compensation=CompensationAction(
                    action_id="comp.reject",
                    description="Reverse approved action",
                    strategy=CompensationStrategy.UNDO_PREVIOUS,
                ),
            ),
        ),
        inputs=(
            WorkflowInput(name="request", type="string", description="Approval request details"),
        ),
        outputs=(
            WorkflowOutput(name="decision", type="string", description="Approval decision"),
            WorkflowOutput(name="result", type="string", description="Execution result"),
        ),
        tags=("approval", "governance"),
    ),
    tags=("approval", "template"),
)

WORKFLOW_TEMPLATES: tuple[WorkflowTemplate, ...] = (
    RESEARCH_WORKFLOW,
    ENGINEERING_WORKFLOW,
    KNOWLEDGE_PROCESSING_WORKFLOW,
    DOCUMENT_ANALYSIS_WORKFLOW,
    PROJECT_PLANNING_WORKFLOW,
    TESTING_WORKFLOW,
    NOTIFICATION_WORKFLOW,
    APPROVAL_WORKFLOW,
)
