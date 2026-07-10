# Intelligence Core Architecture

## Overview

The JARVIS Intelligence Core (JIC) is the central cognitive engine responsible for understanding goals, reasoning, planning, coordinating agents, making decisions, and improving execution quality.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Intelligence Engine                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Cognition│  │Reasoning │  │ Planner  │  │Executor  │   │
│  │ Engine   │  │ Engine   │  │          │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Coordinator│  │ Decision │  │  Safety  │  │Telemetry │   │
│  │           │  │ Engine   │  │  Engine  │  │ Engine   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐   │
│  │Optimizer │  │ Learning │  │Confidence│  │ Policy   │   │
│  │          │  │ Engine   │  │ Engine   │  │ Engine   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Priority  │  │Scheduler │  │ Context  │  │Evaluator │   │
│  │ Engine   │  │ Engine   │  │ Manager  │  │ Engine   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Roles

### IntelligenceEngine
Central orchestrator that wires all sub-engines together. The `execute_goal()` method runs the full pipeline: cognition -> reasoning -> planning -> safety -> decision -> coordination -> evaluation -> learning.

### CognitionEngine
Analyzes goal descriptions to determine intent, complexity, key entities, and constraints.

### ReasoningEngine
Supports 7 reasoning modes: analytical, sequential, strategic, comparative, reflective, constraint-based, multi-step.

### IntelligencePlanner
Creates plans from goals, decomposes goals into task graphs, manages objectives and tasks.

### ExecutionEngine
Executes individual tasks and task graphs. Provides sync/async execution support.

### CoordinatorEngine
Orchestrates multi-task execution with decision gates, retry logic, and reporting.

### DecisionEngine
Makes decisions about strategy selection, agent assignment, task execution, retries, and replanning.

### GoalManager
Manages goal lifecycle: create, update, list, remove. Supports priority ordering and state filtering.

### ContextManager
Maintains execution context including reasoning history, memory references, knowledge references, and execution events.

### EvaluationEngine
Measures task quality, efficiency, confidence. Generates improvement suggestions.

### OptimizerEngine
Optimizes task ordering, agent selection, retry strategies, and workflow efficiency.

### LearningEngine
Records successful/failed execution strategies. Provides recommendations for similar future goals.

### ConfidenceEngine
Computes confidence scores for plans, decisions, agents, and knowledge retrieval.

### PriorityEngine
Assesses goal urgency and importance to compute overall priority scores.

### SchedulerEngine
Manages one-time and recurring task scheduling with due-time detection.

### PolicyEngine
Supports four execution policies: conservative, balanced, aggressive, experimental.

### SafetyEngine
Validates goals, task graphs, and execution parameters. Detects cycles, excessive depth, and dangerous configurations.

### TelemetryEngine
Collects execution metrics, decision latency, planning quality, agent utilization, and failure statistics.
