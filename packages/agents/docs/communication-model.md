# Communication Model

## Design

Agents communicate **indirectly** through the `CommunicationBus`. No agent ever calls another agent directly. All messages are identified by correlation IDs for request-response pairing.

## Message Types

### Requests
Directed messages from one agent to another, expecting a response.

```python
from jarvis_agents.models import AgentCommunicationRequest

req = AgentCommunicationRequest(
    source_agent_id="agent-a",
    target_agent_id="agent-b",
    message_type="task_assignment",
    payload='{"task_id": "task-001", "description": "Write tests"}',
    correlation_id="corr-abc123",
)
bus.send_request(req)
```

### Responses
Replies to requests, linked by correlation ID.

```python
from jarvis_agents.models import AgentCommunicationResponse

resp = AgentCommunicationResponse(
    correlation_id="corr-abc123",
    source_agent_id="agent-b",
    target_agent_id="agent-a",
    payload='{"status": "completed", "result": "All tests pass"}',
    success=True,
)
bus.send_response(resp)
```

### Events
Notifications that can be targeted at a single agent or broadcast to all agents.

```python
from jarvis_agents.models import AgentEvent

event = AgentEvent(
    event_id="evt-001",
    source_agent_id="agent-a",
    event_type="status_change",
    payload='{"status": "busy"}',
    broadcast=False,
)
bus.publish_event(event)
```

## Message Flow

```
Agent A                     CommunicationBus                   Agent B
   │                              │                              │
   │── send_request ─────────────>│                              │
   │                              │── pending_requests ─────────>│
   │                              │                              │
   │                              │<── send_response ────────────│
   │<── pending_responses ────────│                              │
   │                              │                              │
   │── publish_event ────────────>│                              │
   │                              │── pending_events ───────────>│
```

## Through the Kernel

```python
# Send request
corr_id = kernel.send_request("agent-a", "agent-b", "query", "What is the status?")

# Check pending requests on target
requests = kernel.pending_requests("agent-b")

# Send response
kernel.send_response(corr_id, "agent-b", "agent-a", "All good", success=True)

# Check response
responses = kernel.pending_responses(corr_id)

# Publish event
kernel.publish_event("agent-a", "status_change", '{"status": "done"}')
```
