from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from jarvis_planning.analyzer import Goal
from jarvis_planning.estimator import Complexity, Estimator
from jarvis_planning.policies import CompletionCriteria, RetryPolicy


class TaskType(Enum):
    HIERARCHICAL = "hierarchical"
    RECURSIVE = "recursive"
    MILESTONE = "milestone"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    ATOMIC = "atomic"


@dataclass
class TaskInput:
    name: str
    description: str
    required: bool = True
    source_task_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "required": self.required,
            "source_task_id": self.source_task_id,
        }


@dataclass
class TaskOutput:
    name: str
    description: str
    type: str = "artifact"

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "type": self.type}


@dataclass
class Task:
    id: str
    title: str
    description: str
    task_type: TaskType = TaskType.ATOMIC
    inputs: list[TaskInput] = field(default_factory=list)
    outputs: list[TaskOutput] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    priority: int = 0
    assigned_agent: str = ""
    estimated_effort_hours: float = 1.0
    retry_policy: RetryPolicy = field(default_factory=lambda: RetryPolicy())
    completion_criteria: CompletionCriteria = field(default_factory=lambda: CompletionCriteria())
    metadata: dict[str, Any] = field(default_factory=dict)
    group: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "dependencies": self.dependencies,
            "priority": self.priority,
            "assigned_agent": self.assigned_agent,
            "estimated_effort_hours": self.estimated_effort_hours,
            "retry_policy": self.retry_policy.to_dict(),
            "completion_criteria": self.completion_criteria.to_dict(),
            "metadata": self.metadata,
            "group": self.group,
        }


_TASK_TEMPLATES: dict[str, dict[str, Any]] = {
    "gather_requirements": {
        "title": "Gather Requirements",
        "description": "Collect and document all functional and non-functional requirements",
        "task_type": TaskType.HIERARCHICAL,
        "estimated_effort_hours": 3.0,
        "outputs": [{"name": "requirements_doc", "description": "Requirements specification", "type": "document"}],
    },
    "design_architecture": {
        "title": "Design Architecture",
        "description": "Create system architecture design including components, interfaces, and data flow",
        "task_type": TaskType.HIERARCHICAL,
        "estimated_effort_hours": 8.0,
        "outputs": [{"name": "architecture_doc", "description": "Architecture design document", "type": "document"}],
    },
    "design_database": {
        "title": "Design Database",
        "description": "Design database schema, relationships, and indexes",
        "estimated_effort_hours": 5.0,
        "outputs": [{"name": "schema_design", "description": "Database schema design", "type": "document"}],
    },
    "develop_backend": {
        "title": "Develop Backend",
        "description": "Implement backend API services and business logic",
        "task_type": TaskType.HIERARCHICAL,
        "estimated_effort_hours": 16.0,
        "outputs": [{"name": "backend_code", "description": "Backend source code", "type": "code"}],
    },
    "develop_frontend": {
        "title": "Develop Frontend",
        "description": "Implement frontend UI components and pages",
        "task_type": TaskType.HIERARCHICAL,
        "estimated_effort_hours": 12.0,
        "outputs": [{"name": "frontend_code", "description": "Frontend source code", "type": "code"}],
    },
    "develop_mobile": {
        "title": "Develop Mobile Application",
        "description": "Build mobile application for iOS and Android",
        "task_type": TaskType.HIERARCHICAL,
        "estimated_effort_hours": 20.0,
        "outputs": [{"name": "mobile_code", "description": "Mobile application source code", "type": "code"}],
    },
    "testing": {
        "title": "Testing",
        "description": "Execute comprehensive testing including unit, integration, and e2e tests",
        "estimated_effort_hours": 8.0,
        "outputs": [{"name": "test_report", "description": "Test execution report", "type": "report"}],
    },
    "documentation": {
        "title": "Documentation",
        "description": "Create user and technical documentation",
        "estimated_effort_hours": 5.0,
        "outputs": [{"name": "documentation", "description": "Project documentation", "type": "document"}],
    },
    "deployment": {
        "title": "Deployment",
        "description": "Deploy application to target environment",
        "estimated_effort_hours": 4.0,
        "outputs": [{"name": "deployment", "description": "Deployed application", "type": "deployment"}],
    },
}


class TaskDecomposer:
    def __init__(self, estimator: Estimator | None = None) -> None:
        self._estimator = estimator or Estimator()

    def decompose(self, goal: Goal, template_names: list[str] | None = None) -> list[Task]:
        if template_names:
            return self._from_templates(template_names, goal)

        tasks = self._decompose_from_category(goal)
        self._link_dependencies(tasks, goal)
        return tasks

    def _from_templates(self, names: list[str], goal: Goal) -> list[Task]:
        tasks: list[Task] = []
        for idx, name in enumerate(names):
            template = _TASK_TEMPLATES.get(name)
            if template is None:
                continue
            task = Task(
                id=f"task-{idx + 1:02d}",
                title=template["title"],
                description=template["description"],
                task_type=template.get("task_type", TaskType.ATOMIC),
                estimated_effort_hours=template["estimated_effort_hours"],
                outputs=[TaskOutput(**o) for o in template["outputs"]],
            )
            if idx > 0:
                task.dependencies.append(tasks[idx - 1].id)
            tasks.append(task)
        return tasks

    def _decompose_from_category(self, goal: Goal) -> list[Task]:
        category = goal.category
        if category == "web":
            return self._web_app_tasks(goal)
        if category == "mobile":
            return self._mobile_app_tasks(goal)
        if category == "data":
            return self._data_pipeline_tasks(goal)
        if category == "ai-ml":
            return self._ml_project_tasks(goal)
        if category == "devops":
            return self._devops_tasks(goal)
        if category in ("automation", "integration"):
            return self._integration_tasks(goal)
        if category == "security":
            return self._security_tasks(goal)
        return self._general_software_tasks(goal)

    def _web_app_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Gather Requirements", "Collect functional and non-functional requirements",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=4.0, group="initiation",
                 outputs=[TaskOutput("requirements_doc", "Requirements specification", "document")]),
            Task("task-02", "Design Architecture", "Design system architecture and component interaction",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=6.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("architecture_doc", "Architecture design", "document")]),
            Task("task-03", "Design Database Schema", "Design database tables, relationships, and indexes",
                 estimated_effort_hours=4.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("schema", "Database schema", "document")]),
            Task("task-04", "Develop API Backend", "Implement RESTful API services",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=12.0, dependencies=["task-02", "task-03"], group="development",
                 outputs=[TaskOutput("api_code", "Backend API code", "code")]),
            Task("task-05", "Develop Frontend UI", "Implement user interface components and pages",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=10.0, dependencies=["task-02"], group="development",
                 outputs=[TaskOutput("frontend_code", "Frontend code", "code")]),
            Task("task-06", "Testing", "Execute unit, integration, and e2e tests",
                 estimated_effort_hours=6.0, dependencies=["task-04", "task-05"], group="quality",
                 outputs=[TaskOutput("test_report", "Test report", "report")]),
            Task("task-07", "Documentation", "Create user and technical documentation",
                 estimated_effort_hours=4.0, dependencies=["task-06"], group="delivery",
                 outputs=[TaskOutput("docs", "Documentation", "document")]),
            Task("task-08", "Deployment", "Deploy application to production environment",
                 estimated_effort_hours=3.0, dependencies=["task-06"], group="delivery",
                 outputs=[TaskOutput("deployment", "Deployed application", "deployment")]),
        ]

    def _mobile_app_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Gather Requirements", "Collect requirements for mobile application",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=4.0, group="initiation",
                 outputs=[TaskOutput("requirements_doc", "Requirements", "document")]),
            Task("task-02", "Design Architecture", "Design mobile app architecture",
                 estimated_effort_hours=6.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("architecture_doc", "Architecture", "document")]),
            Task("task-03", "Design API Contract", "Design API contracts for mobile-backend communication",
                 estimated_effort_hours=3.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("api_contract", "API contract", "document")]),
            Task("task-04", "Develop Backend API", "Implement backend services for mobile",
                 estimated_effort_hours=10.0, dependencies=["task-02", "task-03"], group="backend",
                 outputs=[TaskOutput("api_code", "Backend code", "code")]),
            Task("task-05", "Build Mobile App", "Develop cross-platform mobile application",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=16.0, dependencies=["task-03"], group="mobile_dev",
                 outputs=[TaskOutput("mobile_code", "Mobile app code", "code")]),
            Task("task-06", "Testing", "Test mobile app on multiple devices and platforms",
                 estimated_effort_hours=8.0, dependencies=["task-04", "task-05"], group="quality",
                 outputs=[TaskOutput("test_report", "Test report", "report")]),
            Task("task-07", "Documentation & Deployment", "Prepare documentation and deploy",
                 estimated_effort_hours=4.0, dependencies=["task-06"], group="delivery",
                 outputs=[TaskOutput("docs", "Documentation", "document"), TaskOutput("deployment", "Deployed app", "deployment")]),
        ]

    def _data_pipeline_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Requirements Analysis", "Analyze data pipeline requirements",
                 estimated_effort_hours=3.0, group="initiation",
                 outputs=[TaskOutput("requirements", "Requirements", "document")]),
            Task("task-02", "Design Data Model", "Design data model and schema",
                 estimated_effort_hours=5.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("data_model", "Data model", "document")]),
            Task("task-03", "Setup Data Sources", "Configure and connect data sources",
                 estimated_effort_hours=6.0, dependencies=["task-01"], group="development",
                 outputs=[TaskOutput("data_sources", "Connected data sources", "configuration")]),
            Task("task-04", "Build ETL Pipeline", "Implement extraction, transformation, loading pipeline",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=12.0, dependencies=["task-02", "task-03"], group="development",
                 outputs=[TaskOutput("etl_code", "ETL pipeline code", "code")]),
            Task("task-05", "Build Analytics Layer", "Implement analytics queries and reports",
                 estimated_effort_hours=8.0, dependencies=["task-04"], group="development",
                 outputs=[TaskOutput("analytics", "Analytics layer", "code")]),
            Task("task-06", "Testing & Validation", "Validate data accuracy and pipeline performance",
                 estimated_effort_hours=5.0, dependencies=["task-04", "task-05"], group="quality",
                 outputs=[TaskOutput("validation_report", "Validation report", "report")]),
            Task("task-07", "Deployment & Monitoring", "Deploy pipeline and setup monitoring",
                 estimated_effort_hours=4.0, dependencies=["task-06"], group="delivery",
                 outputs=[TaskOutput("deployment", "Deployed pipeline", "deployment")]),
        ]

    def _ml_project_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Problem Definition", "Define ML problem and success metrics",
                 estimated_effort_hours=3.0, group="initiation",
                 outputs=[TaskOutput("problem_statement", "Problem definition", "document")]),
            Task("task-02", "Data Collection & Preparation", "Collect, clean, and prepare training data",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=10.0, dependencies=["task-01"], group="data",
                 outputs=[TaskOutput("dataset", "Prepared dataset", "data")]),
            Task("task-03", "Exploratory Data Analysis", "Analyze and visualize data patterns",
                 estimated_effort_hours=5.0, dependencies=["task-02"], group="analysis",
                 outputs=[TaskOutput("eda_report", "EDA report", "report")]),
            Task("task-04", "Model Development", "Develop and train ML model",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=12.0, dependencies=["task-03"], group="development",
                 outputs=[TaskOutput("trained_model", "Trained model", "model")]),
            Task("task-05", "Model Evaluation", "Evaluate model performance and tune hyperparameters",
                 estimated_effort_hours=5.0, dependencies=["task-04"], group="quality",
                 outputs=[TaskOutput("eval_report", "Evaluation report", "report")]),
            Task("task-06", "Model Deployment", "Deploy model to production serving infrastructure",
                 estimated_effort_hours=4.0, dependencies=["task-05"], group="delivery",
                 outputs=[TaskOutput("deployed_model", "Deployed model", "deployment")]),
            Task("task-07", "Monitoring Setup", "Setup model monitoring and alerting",
                 estimated_effort_hours=3.0, dependencies=["task-06"], group="delivery",
                 outputs=[TaskOutput("monitoring", "Monitoring dashboard", "dashboard")]),
        ]

    def _devops_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Infrastructure Assessment", "Assess current infrastructure and requirements",
                 estimated_effort_hours=3.0, group="initiation",
                 outputs=[TaskOutput("assessment", "Infrastructure assessment", "document")]),
            Task("task-02", "Design Infrastructure", "Design target infrastructure architecture",
                 estimated_effort_hours=5.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("infra_design", "Infrastructure design", "document")]),
            Task("task-03", "Setup CI/CD Pipeline", "Configure continuous integration and deployment",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=8.0, dependencies=["task-02"], group="development",
                 outputs=[TaskOutput("cicd_config", "CI/CD configuration", "code")]),
            Task("task-04", "Configure Infrastructure", "Provision and configure infrastructure resources",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=10.0, dependencies=["task-02"], group="development",
                 outputs=[TaskOutput("infra_code", "Infrastructure as code", "code")]),
            Task("task-05", "Security & Compliance", "Implement security controls and compliance checks",
                 estimated_effort_hours=6.0, dependencies=["task-04"], group="security",
                 outputs=[TaskOutput("security_report", "Security review", "report")]),
            Task("task-06", "Testing & Validation", "Validate deployment pipeline and infrastructure",
                 estimated_effort_hours=4.0, dependencies=["task-03", "task-04"], group="quality",
                 outputs=[TaskOutput("validation", "Validation report", "report")]),
            Task("task-07", "Go Live & Monitoring", "Deploy to production and setup monitoring",
                 estimated_effort_hours=4.0, dependencies=["task-05", "task-06"], group="delivery",
                 outputs=[TaskOutput("monitoring", "Monitoring system", "deployment")]),
        ]

    def _integration_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Requirements Analysis", "Analyze integration requirements",
                 estimated_effort_hours=3.0, group="initiation",
                 outputs=[TaskOutput("requirements", "Integration requirements", "document")]),
            Task("task-02", "Design Integration Architecture", "Design integration patterns and data flow",
                 estimated_effort_hours=5.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("integration_design", "Integration design", "document")]),
            Task("task-03", "Setup Integration Endpoints", "Configure API endpoints and connections",
                 estimated_effort_hours=4.0, dependencies=["task-02"], group="development",
                 outputs=[TaskOutput("endpoints", "Integration endpoints", "configuration")]),
            Task("task-04", "Implement Workflows", "Implement automation and orchestration workflows",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=10.0, dependencies=["task-02", "task-03"], group="development",
                 outputs=[TaskOutput("workflow_code", "Workflow implementation", "code")]),
            Task("task-05", "Testing", "Test integration scenarios and error handling",
                 estimated_effort_hours=5.0, dependencies=["task-04"], group="quality",
                 outputs=[TaskOutput("test_report", "Test report", "report")]),
            Task("task-06", "Deployment & Documentation", "Deploy integrations and create documentation",
                 estimated_effort_hours=4.0, dependencies=["task-05"], group="delivery",
                 outputs=[TaskOutput("docs", "Integration documentation", "document")]),
        ]

    def _security_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Security Requirements", "Define security requirements and threat model",
                 estimated_effort_hours=4.0, group="initiation",
                 outputs=[TaskOutput("threat_model", "Threat model", "document")]),
            Task("task-02", "Security Architecture Design", "Design security architecture",
                 estimated_effort_hours=6.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("security_architecture", "Security architecture", "document")]),
            Task("task-03", "Implement Authentication", "Implement authentication and authorization",
                 estimated_effort_hours=8.0, dependencies=["task-02"], group="implementation",
                 outputs=[TaskOutput("auth_system", "Authentication system", "code")]),
            Task("task-04", "Implement Encryption", "Implement data encryption at rest and in transit",
                 estimated_effort_hours=6.0, dependencies=["task-02"], group="implementation",
                 outputs=[TaskOutput("encryption", "Encryption implementation", "code")]),
            Task("task-05", "Security Testing", "Execute penetration testing and security scans",
                 estimated_effort_hours=6.0, dependencies=["task-03", "task-04"], group="quality",
                 outputs=[TaskOutput("security_test_report", "Security test report", "report")]),
            Task("task-06", "Compliance Documentation", "Create compliance and audit documentation",
                 estimated_effort_hours=4.0, dependencies=["task-05"], group="delivery",
                 outputs=[TaskOutput("compliance_docs", "Compliance documentation", "document")]),
        ]

    def _general_software_tasks(self, goal: Goal) -> list[Task]:
        return [
            Task("task-01", "Requirements Gathering", "Collect and analyze project requirements",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=4.0, group="initiation",
                 outputs=[TaskOutput("requirements_doc", "Requirements specification", "document")]),
            Task("task-02", "System Design", "Design overall system architecture",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=6.0, dependencies=["task-01"], group="design",
                 outputs=[TaskOutput("design_doc", "System design", "document")]),
            Task("task-03", "Core Implementation", "Implement core system components",
                 task_type=TaskType.HIERARCHICAL, estimated_effort_hours=14.0, dependencies=["task-02"], group="development",
                 outputs=[TaskOutput("core_code", "Core implementation", "code")]),
            Task("task-04", "Integration & Testing", "Integrate components and execute tests",
                 estimated_effort_hours=6.0, dependencies=["task-03"], group="quality",
                 outputs=[TaskOutput("test_report", "Test report", "report")]),
            Task("task-05", "Documentation & Deployment", "Create documentation and deploy",
                 estimated_effort_hours=4.0, dependencies=["task-04"], group="delivery",
                 outputs=[TaskOutput("docs", "Documentation", "document"), TaskOutput("deployment", "Deployed system", "deployment")]),
        ]

    def _link_dependencies(self, tasks: list[Task], goal: Goal) -> None:
        groups: dict[str, list[Task]] = {}
        for t in tasks:
            groups.setdefault(t.group, []).append(t)
        for group_name, group_tasks in groups.items():
            if len(group_tasks) <= 1:
                continue
            for i in range(1, len(group_tasks)):
                dep = group_tasks[i - 1].id
                if dep not in group_tasks[i].dependencies:
                    group_tasks[i].dependencies.append(dep)

    def get_available_templates(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "title": t["title"],
                "description": t["description"],
                "estimated_effort_hours": t["estimated_effort_hours"],
                "outputs": [o["name"] for o in t["outputs"]],
            }
            for name, t in _TASK_TEMPLATES.items()
        }
