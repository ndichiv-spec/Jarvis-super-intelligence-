# Phase 12 Identity Model

## Supported Identity Types

- User
- Agent
- Extension
- Service
- Organization
- Workspace
- Future devices

## Identity Contract

Each identity is represented by:

- Immutable identifier
- Identity type
- Display name
- Attributes
- Lifecycle metadata

## Metadata Requirements

Every identity includes security metadata with:

- Identifier
- Type
- Owner
- Workspace
- Organization
- Status
- Created timestamp
- Updated timestamp
- Policy references

## Lifecycle Expectations

- Identity identifiers are immutable.
- Lifecycle state is represented through metadata status.
- Updates produce new metadata snapshots using typed value objects.
