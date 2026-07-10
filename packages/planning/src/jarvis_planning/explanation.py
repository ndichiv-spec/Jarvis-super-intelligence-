from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_planning.analyzer import Goal
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.executor import Executor
from jarvis_planning.monitor import ProgressMonitor
from jarvis_planning.reasoning import ReasoningEngine
from jarvis_planning.scheduler import Scheduler


@dataclass
class ExplanationSection:
    title: str
    content: str
    details: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "content": self.content, "details": self.details}


@dataclass
class Explanation:
    sections: list[ExplanationSection] = field(default_factory=list)

    def add_section(self, title: str, content: str, details: list[str] | None = None) -> None:
        self.sections.append(ExplanationSection(title, content, details or []))

    def to_text(self) -> str:
        lines: list[str] = []
        for section in self.sections:
            lines.append(f"\n## {section.title}")
            lines.append(f"\n{section.content}")
            for detail in section.details:
                lines.append(f"  - {detail}")
        return "\n".join(lines).strip()

    def to_dict(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.sections]


class ExplanationEngine:
    def __init__(self, reasoning: ReasoningEngine) -> None:
        self._reasoning = reasoning

    def generate_goal_summary(self, goal: Goal) -> Explanation:
        exp = Explanation()
        exp.add_section(
            "Goal",
            f"**Objective:** {goal.objective}",
            [f"Category: {goal.category}", f"Complexity: {goal.complexity.value}",
             f"Estimated Duration: {goal.estimated_duration}", f"Risk Level: {goal.risk_level}",
             f"Confidence: {goal.confidence:.0%}"],
        )
        if goal.required_knowledge:
            exp.add_section(
                "Required Knowledge",
                f"This plan requires expertise in {len(goal.required_knowledge)} domains.",
                [f"- {k}" for k in goal.required_knowledge],
            )
        if goal.constraints:
            exp.add_section(
                "Constraints",
                f"{len(goal.constraints)} constraints identified.",
                [f"- {c}" for c in goal.constraints],
            )
        return exp

    def generate_plan_summary(self, goal: Goal, graph: DependencyGraph, scheduler: Scheduler) -> Explanation:
        exp = self.generate_goal_summary(goal)
        tasks = list(graph.tasks.values())
        exp.add_section(
            "Execution Plan",
            f"The plan consists of {len(tasks)} tasks organized into a structured workflow.",
            [f"  {t.id}: {t.title} ({t.estimated_effort_hours}h)" for t in tasks],
        )
        try:
            levels = graph.get_levels()
            for i, level in enumerate(levels):
                level_tasks = [f"{tid} ({graph.tasks[tid].title})" for tid in level]
                exp.add_section(f"Execution Level {i + 1}", f"{len(level)} tasks", level_tasks)
        except Exception:
            pass
        try:
            cp = graph.critical_path()
            cp_titles = [graph.tasks[t].title for t in cp]
            total_hours = sum(graph.tasks[t].estimated_effort_hours for t in cp)
            exp.add_section("Critical Path", f"Total critical path: {total_hours}h",
                            [f"  {t} ->" for t in cp_titles[:-1]] + [f"  {cp_titles[-1]}"])
        except Exception:
            pass
        schedule = scheduler.schedule()
        exp.add_section(
            "Execution Status",
            f"{len(schedule.completed_tasks)} completed, {len(schedule.running_tasks)} running, "
            f"{len(schedule.ready_queue)} ready, {len(schedule.waiting_tasks)} waiting, "
            f"{len(schedule.blocked_tasks)} blocked",
        )
        return exp

    def generate_progress_summary(self, monitor: ProgressMonitor) -> Explanation:
        progress = monitor.get_progress()
        exp = Explanation()
        exp.add_section(
            "Progress",
            f"Plan {progress.plan_id}: {progress.completion_percentage}% complete",
            [f"Completed: {progress.completed_tasks}/{progress.total_tasks}",
             f"Running: {progress.running_tasks}", f"Failed: {progress.failed_tasks}",
             f"Elapsed: {progress.elapsed_seconds:.0f}s",
             f"Estimated remaining: {progress.estimated_remaining_seconds:.0f}s"],
        )
        if progress.active_task:
            exp.add_section("Current Activity", f"Active: {progress.active_task}")
        if progress.last_event:
            exp.add_section("Recent Event", progress.last_event)
        return exp

    def generate_completion_summary(self, goal: Goal, graph: DependencyGraph, executor: Executor) -> Explanation:
        exp = Explanation()
        results = executor.get_all_results()
        success_count = sum(1 for r in results.values() if r.success)
        fail_count = sum(1 for r in results.values() if not r.success)
        exp.add_section(
            "Plan Complete",
            f"Goal: {goal.objective}",
            [f"Tasks: {len(results)} total", f"Successful: {success_count}",
             f"Failed: {fail_count}", f"Plan confidence: {goal.confidence:.0%}"],
        )
        if results:
            total_duration = sum(r.duration_seconds for r in results.values() if r.duration_seconds)
            exp.add_section("Execution Summary", f"Total execution time: {total_duration:.1f}s")
        return exp

    def explain_decision(self, title: str, reasoning: str, details: list[str] | None = None) -> Explanation:
        exp = Explanation()
        exp.add_section(title, reasoning, details)
        return exp
