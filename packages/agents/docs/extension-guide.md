# Extension Guide

## Replacing a Component

Each subsystem is defined as a `Protocol` (interface). To replace a default implementation, create a class that satisfies the protocol and inject it into the `AgentKernel`.

### Example: Custom Registry (Database-Backed)

```python
from jarvis_agents.models import AgentMetadata, AgentStatus
from jarvis_agents.protocols import AgentRegistry

class PostgresAgentRegistry:
    def __init__(self, connection_string: str):
        self._conn_string = connection_string

    def register(self, agent: AgentMetadata) -> None:
        # INSERT INTO agents ...
        pass

    def get(self, identifier: str) -> AgentMetadata | None:
        # SELECT * FROM agents WHERE id = ...
        pass

    def update(self, agent: AgentMetadata) -> None:
        # UPDATE agents ...
        pass

    def list(self) -> tuple[AgentMetadata, ...]:
        # SELECT * FROM agents ...
        pass

    def list_by_status(self, status: AgentStatus) -> tuple[AgentMetadata, ...]:
        # SELECT * FROM agents WHERE status = ...
        pass

    def list_by_capability(self, capability_name: str) -> tuple[AgentMetadata, ...]:
        # SELECT * FROM agents WHERE capability = ...
        pass

    def deregister(self, identifier: str) -> None:
        # DELETE FROM agents WHERE id = ...
        pass

# Inject into kernel
kernel = AgentKernel(registry=PostgresAgentRegistry("postgresql://..."))
```

### Example: Custom CommunicationBus (Redis-Backed)

```python
from jarvis_agents.models import AgentCommunicationRequest, AgentCommunicationResponse, AgentEvent

class RedisCommunicationBus:
    def send_request(self, request: AgentCommunicationRequest) -> None:
        # LPUSH agent:{target}:requests ...
        pass

    def send_response(self, response: AgentCommunicationResponse) -> None:
        # LPUSH corr:{correlation_id}:responses ...
        pass

    def publish_event(self, event: AgentEvent) -> None:
        # PUBLISH events channel ...
        pass

    def pending_requests(self, agent_id: str) -> tuple[AgentCommunicationRequest, ...]:
        # LRANGE agent:{agent_id}:requests 0 -1
        pass

    def pending_responses(self, correlation_id: str) -> tuple[AgentCommunicationResponse, ...]:
        # LRANGE corr:{correlation_id}:responses 0 -1
        pass

    def pending_events(self, agent_id: str) -> tuple[AgentEvent, ...]:
        # LRANGE events:{agent_id} 0 -1
        pass

kernel = AgentKernel(communication_bus=RedisCommunicationBus())
```

## Adding New Protocols

To add a new subsystem:

1. Define the model in `models.py`.
2. Define the protocol in `protocols.py`.
3. Create a default in-memory implementation.
4. Add the protocol to `AgentKernel.__init__` with injection support.
5. Expose public methods on `AgentKernel` that delegate to the protocol.

## Protocol Contracts Reference

| Protocol | Key Methods |
|----------|------------|
| `AgentRegistry` | register, update, get, list, list_by_status, list_by_capability, deregister |
| `LifecycleManager` | initialize, transition, current, can_transition |
| `CapabilityManager` | register_capability, get_capability, list_capabilities, has_capability, find_agents_with_capability |
| `PermissionManager` | check_permission, grant_permission, revoke_permission |
| `GoalManager` | create_goal, update_progress, update_status, get_goal, list_goals, list_goals_by_status |
| `TaskManager` | create_task, assign_task, complete_task, fail_task, retry_task, get_task, list_tasks, list_tasks_by_agent, list_tasks_by_status |
| `CommunicationBus` | send_request, send_response, publish_event, pending_requests, pending_responses, pending_events |
| `MemoryInterface` | store, retrieve, search, delete |
| `KnowledgeInterface` | query, get_document, search |
| `ToolInterface` | execute, list_available, check_access |
| `HealthMonitor` | record_heartbeat, record_failure, get_report, list_reports, list_unhealthy |
| `PolicyEngine` | register_policy, resolve, evaluate |
