# Reasoning Engine Guide

## Overview

The ReasoningEngine provides 7 distinct reasoning modes for analyzing problems and generating conclusions.

## Reasoning Modes

### 1. Analytical
Breaks down problems into facts, evaluates patterns, and draws conclusions.
- **Confidence**: 0.85
- **Steps**: identify_facts, evaluate_patterns, draw_conclusions
- **Best for**: Data analysis, problem diagnosis

### 2. Sequential
Creates step-by-step execution plans.
- **Confidence**: 0.80
- **Steps**: step_1, step_2, ..., step_n
- **Best for**: Procedural tasks, ordered workflows

### 3. Strategic
Evaluates resources, options, and selects optimal strategy.
- **Confidence**: 0.75
- **Steps**: assess_resources, evaluate_options, select_strategy
- **Best for**: High-level planning, resource allocation

### 4. Comparative
Identifies options, evaluates criteria, and ranks alternatives.
- **Confidence**: 0.70
- **Steps**: identify_options, evaluate_criteria, rank
- **Best for**: Tool selection, technology choices

### 5. Reflective
Reviews execution history, identifies patterns, extracts lessons.
- **Confidence**: 0.60
- **Steps**: review_history, identify_patterns, extract_lessons
- **Best for**: Post-mortems, improvement cycles

### 6. Constraint-Based
Identifies constraints, maps solutions, validates against boundaries.
- **Confidence**: 0.65
- **Steps**: identify_constraints, map_solutions, validate
- **Best for**: Resource-constrained planning

### 7. Multi-Step
Decomposes complex problems into ordered execution sequences.
- **Confidence**: 0.72
- **Steps**: decompose, order, execute_sequence
- **Best for**: Complex, multi-stage goals

## Usage

```python
from jarvis_intelligence import ReasoningEngine, ReasoningMode

engine = ReasoningEngine()

# Default (analytical)
result = engine.reason("Analyze system performance")

# Specific mode
result = engine.reason("Plan deployment", ReasoningMode.SEQUENTIAL)

# With constraints
result = engine.reason(
    "Design solution",
    ReasoningMode.CONSTRAINT_BASED,
    constraints=("budget_under_10k", "timeline_2_weeks"),
)
```

## ReasoningResult Fields

- `mode` - The reasoning mode used
- `conclusion` - Text summary of the reasoning
- `confidence` - Confidence score (0-1)
- `steps` - The reasoning steps taken
- `alternatives` - Alternative approaches considered
- `assumptions` - Assumptions made during reasoning
- `risks` - Identified risks
- `metadata` - Additional context
