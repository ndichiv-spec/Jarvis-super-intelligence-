# Developer Guide

## Installation

```bash
uv pip install -e packages/agents
```

## Quick Start

```python
from jarvis_agents import AgentKernel, AgentTaskResult
from jarvis_agents.definitions import DEFAULT_AGENT_DEFINITIONS

kernel = AgentKernel()

# Register agents from built-in definitions
for defn in DEFAULT_AGENT_DEFINITIONS:
    kernel.register_agent(defn, owner="admin", workspace="default")

# Activate specific agents
kernel.activate_agent("agent-engineering")
kernel.activate_agent("agent-research")

# Find agents by capability
engineers = kernel.find_agents_by_capability("programming")

# Send inter-agent communication
corr_id = kernel.send_request(
    "agent-research",
    "agent-engineering",
    "task",
    "Please implement the database layer",
)

# Create and complete tasks
task = kernel.create_task("Build API", "agent-engineering", priority="high")
result = AgentTaskResult(success=True, output="API implemented")
kernel.complete_task(task.task_id, result)

# Create goals
goal = kernel.create_goal("Complete Phase 1", priority="high")
kernel.update_goal_progress(goal.goal_id, 0.5)
kernel.complete_goal(goal.goal_id)

# Monitor health
health = kernel.get_health("agent-engineering")
unhealthy = kernel.list_unhealthy_agents()
```

## Creating a Custom Agent Definition

```python
from jarvis_agents.models import (
    AgentCapability,
    AgentDefinition,
    AgentPermission,
    AgentPermissionResource,
    PermissionAccess,
)

my_agent = AgentDefinition(
    role="data_scientist",
    description="Analyzes data and builds ML models",
    capabilities=(
        AgentCapability(name="analysis", description="Analyze data"),
        AgentCapability(name="programming", description="Write ML code"),
    ),
    permissions=(
        AgentPermission(
            resource=AgentPermissionResource.MEMORY,
            access=PermissionAccess.WRITE,
        ),
        AgentPermission(
            resource=AgentPermissionResource.KNOWLEDGE,
            access=PermissionAccess.READ,
        ),
    ),
)
```

## Custom Policy

```python
from jarvis_agents import AgentPolicy, AgentPolicyScope

scope = AgentPolicyScope(owner="user1", workspace="strict-ws")
policy = AgentPolicy(
    policy_id="pol-restricted",
    name="Restricted",
    allowed_capabilities=("research",),
    max_concurrent_tasks=1,
)
kernel.register_policy(scope, policy)
```

## Running Tests

```bash
pytest packages/agents/tests/
```
