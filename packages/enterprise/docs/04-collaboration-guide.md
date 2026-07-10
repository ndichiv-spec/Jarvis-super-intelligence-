# Enterprise Collaboration Guide

## Shared Projects

Create cross-team collaborative projects within workspaces:

```python
from jarvis_enterprise.collaboration.service import CollaborationService

collab = CollaborationService(repository)

project = collab.create_shared_project(
    workspace_id=workspace.id,
    name="AI Model v2",
    owner_id="project-lead",
    description="Next generation model development"
)
```

## Shared Knowledge Base

Teams can contribute and discover enterprise knowledge:

```python
knowledge = collab.create_shared_knowledge(
    title="Deployment Runbook",
    content="# Production Deployment Steps\n1. Verify health checks...",
    author_id="devops-lead"
)
```

## Discussions

Collaborate asynchronously with threaded discussions:

```python
from jarvis_enterprise.collaboration.models import DiscussionKind

discussion = collab.create_discussion(
    title="Architecture Review",
    content="Should we adopt event sourcing?",
    author_id="architect",
    kind=DiscussionKind.design
)

reply = collab.add_reply(
    discussion_id=discussion.id,
    author_id="senior-dev",
    content="Yes, it aligns with our CQRS pattern."
)
```

## Review Workflows

### Creating a Review
```python
workflow = collab.create_review_workflow(
    title="API Design Review",
    created_by="tech-lead",
    reviewers=("senior-dev-1", "senior-dev-2", "architect")
)
```

### Approving/Rejecting
```python
# Approve
approval = collab.approve(
    workflow_id=workflow.id,
    reviewer_id="senior-dev-1",
    comment="LGTM, minor suggestions inline"
)

# Reject
rejection = collab.reject(
    workflow_id=workflow.id,
    reviewer_id="architect",
    comment="Needs security review before approval"
)
```

## Collaboration Best Practices

1. **Use discussion threads** for design decisions to preserve context
2. **Leverage review workflows** for changes that cross team boundaries
3. **Tag knowledge articles** for discoverability
4. **Set appropriate visibility** — start internal, promote to shared when stable
5. **Archive completed projects** rather than deleting them
