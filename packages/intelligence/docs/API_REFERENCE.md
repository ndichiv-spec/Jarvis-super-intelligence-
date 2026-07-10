# Intelligence Core API Reference

## Gateway Endpoints

### GET /intelligence/status
Returns the current status of the Intelligence Engine.

**Response:**
```json
{
    "active_goals": 3,
    "active_plans": 2,
    "policy": "balanced",
    "total_learned": 5,
    "metrics": {
        "total_executions": 10,
        "successful": 8,
        "failed": 2,
        "avg_duration_seconds": 1.5
    }
}
```

### GET /intelligence/context
Returns all active execution contexts.

**Response:**
```json
{
    "contexts": [
        {
            "id": "ctx-123",
            "goal_id": "goal-abc",
            "plan_id": "plan-xyz",
            "session_id": null,
            "workspace_id": "default",
            "reasoning_steps": 3,
            "execution_events": 5
        }
    ],
    "total": 1
}
```

### GET /intelligence/goals
List all goals sorted by priority.

### POST /intelligence/goals
Create a new goal and plan.

**Body:**
```json
{
    "description": "Build authentication module",
    "priority": "high"
}
```

### POST /intelligence/plan
Create a decomposed execution plan.

**Body:**
```json
{
    "description": "Deploy to production",
    "priority": "high",
    "policy": "conservative"
}
```

### POST /intelligence/execute
Execute a goal through the full intelligence pipeline.

**Body:**
```json
{
    "description": "Design, build, test, document, and deploy a complete inventory management platform",
    "priority": "high",
    "policy": "balanced"
}
```

### GET /intelligence/metrics
Returns execution metrics.

### GET /intelligence/plans
List all plans.

### GET /intelligence/plans/{plan_id}
Get detailed plan information including tasks.

### GET /intelligence/policy
Get current execution policy configuration.

### PUT /intelligence/policy
Set execution policy.

**Body:** `{"policy": "aggressive"}`

### GET /intelligence/learning
Get learning records.

## Python API

### IntelligenceEngine

```python
engine = IntelligenceEngine()

# Full goal execution pipeline
result = await engine.execute_goal(
    goal_description="Build the platform",
    priority=GoalPriority.HIGH,
    policy=ExecutionPolicy.BALANCED,
    context={"deadline": "2026-08-01"},
)

# Get engine status
status = engine.get_status()
```

### IntelligencePlanner

```python
planner = IntelligencePlanner()

# Create plan
plan = planner.create_plan("Build system", GoalPriority.HIGH)

# Decompose goal into tasks
plan = planner.decompose_goal(plan.id)

# Add objectives and tasks
planner.add_objective(plan.id, "Achieve 90% coverage")
planner.add_task(plan.id, "Design architecture")
```

### CoordinatorEngine

```python
coordinator = CoordinatorEngine()
report = await coordinator.coordinate(plan_id, task_graph, context)
# report.completed_tasks, report.failed_tasks, report.decisions_made, etc.
```

### EvaluationEngine

```python
evaluator = EvaluationEngine()
result = evaluator.evaluate(
    task_description="Build module",
    result={"duration_seconds": 2.5, "errors": []},
    state=TaskState.COMPLETED,
)
# result.quality_score, result.efficiency_score, result.confidence
```

### LearningEngine

```python
learning = LearningEngine()
learning.record_success(goal, strategy, evaluation)
learning.record_failure(goal, strategy, error)
recommendation = learning.get_recommendation("Build platform")
```
