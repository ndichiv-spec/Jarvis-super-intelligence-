from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_intelligence.tasks import Task, TaskGraph, TaskState
from jarvis_intelligence.evaluator import EvaluationResult


@dataclass
class OptimizationSuggestion:
    type: str
    description: str
    impact: str
    effort: str
    target_id: str | None = None


class OptimizerEngine:
    def __init__(self) -> None:
        self._suggestions: list[OptimizationSuggestion] = []

    def optimize_task_order(self, graph: TaskGraph) -> list[OptimizationSuggestion]:
        suggestions: list[OptimizationSuggestion] = []
        tasks = graph.all()
        for task in tasks:
            if len(task.depends_on) > 3:
                suggestions.append(OptimizationSuggestion(
                    type="dependency",
                    description=f"Task {task.id} has {len(task.depends_on)} dependencies — consider parallelizing",
                    impact="medium",
                    effort="low",
                    target_id=task.id,
                ))
        self._suggestions.extend(suggestions)
        return suggestions

    def optimize_agent_selection(self, evaluation: EvaluationResult) -> list[OptimizationSuggestion]:
        suggestions: list[OptimizationSuggestion] = []
        if evaluation.quality_score < 0.5:
            suggestions.append(OptimizationSuggestion(
                type="agent",
                description="Consider alternative agent with higher capability match",
                impact="high",
                effort="medium",
            ))
        return suggestions

    def optimize_retry_strategy(self, task: Task) -> OptimizationSuggestion | None:
        if task.state == TaskState.FAILED and task.retry_count >= task.max_retries:
            return OptimizationSuggestion(
                type="retry",
                description=f"Increase max_retries for task {task.id} or implement fallback",
                impact="medium",
                effort="low",
                target_id=task.id,
            )
        return None

    def get_all_suggestions(self) -> list[OptimizationSuggestion]:
        return list(self._suggestions)
