# Goal Model Specification

## Goal Structure

```python
@dataclass(frozen=True)
class Goal:
    id: str                    # Unique identifier (goal-{uuid})
    description: str           # Human-readable goal description
    priority: GoalPriority     # LOWEST, LOW, MEDIUM, HIGH, CRITICAL
    state: GoalState           # DRAFT, ACTIVE, IN_PROGRESS, COMPLETED, FAILED, etc.
    constraints: tuple         # Execution constraints
    success_criteria: tuple    # Conditions for success
    dependencies: tuple        # Goal dependencies (IDs)
    deadline: datetime | None  # Optional deadline
    required_capabilities: tuple  # Required agent capabilities
    owner: str                 # Responsible entity
    workspace_id: str          # Workspace isolation
    parent_goal_id: str | None  # Optional parent goal
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    metadata: dict             # Flexible metadata
```

## Goal States

- DRAFT -> ACTIVE -> IN_PROGRESS -> COMPLETED
- IN_PROGRESS -> FAILED
- ACTIVE -> CANCELLED
- Any -> BLOCKED / ON_HOLD

## Goal Priorities

| Priority  | Weight | Description         |
|-----------|--------|---------------------|
| LOWEST    | 0.1    | Optional enhancement |
| LOW       | 0.3    | Nice to have        |
| MEDIUM    | 0.5    | Standard priority   |
| HIGH      | 0.75   | Important objective |
| CRITICAL  | 1.0    | Blocking / urgent   |

## Objective Structure

```python
@dataclass(frozen=True)
class Objective:
    id: str
    description: str
    goal_id: str | None
    constraints: tuple
    priority: int       # 0-100 scale
```

## Task Structure

```python
@dataclass(frozen=True)
class Task:
    id: str
    description: str
    state: TaskState        # PENDING, READY, RUNNING, COMPLETED, FAILED, etc.
    parent_task_id: str | None
    child_task_ids: tuple
    depends_on: tuple       # Dependency task IDs
    assigned_agent_id: str | None
    required_capabilities: tuple
    priority: int           # 0-100
    max_retries: int
    retry_count: int
    timeout_seconds: float | None
    started_at: datetime | None
    completed_at: datetime | None
    result: Any
    error: str | None
```

## Task Graph

The TaskGraph provides:
- `add(task)` - Add a task node
- `get(task_id)` - Get task by ID
- `update(task_id, **updates)` - Update task state
- `get_ready_tasks()` - Get tasks with all dependencies met
- `get_by_state(state)` - Filter tasks by state
- `all()` - Return all tasks
- `topological_sort()` - Return tasks in dependency order

## Task Decomposition

Goals are decomposed into executable task graphs supporting:
- Parent/child task hierarchies
- Parallel execution branches
- Sequential execution chains
- Conditional branching
- Retry logic with configurable max_retries
- Rollback capabilities
