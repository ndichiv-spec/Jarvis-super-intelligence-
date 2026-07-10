# Phase 5 — Communication Architecture

## Purpose

The communication package is the framework-independent nervous system for JARVIS modules.
It provides asynchronous, typed message exchange through events, commands, queries,
notifications, and routing decisions without infrastructure coupling.

## Design Principles

- Async-first APIs
- Immutable message contracts
- Strict typing through dataclasses and protocols
- Separation of concerns (transport/infrastructure decoupled)
- Extensible contracts for observability, serialization, scheduling, and event persistence

## Core Components

- `messages.py`: immutable contracts for all message categories and response objects
- `context.py`: execution context propagation (`correlation_id`, `request_id`, `execution_id`, parent)
- `event_bus.py`: publish/subscribe with priority, filters, one-shot handlers, replay and dead-letter hooks
- `command_bus.py`: command dispatch with execution contracts and pipeline integration
- `query_bus.py`: query dispatch with caching, projection, filtering, and pagination contracts
- `pipeline.py`: middleware chain and validation/auth/logging/retry/metrics hooks
- `routing.py`: priority/grouping/broadcast/directed/conditional route resolution
- `message_bus.py`: unified abstraction over events, commands, queries, notifications, and routing
- `contracts.py`: interfaces for observability, serialization, event store, and scheduler

## Dependency Boundaries

- No framework dependencies
- No broker/database dependencies
- No direct coupling to Redis/Kafka/RabbitMQ/FastAPI
- Infrastructure adapters are deferred to later phases and can target the protocol contracts

## Extension Surface

- Replace in-memory/default execution behavior by implementing protocol contracts
- Add middleware and hook implementations for cross-cutting concerns
- Attach external transport adapters to `MessageBus` and serializer/scheduler/event-store protocols
