# Planner API Reference

## Gateway REST Endpoints

All planning endpoints are exposed through the Gateway at `/gateway/planning`.

### Create Full Plan

```
POST /planning/create
```

**Request Body:**
```json
{
  "objective": "Build a professional inventory management platform",
  "templates": ["gather_requirements", "design_architecture"]
}
```

**Response:**
```json
{
  "plan_id": "uuid",
  "objective": "...",
  "status": "executing",
  "goal": { ... },
  "tasks": [ ... ],
  "graph": { ... }
}
```

### Analyze Goal

```
POST /planning/analyze
```

**Request Body:**
```json
{
  "objective": "Build a web application"
}
```

**Response:**
```json
{
  "plan_id": "uuid",
  "goal": {
    "objective": "Build a web application",
    "category": "web",
    "complexity": "moderate",
    "required_knowledge": ["backend_development", ...],
    "estimated_duration": "days",
    "constraints": ["performance", "security", "scalability"],
    "deliverables": ["source_code", "test_suite", ...],
    "risk_level": "low",
    "ambiguity": [],
    "confidence": 0.7
  },
  "validation": { ... }
}
```

### Decompose Goal

```
POST /planning/decompose
```

**Request Body:**
```json
{
  "objective": "Build a web application",
  "templates": []
}
```

### Execute Plan

```
POST /planning/execute
```

**Request Body:**
```json
{
  "plan_id": "uuid"
}
```

### Replan

```
POST /planning/replan
```

**Request Body:**
```json
{
  "plan_id": "uuid",
  "reason": "task_failure",
  "context": {
    "task_id": "task-03",
    "alternative": "retry_with_timeout"
  }
}
```

### Get Plan

```
GET /planning/{plan_id}
```

### Get Graph

```
GET /planning/{plan_id}/graph
```

### Get Status

```
GET /planning/{plan_id}/status
```

### List Plans

```
GET /planning/
```

## Python API

### Planner

```python
from jarvis_planning import Planner

planner = Planner()

# Full pipeline
plan = planner.full_plan("Build an inventory platform")

# Step-by-step
plan = planner.create_plan("Build an app")
plan = planner.analyze(plan.id)
plan = planner.decompose(plan.id)
planner.assign_agents(plan.id)
plan = planner.validate(plan.id)
plan = planner.prepare_execution(plan.id)
plan = planner.execute_all(plan.id)

# Progress and explanation
progress = planner.get_progress(plan.id)
explanation = planner.get_explanation(plan.id)
summary = planner.get_completion_summary(plan.id)
```

**Constructor Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `analyzer` | `GoalAnalyzer` | New instance | Goal analysis engine |
| `decomposer` | `TaskDecomposer` | New instance | Task decomposition engine |
| `validator` | `PlanValidator` | New instance | Plan validation engine |
| `reasoning` | `ReasoningEngine` | New instance | Reasoning chain engine |
| `explanation` | `ExplanationEngine` | New instance | Human-readable explanation |
| `event_bus` | `EventBus` | New instance | Pub-sub event system |
| `agent_assigner` | `AgentAssigner` | None | AgentKernel integration |
| `memory_connector` | `MemoryConnector` | None | MemoryKernel integration |

**Methods:**
| Method | Returns | Description |
|--------|---------|-------------|
| `create_plan(objective)` | `Plan` | Create a new plan |
| `analyze(plan_id)` | `Plan` | Analyze goal objective |
| `decompose(plan_id, templates)` | `Plan` | Decompose goal into tasks |
| `validate(plan_id)` | `Plan` | Validate plan completeness |
| `prepare_execution(plan_id, policy)` | `Plan` | Create scheduler and executor |
| `execute_next(plan_id)` | `Plan` | Execute next ready task |
| `execute_all(plan_id)` | `Plan` | Execute all tasks |
| `replan(plan_id, reason, context)` | `ReplanResult` | Dynamic replanning |
| `assign_agents(plan_id, strategy)` | `list[AgentAssignment]` | Auto-assign agents |
| `cancel_plan(plan_id)` | `Plan` | Cancel a plan |
| `get_plan(plan_id)` | `Plan` | Get plan by ID |
| `get_progress(plan_id)` | `ProgressReport` | Get execution progress |
| `get_explanation(plan_id)` | `Explanation` | Get human-readable plan |
| `get_completion_summary(plan_id)` | `Explanation` | Get completion summary |
| `store_to_memory(plan_id)` | `MemoryRecord` | Persist plan to memory |
| `store_execution_to_memory(plan_id)` | `MemoryRecord` | Persist execution results |
| `retrieve_similar_plans(objective)` | `list[MemoryRecord]` | Find similar past plans |
| `register_executor(plan_id, type, func)` | None | Register custom executor |
| `list_plans()` | `list[dict]` | List all plans |
| `full_plan(objective, templates)` | `Plan` | Full pipeline end-to-end |

### Plan

```python
@dataclass
class Plan:
    id: str
    objective: str
    status: str  # CREATED, ANALYZED, DECOMPOSED, VALIDATED, EXECUTING, COMPLETED, FAILED, CANCELLED, REPLANNED
    goal: Goal | None
    tasks: list[Task]
    graph: DependencyGraph | None
    scheduler: Scheduler | None
    validation: ValidationResult | None
    created_at: datetime
    updated_at: datetime
    metadata: dict
```

### Goal

```python
@dataclass
class Goal:
    objective: str
    category: str
    complexity: Complexity
    required_knowledge: list[str]
    estimated_duration: str
    constraints: list[str]
    deliverables: list[str]
    dependencies: list[str]
    risk_level: str
    ambiguity: list[str]
    estimate: Estimate | None
    confidence: float
```

### Task

```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    task_type: TaskType  # HIERARCHICAL, RECURSIVE, MILESTONE, PARALLEL, SEQUENTIAL, ATOMIC
    inputs: list[TaskInput]
    outputs: list[TaskOutput]
    dependencies: list[str]
    priority: int
    assigned_agent: str
    estimated_effort_hours: float
    retry_policy: RetryPolicy
    completion_criteria: CompletionCriteria
    metadata: dict
    group: str
```

### ExecutionPolicy

```python
@dataclass
class ExecutionPolicy:
    max_concurrent_tasks: int = 5
    allow_parallel: bool = True
    require_agent_approval: bool = False
    timeout_seconds: float | None = None
    retry_policy: RetryPolicy = RetryPolicy()
    completion_criteria: CompletionCriteria = CompletionCriteria()
```

### AgentAssignment

```python
@dataclass
class AgentAssignment:
    task_id: str
    agent_id: str
    agent_name: str
    confidence: float
    strategy: AssignmentStrategy
    capability_matched: str
```

### TaskState Transitions

```
PLANNED   -> READY, CANCELLED
READY     -> RUNNING, WAITING, BLOCKED, CANCELLED
RUNNING   -> WAITING, BLOCKED, COMPLETED, FAILED, CANCELLED
WAITING   -> READY, BLOCKED, CANCELLED, FAILED
BLOCKED   -> READY, WAITING, CANCELLED, FAILED
FAILED    -> (terminal)
CANCELLED -> (terminal)
COMPLETED -> (terminal)
```
