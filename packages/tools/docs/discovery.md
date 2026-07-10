# Discovery Engine

The discovery engine provides flexible, composable search over registered
tool definitions.

## Query Methods

| Method               | Description                                 |
|----------------------|---------------------------------------------|
| `find_by_identifier` | Exact match by dotted identifier             |
| `find_by_category`   | All tools in a given category                |
| `find_by_capability` | All tools with a specific capability          |
| `find_by_workspace`  | All tools allowed in a given workspace        |
| `search`             | Text search across name, description, identifier, and capability values |
| `composite_query`    | Filter by multiple criteria (category, capability, workspace, owner, version, status) |

## Scope

Only tools with `status == ToolStatus.ACTIVE` are returned by discovery.
Inactive, deprecated, or retired tools are excluded from all query results.

## Usage

```python
from jarvis_tools.discovery import InMemoryDiscoveryEngine
from jarvis_tools.models import ToolCategory, ToolCapability

engine = InMemoryDiscoveryEngine()
engine.sync(tool_registry.list())  # populate from registry

# By category
docs = engine.find_by_category(ToolCategory.DOCUMENT_PROCESSING)

# By capability
search_tools = engine.find_by_capability(ToolCapability.SEARCH)

# Full-text search
results = engine.search("image")

# Composite
filtered = engine.composite_query({"category": "utility"})
```
