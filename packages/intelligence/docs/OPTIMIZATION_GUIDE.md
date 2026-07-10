# Optimization Guide

## Overview

The OptimizerEngine continuously improves planning quality, agent selection, task ordering, retry strategies, and workflow efficiency.

## Optimization Areas

### Task Order Optimization
- Detects tasks with excessive dependencies
- Suggests parallelization opportunities
- Reduces overall execution time

### Agent Selection Optimization
- Evaluates execution quality scores
- Recommends alternative agents when quality is low
- Tracks agent performance history

### Retry Strategy Optimization
- Analyzes failure patterns
- Suggests adjusted retry limits
- Recommends fallback strategies

### Workflow Efficiency
- Identifies bottleneck tasks
- Suggests workflow restructuring
- Measures resource utilization

## Usage

```python
from jarvis_intelligence import OptimizerEngine
from jarvis_intelligence.tasks import TaskGraph

engine = OptimizerEngine()
graph = TaskGraph()

# Optimize task ordering
suggestions = engine.optimize_task_order(graph)

# Evaluate agent performance
from jarvis_intelligence.evaluator import EvaluationResult
eval_result = EvaluationResult(
    task_id="t1", success=True,
    quality_score=0.4, efficiency_score=0.3,
    confidence=0.35,
)
agent_suggestions = engine.optimize_agent_selection(eval_result)

# Analyze retry strategy
task = Task.create(description="Failed task")
suggestion = engine.optimize_retry_strategy(task)
```

## Suggestion Types

| Type        | Description                    | Impact  | Effort  |
|-------------|--------------------------------|---------|---------|
| dependency  | Parallelize dependencies       | medium  | low     |
| agent       | Switch to better agent         | high    | medium  |
| retry       | Adjust retry configuration     | medium  | low     |
| workflow    | Restructure execution flow     | high    | high    |
