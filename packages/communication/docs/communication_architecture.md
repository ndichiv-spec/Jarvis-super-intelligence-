# JARVIS Communication Architecture

## Overview

The JARVIS Communication & Collaboration Platform (JCP) serves as the unified communication layer for all interactions within the JARVIS ecosystem. It supports real-time messaging, notifications, email, WebSocket streaming, presence tracking, and collaboration features.

## Architecture Diagram

```
+------------------------------------------------------------------+
|                     Home Dashboard (Next.js)                       |
|  Communication Dashboard - Conversations - Notifications - Users  |
+------------------------------------------------------------------+
         |  HTTP / WebSocket
         v
+------------------------------------------------------------------+
|                    Gateway API (FastAPI)                           |
|  /communication/*  - REST endpoints for all communication ops     |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|                 Communication Engine (Python)                      |
|  +------------+  +------------+  +-------------+  +------------+  |
|  | Messaging  |  |Conversation|  | Notification|  | Streaming  |  |
|  | Service    |  | Manager    |  | Service     |  | Engine     |  |
|  +------------+  +------------+  +-------------+  +------------+  |
|  +------------+  +------------+  +-------------+  +------------+  |
|  | WebSocket  |  | Presence   |  | Delivery    |  | Channels   |  |
|  | Manager    |  | Service    |  | Service     |  | Manager    |  |
|  +------------+  +------------+  +-------------+  +------------+  |
|  +------------+  +------------+  +-------------+  +------------+  |
|  | Email      |  | Chat       |  | Templates   |  | Meetings   |  |
|  | Service    |  | Service    |  | Engine      |  | Manager    |  |
|  +------------+  +------------+  +-------------+  +------------+  |
|  +------------+  +------------+  +-------------+  +------------+  |
|  | Analytics  |  | Audit      |  | Security    |  | Metrics    |  |
|  | Engine     |  | Service    |  | Service     |  | Collector  |  |
|  +------------+  +------------+  +-------------+  +------------+  |
+------------------------------------------------------------------+
```

## Core Components

### Messaging Service
Handles sending, retrieving, searching, and managing delivery of messages between users, agents, and systems.

### Conversation Manager  
Manages persistent conversations with threaded discussions, participant management, and context preservation.

### Notification Service
Handles platform alerts, task completions, agent updates, security alerts, and system notifications with multiple severity levels.

### Streaming Engine
Supports live streaming for AI responses, agent execution, planning progress, knowledge indexing, and automation workflows.

### WebSocket Manager
Provides real-time updates for live dashboards, agent status, planning updates, notifications, and logs.

### Presence Service
Tracks online users, active agents, active sessions, current activities, and connected clients.

### Delivery Service
Manages delivery receipts, read confirmations, and delivery failure reporting for all messages.

### Security Service
Provides permission checks, access validation, rate limiting, and payload encryption.

### Analytics Engine
Measures messages sent, delivery time, unread messages, response latency, notification success, and streaming latency.

## Communication Model

Every communication is represented as a structured `CommunicationMessage` object containing:

- **message_id**: Unique identifier (UUID)
- **sender**: Source of the message
- **receiver**: Target recipient
- **channel**: Channel type (internal, ai_conversation, email, push_notification, websocket, system, external)
- **conversation_id**: Reference to parent conversation
- **timestamp**: UTC timestamp
- **message_type**: Type of message (text, command, event, notification, system, error, warning)
- **priority**: Priority level (low, normal, high, critical)
- **body**: Message content
- **subject**: Optional subject line
- **attachments**: List of attached files
- **metadata**: Extensible metadata dictionary
- **delivery_status**: Current delivery state (pending, sent, delivered, read, failed)
- **read_status**: Read state (unread, read, archived)

## Supported Channels

- **Internal Platform Messaging**: Direct user-to-user and system messages
- **AI Conversations**: User-to-agent and agent-to-agent communication
- **Email**: Outbound email delivery
- **Push Notifications**: Real-time platform notifications
- **WebSocket Streams**: Live data streaming
- **System Notifications**: Automated system alerts
- **External Connectors**: Extensible for future integrations

## Notification Levels

| Level    | Description          | Example                          |
|----------|----------------------|----------------------------------|
| Info     | General information  | Task started                     |
| Success  | Successful operation | Task completed                   |
| Warning  | Potential issue      | Rate limit approaching           |
| Error    | Operation failure    | Agent unresponsive               |
| Critical | Immediate attention  | Security breach detected         |
