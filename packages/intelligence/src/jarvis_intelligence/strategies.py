from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class StrategyType(StrEnum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    FAN_OUT = "fan_out"
    FAN_IN = "fan_in"
    CONDITIONAL = "conditional"
    ITERATIVE = "iterative"
    HIERARCHICAL = "hierarchical"
    OPPORTUNISTIC = "opportunistic"


@dataclass(frozen=True, slots=True)
class Strategy:
    id: str
    type: StrategyType
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    conditions: tuple[str, ...] = ()
    risk_level: str = "low"
    expected_duration_seconds: float | None = None

    @classmethod
    def sequential(cls, name: str = "Sequential", description: str = "Execute tasks one after another") -> Strategy:
        return cls(id="strat-seq", type=StrategyType.SEQUENTIAL, name=name, description=description)

    @classmethod
    def parallel(cls, name: str = "Parallel", description: str = "Execute tasks concurrently") -> Strategy:
        return cls(id="strat-par", type=StrategyType.PARALLEL, name=name, description=description)

    @classmethod
    def hierarchical(cls, name: str = "Hierarchical", description: str = "Break down top-down") -> Strategy:
        return cls(id="strat-hier", type=StrategyType.HIERARCHICAL, name=name, description=description)


class StrategySelector:
    def select(self, goal_description: str, complexity: str, capabilities: tuple[str, ...]) -> Strategy:
        if complexity == "simple":
            return Strategy.sequential()
        elif complexity == "complex":
            return Strategy.hierarchical()
        elif complexity == "concurrent":
            return Strategy.parallel()
        else:
            return Strategy.sequential()
