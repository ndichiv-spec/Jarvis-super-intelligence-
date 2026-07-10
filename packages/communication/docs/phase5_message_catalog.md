# Phase 5 — Message Catalog

## Core Message Contracts

| Contract | Purpose | Key Fields |
| --- | --- | --- |
| `BaseMessage` | Common immutable message envelope | `message_name`, `payload`, `headers`, `message_id`, `timestamp`, `context` |
| `EventMessage` | Domain/integration event publication | `topic` + inherited fields |
| `CommandMessage[T]` | Intent to change state | `expected_response` + inherited fields |
| `QueryMessage[T]` | Read-oriented request | `filters`, `pagination`, `expected_response` |
| `ResponseMessage[T]` | Generic request/response envelope | `request_message_id`, `success`, `result`, `errors`, `warnings` |
| `NotificationMessage` | Non-blocking broadcast notifications | `severity` + inherited fields |
| `ErrorMessage` | Structured failure payload | `code`, `detail` + inherited fields |
| `WarningMessage` | Structured warning payload | `code`, `detail` + inherited fields |

## Context Contracts

| Contract | Purpose |
| --- | --- |
| `ExecutionContext` | Carries correlation/request/execution lineage and source/timestamp |
| `SecurityContext` | Principal identity, roles, scopes |
| `WorkspaceContext` | Workspace/tenant/environment scope |

## Bus Result Contracts

| Contract | Purpose |
| --- | --- |
| `CommandResult[T]` | Outcome of command execution |
| `QueryResult[T]` | Outcome of query execution with cache/pagination/filter metadata |
