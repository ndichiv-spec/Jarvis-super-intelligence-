# Developer Guide

## Getting Started

### Prerequisites
- Python 3.13+
- uv package manager

### Installation

```bash
cd packages/intelligence
uv sync
```

### Running Tests

```bash
cd packages/intelligence
$env:PYTHONPATH="src"
uv run --no-project pytest tests/ -v
```

Run with coverage:

```bash
$env:PYTHONPATH="src"
uv run --no-project pytest tests/ --cov=src/jarvis_intelligence -v
```

## Project Structure

```
packages/intelligence/
├── pyproject.toml
├── src/
│   └── jarvis_intelligence/
│       ├── __init__.py       # Public API exports
│       ├── engine.py         # IntelligenceEngine orchestrator
│       ├── cognition.py      # Goal understanding
│       ├── reasoning.py      # 7 reasoning modes
│       ├── planner.py        # Goal decomposition & planning
│       ├── executor.py       # Task execution
│       ├── coordinator.py    # Multi-task coordination
│       ├── decision.py       # Decision engine
│       ├── goals.py          # Goal model & manager
│       ├── objectives.py     # Objective model
│       ├── tasks.py          # Task model & task graph
│       ├── context.py        # Execution context manager
│       ├── strategies.py     # Strategy selection
│       ├── evaluator.py      # Task evaluation
│       ├── optimizer.py      # Continuous optimization
│       ├── learning.py       # Learning & memory
│       ├── confidence.py     # Confidence scoring
│       ├── priorities.py     # Priority assessment
│       ├── scheduler.py      # Task scheduling
│       ├── policies.py       # Execution policies
│       ├── safety.py         # Safety validation
│       └── telemetry.py      # Metrics & telemetry
├── tests/
│   ├── test_cognition.py
│   ├── test_confidence.py
│   ├── test_context.py
│   ├── test_coordinator.py
│   ├── test_decision.py
│   ├── test_engine.py
│   ├── test_evaluator.py
│   ├── test_executor.py
│   ├── test_goals.py
│   ├── test_learning.py
│   ├── test_objectives.py
│   ├── test_optimizer.py
│   ├── test_planner.py
│   ├── test_policies.py
│   ├── test_priorities.py
│   ├── test_reasoning.py
│   ├── test_safety.py
│   ├── test_scheduler.py
│   ├── test_strategies.py
│   ├── test_tasks.py
│   ├── test_telemetry.py
│   └── test_validation_scenario.py
└── docs/
    ├── ARCHITECTURE.md
    ├── GOAL_MODEL.md
    ├── REASONING_GUIDE.md
    ├── DECISION_GUIDE.md
    ├── OPTIMIZATION_GUIDE.md
    ├── API_REFERENCE.md
    └── DEVELOPER_GUIDE.md
```

## Gateway Integration

The Intelligence Core APIs are exposed through the JARVIS Gateway:

```
packages/api/src/jarvis_api/gateway/routes/intelligence.py
```

Routes are registered in `packages/api/src/jarvis_api/gateway/app.py`.

## Frontend Integration

### Home Dashboard
```
packages/home/src/app/intelligence/page.tsx
```
Provides dashboard with active goals, plans, execution metrics, and goal execution.

### Studio Workspace
```
packages/studio/src/app/intelligence/page.tsx
```
Provides workspace with advanced execution controls, learning records, and detailed monitoring.

## Adding New Features

1. Add the feature module in `src/jarvis_intelligence/`
2. Export it from `__init__.py`
3. Integrate it into `IntelligenceEngine` in `engine.py`
4. Add gateway routes in the API package
5. Write comprehensive tests
6. Update documentation
