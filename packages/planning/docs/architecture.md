# Planning Architecture Summary

## Overview

The Cognitive Planning Engine transforms natural language objectives into structured, executable plans. It is the mandatory first phase of all complex workflows in the JARVIS platform. Instead of responding immediately, JARVIS first constructs an explicit execution strategy.

## Architecture

```text
User Objective
    |
    v
+------------------+
|  GoalAnalyzer     |  Intent detection, category classification,
|                   |  ambiguity detection, constraint/deliverable suggestion
+------------------+
    |
    v
+------------------+
|  TaskDecomposer   |  Hierarchical/recursive decomposition into
|                   |  executable tasks with effort estimation
+------------------+
    |
    v
+------------------+
|  AgentAssigner    |  Automatic agent selection based on capability
|                   |  match, workload balance, or confidence score
+------------------+
    |
    v
+------------------+
|  DependencyGraph  |  DAG construction, topological sort,
|                   |  critical path identification
+------------------+
    |
    v
+------------------+
|  PlanValidator    |  Cycle detection, missing deps, completeness
+------------------+
    |
    v
+------------------+
|  Scheduler        |  Priority queues, concurrency limits,
|                   |  ready/waiting/blocked state management
+------------------+
    |
    v
+------------------+
|  Executor         |  Task execution with retry, state machines,
|                   |  event emission
+------------------+
    |
    v
+------------------+
|  ProgressMonitor  |  Real-time progress, completion pct,
|                   |  estimated remaining time
+------------------+
    |
    v
+------------------+
|  MemoryConnector  |  Persist plans and execution results
|                   |  to MemoryKernel for reuse
+------------------+
```

## Core Modules

### analyzer.py
Converts raw objectives into structured `Goal` objects. Detects category (web, mobile, data, ai-ml, devops, etc.), identifies ambiguity, suggests required knowledge domains, constraints, and deliverables.

### decomposer.py
Divides goals into `Task` objects supporting hierarchical, recursive, milestone, parallel, sequential, and atomic task types. Provides category-specific decomposition templates and custom template support.

### agent_assigner.py
Integrates with the Agents Platform (`AgentKernel`) to automatically select specialist agents based on task capability requirements. Supports four assignment strategies: capability match, workload balance, confidence score, and round-robin.

### dependency_graph.py
Represents every plan as a Directed Acyclic Graph (DAG). Provides topological sort, execution levels, critical path analysis, subgraph extraction, and cycle detection.

### scheduler.py
Intelligent scheduler with priority queues, concurrency limits, dependency awareness, and ready/waiting/blocked state management. Supports dynamic scheduling with capacity tracking.

### executor.py
Executes tasks with configurable retry policies (exponential backoff). Emits events for all state transitions. Supports custom executor functions per task type.

### state_machine.py
Validated task state transitions: PLANNED -> READY -> RUNNING -> WAITING/BLOCKED -> FAILED/CANCELLED/COMPLETED. All transitions are validated against allowed paths.

### monitor.py
Real-time progress tracking with completion percentage, estimated remaining time, task breakdown, and event-driven updates.

### replanner.py
Dynamic replanning on task failure, dependency changes, agent unavailability, requirement changes, or timeouts. Preserves completed work and generates updated execution paths.

### validator.py
Validates goals (empty, ambiguous, missing deliverables), graphs (cycles, missing deps), tasks (no effort, no title), and plan completeness.

### estimator.py
Effort estimation and complexity scoring based on objective text analysis, domain factors, and keyword indicators. Produces complexity (trivial to very complex), effort hours, duration text, confidence, and risk level.

### reasoning.py
Structured reasoning chains that explain every planning decision. Captures objective analysis, category detection, complexity assessment, ambiguity detection, knowledge requirements, dependency analysis, and schedule evaluation.

### explanation.py
Human-readable planning summaries for goals, execution plans, progress, completion, and individual decisions. Generates formatted text and structured data output.

### memory_connector.py
Persists plans, execution results, and outcomes to the MemoryKernel. Enables retrieval of similar past plans for knowledge reuse.

### events.py
Pub-sub event bus for plan lifecycle events including creation, validation, start, completion, failure, cancellation, replanning, task state changes, agent assignments, and milestone events.

### policies.py
Configurable execution policies: concurrency limits, retry policies (exponential backoff), completion criteria (output verification, confidence thresholds, custom checks).

## Integration Points

| Integration | Module | Purpose |
|-------------|--------|---------|
| Agents Platform | `AgentKernel` | Agent discovery, assignment, task delegation |
| Memory System | `MemoryKernel` | Plan persistence, retrieval, knowledge reuse |
| Gateway API | FastAPI Router | REST endpoints for plan CRUD and execution |
| Home UI | Next.js Page | End-user planning dashboard |
| Studio UI | Next.js Page | Developer planning workspace |
| Brain Pipeline | `PlanningEngine` | Intent-to-plan bridge |

## Execution Flow

1. **Create** — Generate unique plan ID, store empty plan
2. **Analyze** — Detect category, complexity, ambiguity, constraints
3. **Decompose** — Split goal into tasks with dependencies
4. **Assign Agents** — Select specialist agents per capability
5. **Validate** — Check for cycles, missing deps, completeness
6. **Schedule** — Build priority queue with concurrency limits
7. **Execute** — Run tasks with retry, emit state events
8. **Monitor** — Track progress, estimate remaining time
9. **Store** — Persist plan and results to memory
10. **Replan** — Adapt dynamically when conditions change
