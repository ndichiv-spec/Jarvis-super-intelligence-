from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import CycleError, DependencyGraph


@dataclass
class ValidationIssue:
    severity: str
    message: str
    location: str = ""
    suggestion: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationResult:
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [i.to_dict() for i in self.issues],
            "issue_count": len(self.issues),
        }


class PlanValidator:
    def validate_goal(self, goal: Goal) -> ValidationResult:
        issues: list[ValidationIssue] = []
        if not goal.objective or not goal.objective.strip():
            issues.append(ValidationIssue("error", "Goal objective is empty", "objective"))
        if len(goal.objective) < 10:
            issues.append(ValidationIssue("warning", "Goal objective is very short, may lack detail", "objective",
                                          "Provide more detail about what you want to build"))
        if goal.ambiguity:
            for a in goal.ambiguity:
                issues.append(ValidationIssue("warning", f"Ambiguous goal: {a}", "objective",
                                              "Clarify the scope and requirements"))
        if not goal.deliverables:
            issues.append(ValidationIssue("warning", "No deliverables specified", "deliverables",
                                          "Define what should be produced"))
        return ValidationResult(valid=len([i for i in issues if i.severity == "error"]) == 0, issues=issues)

    def validate_graph(self, graph: DependencyGraph) -> ValidationResult:
        issues: list[ValidationIssue] = []
        try:
            graph.validate_no_cycles()
        except CycleError as e:
            issues.append(ValidationIssue("error", f"Dependency cycle detected: {' -> '.join(e.cycle)}", "dependencies",
                                          "Remove the circular dependency"))
        for tid, task in graph.tasks.items():
            deps = graph.get_dependencies(tid)
            for dep in deps:
                if dep not in graph.tasks:
                    issues.append(ValidationIssue("error", f"Task '{tid}' depends on missing task '{dep}'",
                                                  f"{tid}.dependencies"))
            if not task.title:
                issues.append(ValidationIssue("warning", f"Task '{tid}' has no title", tid))
            if task.estimated_effort_hours <= 0:
                issues.append(ValidationIssue("warning", f"Task '{tid}' has no estimated effort", tid))
        return ValidationResult(valid=len([i for i in issues if i.severity == "error"]) == 0, issues=issues)

    def validate_tasks(self, tasks: list[Task]) -> ValidationResult:
        graph = DependencyGraph()
        graph.add_tasks(tasks)
        return self.validate_graph(graph)

    def validate_plan_completeness(self, graph: DependencyGraph) -> ValidationResult:
        issues: list[ValidationIssue] = []
        if len(graph.tasks) == 0:
            issues.append(ValidationIssue("error", "Plan has no tasks", "plan"))
        missing_outputs = 0
        for tid, task in graph.tasks.items():
            if not task.outputs:
                missing_outputs += 1
        if missing_outputs > len(graph.tasks) / 2:
            issues.append(ValidationIssue("warning", f"{missing_outputs}/{len(graph.tasks)} tasks lack outputs",
                                          "outputs"))
        return ValidationResult(valid=len([i for i in issues if i.severity == "error"]) == 0, issues=issues)

    def validate_all(self, goal: Goal, graph: DependencyGraph) -> ValidationResult:
        all_issues: list[ValidationIssue] = []
        for v in [self.validate_goal(goal), self.validate_graph(graph), self.validate_plan_completeness(graph)]:
            all_issues.extend(v.issues)
        return ValidationResult(valid=len([i for i in all_issues if i.severity == "error"]) == 0, issues=all_issues)
