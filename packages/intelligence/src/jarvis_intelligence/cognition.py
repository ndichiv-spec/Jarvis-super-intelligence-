from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from jarvis_intelligence.reasoning import ReasoningEngine, ReasoningMode, ReasoningResult


@dataclass
class CognitionState:
    understanding: str = ""
    intent: str = ""
    reasoning_result: ReasoningResult | None = None
    complexity: str = "moderate"
    key_entities: list[str] = field(default_factory=list)
    constraints_identified: list[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class CognitionEngine:
    def __init__(self, reasoning_engine: ReasoningEngine | None = None) -> None:
        self._reasoning = reasoning_engine or ReasoningEngine()
        self._states: dict[str, CognitionState] = {}

    def process(self, goal_description: str, context: dict[str, Any] | None = None) -> CognitionState:
        state = CognitionState()

        state.understanding = self._analyze_goal(goal_description)
        state.intent = self._determine_intent(goal_description)
        state.complexity = self._assess_complexity(goal_description)

        reasoning = self._reasoning.reason(
            context=f"Goal: {goal_description} | Understanding: {state.understanding} | Intent: {state.intent}",
            mode=ReasoningMode.ANALYTICAL,
        )
        state.reasoning_result = reasoning
        state.confidence = reasoning.confidence

        state.key_entities = self._extract_entities(goal_description)
        state.constraints_identified = self._identify_constraints(goal_description, context)

        state_id = f"cog-{datetime.now(UTC).timestamp()}"
        self._states[state_id] = state
        return state

    def _analyze_goal(self, description: str) -> str:
        prefixes = ["design", "build", "create", "develop", "implement", "deploy", "test", "analyze", "research", "optimize"]
        words = description.lower().split()
        detected = [w for w in words if w in prefixes]
        if detected:
            return f"User wants to {detected[0]}: {description[:120]}"
        return f"Process goal: {description[:120]}"

    def _determine_intent(self, description: str) -> str:
        lower = description.lower()
        if any(w in lower for w in ["design", "architect", "plan"]):
            return "design_and_plan"
        if any(w in lower for w in ["build", "create", "implement", "develop", "code"]):
            return "build_and_implement"
        if any(w in lower for w in ["test", "validate", "verify"]):
            return "test_and_validate"
        if any(w in lower for w in ["deploy", "release", "publish", "launch"]):
            return "deploy_and_release"
        if any(w in lower for w in ["analyze", "research", "investigate"]):
            return "analyze_and_research"
        if any(w in lower for w in ["optimize", "improve", "refactor"]):
            return "optimize_and_improve"
        return "general_execution"

    def _assess_complexity(self, description: str) -> str:
        length = len(description)
        comma_count = description.count(",")
        and_count = description.count(" and ")
        score = length / 50 + comma_count * 2 + and_count * 3
        if score < 3:
            return "simple"
        if score < 8:
            return "moderate"
        return "complex"

    def _extract_entities(self, description: str) -> list[str]:
        keywords = ["platform", "system", "application", "api", "service", "pipeline", "dashboard", "module", "integration", "database", "frontend", "backend", "tool", "library", "framework", "agent", "workflow", "report"]
        found: list[str] = []
        words = description.lower().split()
        for word in words:
            word_clean = word.strip(",.;:!?")
            if word_clean in keywords and word_clean not in found:
                found.append(word_clean)
        return found

    def _identify_constraints(self, description: str, context: dict[str, Any] | None) -> list[str]:
        constraints: list[str] = []
        if context:
            if "deadline" in context:
                constraints.append(f"Deadline: {context['deadline']}")
            if "budget" in context:
                constraints.append(f"Budget: {context['budget']}")
        return constraints
