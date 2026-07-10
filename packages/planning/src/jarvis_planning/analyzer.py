from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jarvis_planning.estimator import Complexity, Estimate, Estimator


@dataclass
class Goal:
    objective: str
    category: str = ""
    complexity: Complexity = Complexity.MODERATE
    required_knowledge: list[str] = field(default_factory=list)
    estimated_duration: str = ""
    constraints: list[str] = field(default_factory=list)
    deliverables: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    risk_level: str = "low"
    ambiguity: list[str] = field(default_factory=list)
    estimate: Estimate | None = None
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "category": self.category,
            "complexity": self.complexity.value,
            "required_knowledge": self.required_knowledge,
            "estimated_duration": self.estimated_duration,
            "constraints": self.constraints,
            "deliverables": self.deliverables,
            "dependencies": self.dependencies,
            "risk_level": self.risk_level,
            "ambiguity": self.ambiguity,
            "estimate": self.estimate.to_dict() if self.estimate else None,
            "confidence": self.confidence,
        }


_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "application": ["app", "application", "software", "system", "platform", "tool"],
    "web": ["web", "website", "portal", "frontend", "backend", "full-stack", "api"],
    "mobile": ["mobile", "ios", "android", "cross-platform"],
    "data": ["database", "data", "analytics", "reporting", "etl", "pipeline", "warehouse"],
    "devops": ["deploy", "ci/cd", "infrastructure", "cloud", "kubernetes", "docker"],
    "ai-ml": ["ai", "machine-learning", "deep-learning", "nlp", "model", "neural", "intelligence"],
    "automation": ["automation", "workflow", "orchestration", "pipeline"],
    "security": ["security", "authentication", "authorization", "encryption", "compliance"],
    "integration": ["integration", "api", "connect", "sync", "migration"],
}

_AMBIGUITY_PATTERNS: list[tuple[str, str]] = [
    ("vague", r"\b(something|stuff|things|make|do|build)\b"),
    ("unclear_scope", r"\b(etc\.|etc|and so on|and more)\b"),
    ("missing_platform", r"\b(app|application|system|tool)\b(?!\s+(for|to|that|which))"),
    ("missing_users", r"\b(without mentioning users|no users|single-user)\b"),
    ("no_constraints", r"\b(no constraints|no requirements|whatever|anything)\b"),
]

_EXPERTISE_DOMAINS: list[str] = [
    "software_architecture", "backend_development", "frontend_development",
    "database_design", "devops", "security", "ui_ux_design", "api_design",
    "testing", "project_management", "cloud_infrastructure", "mobile_development",
    "data_engineering", "machine_learning", "system_integration",
]

_COMMON_CONSTRAINTS: list[str] = [
    "performance", "security", "scalability", "maintainability",
    "usability", "reliability", "cost", "time_to_market",
]

_COMMON_DELIVERABLES: list[str] = [
    "architecture_document", "api_specification", "source_code",
    "test_suite", "deployment_scripts", "user_documentation",
    "technical_documentation", "monitoring_dashboard",
]


class GoalAnalyzer:
    def __init__(self, estimator: Estimator | None = None) -> None:
        self._estimator = estimator or Estimator()

    def analyze(self, objective: str) -> Goal:
        text = objective.lower()
        category = self._detect_category(text)
        ambiguity = self._detect_ambiguity(objective)
        required_knowledge = self._determine_knowledge(category, text)
        constraints = self._suggest_constraints(text)
        deliverables = self._suggest_deliverables(category, text)
        dependencies = self._suggest_dependencies(category)
        estimate = self._estimator.estimate(objective, domain=category, known_factors=required_knowledge)
        goal = Goal(
            objective=objective,
            category=category,
            complexity=estimate.complexity,
            required_knowledge=required_knowledge,
            estimated_duration=estimate.duration_text,
            constraints=constraints,
            deliverables=deliverables,
            dependencies=dependencies,
            risk_level=estimate.risk_level,
            ambiguity=ambiguity,
            estimate=estimate,
            confidence=estimate.confidence,
        )
        return goal

    def _detect_category(self, text: str) -> str:
        scores: dict[str, int] = {}
        for category, keywords in _CATEGORY_KEYWORDS.items():
            scores[category] = sum(1 for kw in keywords if kw in text)
        if not scores or max(scores.values()) == 0:
            return "general"
        return max(scores, key=scores.get)

    def _detect_ambiguity(self, objective: str) -> list[str]:
        import re
        issues: list[str] = []
        for label, pattern in _AMBIGUITY_PATTERNS:
            if re.search(pattern, objective, re.IGNORECASE):
                issues.append(label)
        return issues

    def _determine_knowledge(self, category: str, text: str) -> list[str]:
        domain_map: dict[str, list[str]] = {
            "application": ["software_architecture", "backend_development", "frontend_development"],
            "web": ["backend_development", "frontend_development", "api_design", "ui_ux_design"],
            "mobile": ["mobile_development", "api_design", "ui_ux_design"],
            "data": ["database_design", "data_engineering", "software_architecture"],
            "devops": ["devops", "cloud_infrastructure", "system_integration"],
            "ai-ml": ["machine_learning", "data_engineering", "software_architecture"],
            "automation": ["system_integration", "devops", "software_architecture"],
            "security": ["security", "software_architecture", "system_integration"],
            "integration": ["system_integration", "api_design", "backend_development"],
        }
        result = domain_map.get(category, ["software_architecture"])
        general = [d for d in _EXPERTISE_DOMAINS if d not in result]
        result.extend(general[:3])
        return result

    def _suggest_constraints(self, text: str) -> list[str]:
        present = [c for c in _COMMON_CONSTRAINTS if c in text]
        if not present:
            return _COMMON_CONSTRAINTS[:3]
        return present + [c for c in _COMMON_CONSTRAINTS if c not in present][:2]

    def _suggest_deliverables(self, category: str, text: str) -> list[str]:
        base = list(_COMMON_DELIVERABLES)
        if category == "web":
            base.extend(["responsive_design", "browser_compatibility"])
        elif category == "mobile":
            base.extend(["app_store_package", "push_notifications"])
        elif category == "ai-ml":
            base.extend(["trained_model", "evaluation_report"])
        return base

    def _suggest_dependencies(self, category: str) -> list[str]:
        deps_map: dict[str, list[str]] = {
            "application": ["requirements", "architecture_approval"],
            "web": ["requirements", "design_approval", "api_contract"],
            "mobile": ["requirements", "design_approval", "api_contract"],
            "data": ["requirements", "data_access", "schema_approval"],
            "devops": ["infrastructure_access", "security_review"],
            "ai-ml": ["requirements", "data_access", "model_approval"],
            "automation": ["requirements", "workflow_approval"],
            "security": ["requirements", "architecture_review"],
            "integration": ["requirements", "api_contract", "access_approval"],
        }
        return deps_map.get(category, ["requirements"])
