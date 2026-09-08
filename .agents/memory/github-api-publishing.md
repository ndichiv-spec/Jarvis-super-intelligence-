---
name: GitHub API publishing fallback
description: Reliable project publication when local GitHub credential helpers cannot authenticate.
---

When local Git push authentication fails but the GitHub connector is attached, publish through the authenticated GitHub REST Git Data API instead of asking for a token or force-pushing.

**Why:** The local credential helper can be stale even when the Replit-managed connection is healthy. GitHub's connector also enforces a workspace request rate limit and can time out on one large tree payload.

**How to apply:** Upload blobs with a shared request throttle, create trees in small incremental batches, create a commit with the current remote branch as its parent, and update the branch with `force: false`. Verify the branch ref and at least one uploaded file afterward.