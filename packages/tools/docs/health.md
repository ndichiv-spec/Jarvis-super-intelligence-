# Health Monitor

The health monitor tracks execution metrics and surfaces unhealthy tools
for remediation.

## Metrics Tracked

- `execution_count` — total executions recorded
- `failure_count` — total failures recorded
- `average_execution_time_ms` — rolling average of last 100 executions
- `last_execution` — timestamp of most recent run
- `available` — boolean derived from status
- `status` — computed from failure rate: ACTIVE (<30%), UNDER_MAINTENANCE (30-50%), FAILED (>50%)

## Usage

```python
from jarvis_tools.health import InMemoryHealthMonitor

monitor = InMemoryHealthMonitor()
monitor.record_execution("knowledge.search", 150, True)
monitor.record_failure("knowledge.search", "timeout")

report = monitor.get_report("knowledge.search")
print(report.execution_count, report.failure_count)

unhealthy = monitor.list_unhealthy()
```
