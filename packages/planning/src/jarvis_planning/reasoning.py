from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_planning.analyzer import Goal
from jarvis_planning.decomposer import Task
from jarvis_planning.dependency_graph import DependencyGraph
from jarvis_planning.scheduler import Scheduler


@dataclass
class ReasoningStep:
    type: str
    content: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "content": self.content, "details": self.details}


@dataclass
class ReasoningChain:
    steps: list[ReasoningStep] = field(default_factory=list)

    def add(self, step_type: str, content: str, details: dict[str, Any] | None = None) -> None:
        self.steps.append(ReasoningStep(step_type, content, details or {}))

    def to_dict(self) -> list[dict[str, Any]]:
        return [s.to_dict() for s in self.steps]


class ReasoningEngine:
    def __init__(self) -> None:
        self._chains: dict[str, ReasoningChain] = {}

    def analyze_goal(self, goal: Goal) -> ReasoningChain:
        chain = ReasoningChain()
        chain.add("objective_analysis", f"Analyzed objective: '{goal.objective}'",
                   {"word_count": len(goal.objective.split())})
        chain.add("category_detection", f"Detected category: {goal.category}",
                   {"category": goal.category})
        chain.add("complexity_assessment", f"Assessed complexity: {goal.complexity.value}",
                   {"complexity": goal.complexity.value, "confidence": goal.confidence})
        if goal.ambiguity:
            chain.add("ambiguity_detection", f"Detected ambiguity: {', '.join(goal.ambiguity)}",
                       {"ambiguities": goal.ambiguity})
        chain.add("knowledge_requirements", f"Required expertise: {', '.join(goal.required_knowledge)}",
                   {"domains": goal.required_knowledge})
        chain.add("risk_assessment", f"Risk level: {goal.risk_level}",
                   {"risk": goal.risk_level, "confidence": goal.confidence})
        self._chains["goal_analysis"] = chain
        return chain

    def analyze_task_decomposition(self, tasks: list[Task]) -> ReasoningChain:
        chain = ReasoningChain()
        chain.add("decomposition", f"Decomposed into {len(tasks)} tasks",
                   {"task_count": len(tasks)})
        milestones = [t for t in tasks if t.task_type.value == "milestone"]
        if milestones:
            chain.add("milestones", f"Created {len(milestones)} milestones",
                       {"milestones": [m.title for m in milestones]})
        parallel_groups = set()
        for t in tasks:
            if t.group:
                parallel_groups.add(t.group)
        chain.add("execution_groups", f"Organized into {len(parallel_groups)} execution groups",
                   {"groups": list(parallel_groups)})
        total_effort = sum(t.estimated_effort_hours for t in tasks)
        chain.add("effort_estimation", f"Total estimated effort: {total_effort} hours",
                   {"total_hours": total_effort})
        self._chains["decomposition"] = chain
        return chain

    def analyze_dependency_graph(self, graph: DependencyGraph, scheduler: Scheduler) -> ReasoningChain:
        chain = ReasoningChain()
        try:
            levels = graph.get_levels()
            chain.add("dependency_structure", f"Built dependency graph with {len(graph.tasks)} tasks across {len(levels)} execution levels",
                       {"levels": len(levels), "tasks": len(graph.tasks)})
            cp = graph.critical_path()
            cp_titles = [graph.tasks[t].title for t in cp]
            chain.add("critical_path", f"Identified critical path: {' -> '.join(cp_titles)}",
                       {"path": cp, "titles": cp_titles})
            deps_count = sum(len(deps) for deps in graph.edges.values())
            chain.add("dependency_count", f"Established {deps_count} dependency relationships",
                       {"total_dependencies": deps_count})
        except Exception as e:
            chain.add("validation", f"Dependency validation issue: {e}")
        self._chains["dependencies"] = chain
        return chain

    def analyze_schedule(self, scheduler: Scheduler) -> ReasoningChain:
        chain = ReasoningChain()
        schedule = scheduler.schedule()
        chain.add("schedule", f"Scheduled execution: {len(schedule.ready_queue)} ready, {len(schedule.running_tasks)} running, {len(schedule.waiting_tasks)} waiting, {len(schedule.blocked_tasks)} blocked",
                   {"ready": len(schedule.ready_queue), "running": len(schedule.running_tasks),
                    "waiting": len(schedule.waiting_tasks), "blocked": len(schedule.blocked_tasks),
                    "completed": len(schedule.completed_tasks), "failed": len(schedule.failed_tasks)})
        capacities = scheduler.get_available_capacity()
        chain.add("capacity", f"Available execution capacity: {capacities} slots",
                   {"available_capacity": capacities})
        self._chains["schedule"] = chain
        return chain

    def get_chain(self, name: str) -> ReasoningChain | None:
        return self._chains.get(name)

    def get_all_chains(self) -> dict[str, ReasoningChain]:
        return dict(self._chains)

    def clear(self) -> None:
        self._chains.clear()
