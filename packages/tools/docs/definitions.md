# Tool Definitions

A `ToolDefinition` is an immutable contract that fully describes a tool's
capabilities, structure, and governance requirements.

## Fields

| Field            | Type                        | Description                              |
|------------------|-----------------------------|------------------------------------------|
| `identifier`     | `str`                       | Unique dotted name (e.g. `knowledge.search`) |
| `name`           | `str`                       | Human-readable name                     |
| `description`    | `str`                       | Long description of the tool            |
| `version`        | `str`                       | Semantic version string                 |
| `category`       | `ToolCategory`              | Functional category enum                |
| `capabilities`   | `tuple[ToolCapability]`     | Set of capability flags                 |
| `input_schema`   | `ToolSchema`                | Expected input parameters               |
| `output_schema`  | `ToolSchema`                | Expected output parameters              |
| `permissions`    | `tuple[ToolPermission]`     | Required permission grants              |
| `execution_policy`| `ToolExecutionPolicy`      | Runtime constraints                     |
| `metadata`       | `dict[str, str]`            | Key-value annotations                   |
| `status`         | `ToolStatus`                | Lifecycle status                        |
| `owner`          | `str`                       | Owning entity                           |

## Categories

- DOCUMENT_PROCESSING, SEARCH, IMAGE_GENERATION, IMAGE_ANALYSIS
- CODE_EXECUTION, MATHEMATICS, TRANSLATION, FORMATTING
- NOTIFICATION, DATA_CONVERSION, KNOWLEDGE, MEMORY
- COMMUNICATION, ANALYSIS, UTILITY, CUSTOM

## Built-in Definitions

Eight built-in tool definitions are registered automatically by the ToolKernel:

1. **knowledge.search** — Knowledge Search
2. **memory.lookup** — Memory Lookup
3. **image.generation** — Image Generation
4. **document.analysis** — Document Analysis
5. **code.execution** — Code Execution
6. **translation** — Translation
7. **summarization** — Summarization
8. **notification** — Notification
