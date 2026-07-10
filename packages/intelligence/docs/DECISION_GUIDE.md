# Decision Engine Guide

## Overview

The DecisionEngine provides structured decision-making based on available resources, agent capabilities, confidence scores, execution history, policies, and risk analysis.

## Decision Types

| Type              | Description                        | Confidence Factors              |
|-------------------|------------------------------------|---------------------------------|
| SELECT_STRATEGY   | Choose execution strategy           | Complexity assessment           |
| ASSIGN_AGENT      | Assign agent to task               | Capability matching             |
| EXECUTE_TASK      | Proceed with task execution        | Dependency readiness            |
| RETRY_TASK        | Retry failed task                  | Retry count vs max retries      |
| SKIP_TASK         | Skip non-critical failed task      | Impact analysis                 |
| REPLAN            | Replan after failures              | Failure count                   |
| ESCALATE          | Escalate to human                  | Confidence threshold            |
| COMPLETE_GOAL     | Mark goal as complete              | Success criteria met            |
| CANCEL_GOAL       | Cancel goal execution              | Irrecoverable failure           |

## Decision Process

1. Context is collected (task state, available agents, capabilities, etc.)
2. Appropriate decision method is selected based on DecisionType
3. Confidence score is computed
4. Decision is recorded in history
5. Decision is returned for execution

## Integration

The DecisionEngine is used by:
- **CoordinatorEngine** - Decides whether to execute/retry tasks
- **IntelligencePlanner** - Selects strategies
- **ExecutionEngine** - Determines execution path

## Custom Decision Methods

Add custom decisions by creating a method `_decide_<type>` on DecisionEngine:

```python
def _decide_custom_action(self, context, threshold):
    return Decision(
        type=DecisionType("custom_action"),
        reasoning="Custom logic",
        confidence=0.8,
        target_id=context.get("target_id"),
    )
```
