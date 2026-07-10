# Validation Engine

The validation engine checks tool inputs, outputs, permissions, and
execution policies before and after execution.

## Validation Methods

| Method                    | Scope                                           |
|---------------------------|-------------------------------------------------|
| `validate_input`          | Required properties exist; type checking (integer, number, string) |
| `validate_output`         | Output is present when schema declares required properties |
| `validate_permissions`    | Permission scope matches the target workspace    |
| `validate_execution_policy` | Workspace is in the allowed list               |
| `validate_all`            | Runs all four validators and aggregates results |

## ValidationReport

Each validation returns a `ToolValidationReport` with:

- `valid: bool` — overall pass/fail
- `errors: tuple[str]` — blocking issues
- `warnings: tuple[str]` — non-blocking advisories

## Usage

```python
from jarvis_tools.validation import InMemoryValidationEngine

engine = InMemoryValidationEngine()
report = engine.validate_input(definition, params)
if not report.valid:
    for error in report.errors:
        print(error)
```
