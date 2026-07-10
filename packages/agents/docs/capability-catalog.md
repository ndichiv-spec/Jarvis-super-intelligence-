# Capability Catalog

## Built-in Capabilities

The platform ships with a standard set of capabilities that agent definitions can reference.

| Capability | Description |
|-----------|-------------|
| `research` | Conduct research and gather information |
| `programming` | Write and review code |
| `architecture` | Design software architecture |
| `automation` | Automate workflows and processes |
| `planning` | Create and manage plans |
| `summarization` | Summarize information |
| `analysis` | Analyze data and patterns |
| `design` | Design systems and interfaces |
| `translation` | Translate between languages |
| `vision` | Process visual information |
| `voice` | Process voice and audio |
| `reasoning` | Perform logical reasoning |
| `documentation` | Create and maintain documentation |
| `testing` | Write and execute tests |
| `code_review` | Review code for quality |
| `debugging` | Debug issues in code |
| `optimization` | Optimize performance |
| `monitoring` | Monitor systems and health |
| `communication` | Handle communications |
| `reporting` | Generate reports |

## Default Agent Definitions

| Role | Capabilities |
|------|-------------|
| `research` | research, analysis, summarization, reasoning |
| `engineering` | programming, architecture, code_review, debugging, optimization, testing |
| `planning` | planning, analysis, reasoning, reporting |
| `documentation` | documentation, summarization, analysis |
| `automation` | automation, planning, monitoring, analysis |
| `vision` | vision, analysis, reasoning |
| `voice` | voice, translation, communication |
| `testing` | testing, analysis, programming |
| `design` | design, architecture, analysis, reasoning |

## Defining Custom Capabilities

```python
from jarvis_agents.models import AgentCapability, AgentPermission

custom_cap = AgentCapability(
    name="data_science",
    description="Perform data science and ML tasks",
    permission_required=AgentPermission(
        resource="memory",
        access="read",
    ),
)
```
