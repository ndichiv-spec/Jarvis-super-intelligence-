from __future__ import annotations

from jarvis_tools.models import (
    PermissionAccess,
    PermissionResource,
    ToolCapability,
    ToolCategory,
    ToolDefinition,
    ToolExecutionPolicy,
    ToolPermission,
    ToolProperty,
    ToolSchema,
)


def _prop(name: str, type_: str, description: str, required: bool = True) -> ToolProperty:
    return ToolProperty(name=name, type=type_, description=description, required=required)


def _read_perm(resource: PermissionResource, scope: str = "*") -> ToolPermission:
    return ToolPermission(
        resource=resource,
        access=PermissionAccess.READ,
        scope=scope,
        description=f"Read access to {resource.value}",
    )


def _write_perm(resource: PermissionResource, scope: str = "*") -> ToolPermission:
    return ToolPermission(
        resource=resource,
        access=PermissionAccess.WRITE,
        scope=scope,
        description=f"Write access to {resource.value}",
    )


def _default_policy(timeout: int = 300) -> ToolExecutionPolicy:
    return ToolExecutionPolicy(timeout_seconds=timeout)


KNOWLEDGE_SEARCH: ToolDefinition = ToolDefinition(
    identifier="knowledge.search",
    name="Knowledge Search",
    description="Search across indexed knowledge bases using natural language queries.",
    version="1.0.0",
    category=ToolCategory.KNOWLEDGE,
    capabilities=(ToolCapability.KNOWLEDGE_QUERY, ToolCapability.SEARCH),
    input_schema=ToolSchema(
        properties=(
            _prop("query", "string", "Natural language search query"),
            _prop("max_results", "integer", "Maximum number of results", required=False),
            _prop("filter", "string", "Optional scope filter", required=False),
        ),
        description="Query parameters for knowledge search",
    ),
    output_schema=ToolSchema(
        properties=(
            _prop("results", "string", "Search results as formatted text"),
            _prop("total_count", "integer", "Total number of matches", required=False),
        ),
        description="Search output",
    ),
    permissions=(_read_perm(PermissionResource.KNOWLEDGE),),
    execution_policy=_default_policy(),
    metadata={"category": "search", "tags": "knowledge,search"},
)

MEMORY_LOOKUP: ToolDefinition = ToolDefinition(
    identifier="memory.lookup",
    name="Memory Lookup",
    description="Retrieve information from the agent's long-term memory store.",
    version="1.0.0",
    category=ToolCategory.MEMORY,
    capabilities=(ToolCapability.MEMORY_ACCESS, ToolCapability.SEARCH),
    input_schema=ToolSchema(
        properties=(
            _prop("key", "string", "Memory key or identifier"),
            _prop("namespace", "string", "Memory namespace", required=False),
        ),
        description="Lookup parameters",
    ),
    output_schema=ToolSchema(
        properties=(_prop("value", "string", "Retrieved memory content"),),
        description="Memory lookup output",
    ),
    permissions=(_read_perm(PermissionResource.MEMORY),),
    execution_policy=_default_policy(),
    metadata={"category": "memory", "tags": "memory,lookup"},
)

IMAGE_GENERATION: ToolDefinition = ToolDefinition(
    identifier="image.generation",
    name="Image Generation",
    description="Generate images from textual descriptions.",
    version="1.0.0",
    category=ToolCategory.IMAGE_GENERATION,
    capabilities=(ToolCapability.IMAGE_GENERATION,),
    input_schema=ToolSchema(
        properties=(
            _prop("prompt", "string", "Text description of the image"),
            _prop("style", "string", "Image style", required=False),
            _prop("resolution", "string", "Image resolution", required=False),
        ),
        description="Image generation parameters",
    ),
    output_schema=ToolSchema(
        properties=(_prop("image_url", "string", "URL or reference to the generated image"),),
        description="Generated image output",
    ),
    permissions=(_write_perm(PermissionResource.WORKSPACE),),
    execution_policy=ToolExecutionPolicy(timeout_seconds=600),
    metadata={"category": "creative", "tags": "image,generation"},
)

DOCUMENT_ANALYSIS: ToolDefinition = ToolDefinition(
    identifier="document.analysis",
    name="Document Analysis",
    description="Analyze document content and extract structured information.",
    version="1.0.0",
    category=ToolCategory.DOCUMENT_PROCESSING,
    capabilities=(
        ToolCapability.DOCUMENT_PROCESSING,
        ToolCapability.TEXT_ANALYSIS,
    ),
    input_schema=ToolSchema(
        properties=(
            _prop("content", "string", "Document content or reference"),
            _prop("analysis_type", "string", "Type of analysis to perform", required=False),
        ),
        description="Document analysis parameters",
    ),
    output_schema=ToolSchema(
        properties=(_prop("analysis", "string", "Structured analysis results"),),
        description="Analysis output",
    ),
    permissions=(_read_perm(PermissionResource.KNOWLEDGE),),
    execution_policy=_default_policy(),
    metadata={"category": "analysis", "tags": "document,analysis"},
)

CODE_EXECUTION: ToolDefinition = ToolDefinition(
    identifier="code.execution",
    name="Code Execution",
    description="Execute code snippets in a sandboxed environment.",
    version="1.0.0",
    category=ToolCategory.CODE_EXECUTION,
    capabilities=(ToolCapability.CODE_EXECUTION,),
    input_schema=ToolSchema(
        properties=(
            _prop("code", "string", "Code to execute"),
            _prop("language", "string", "Programming language"),
        ),
        description="Code execution parameters",
    ),
    output_schema=ToolSchema(
        properties=(
            _prop("output", "string", "Execution stdout"),
            _prop("error", "string", "Execution stderr", required=False),
            _prop("exit_code", "integer", "Process exit code", required=False),
        ),
        description="Execution output",
    ),
    permissions=(_write_perm(PermissionResource.WORKSPACE),),
    execution_policy=ToolExecutionPolicy(
        timeout_seconds=120,
        requires_confirmation=True,
    ),
    metadata={"category": "development", "tags": "code,execution,development"},
)

TRANSLATION: ToolDefinition = ToolDefinition(
    identifier="translation",
    name="Translation",
    description="Translate text between languages.",
    version="1.0.0",
    category=ToolCategory.TRANSLATION,
    capabilities=(ToolCapability.TRANSLATION,),
    input_schema=ToolSchema(
        properties=(
            _prop("text", "string", "Text to translate"),
            _prop("source_language", "string", "Source language code"),
            _prop("target_language", "string", "Target language code"),
        ),
        description="Translation parameters",
    ),
    output_schema=ToolSchema(
        properties=(_prop("translated_text", "string", "Translated output"),),
        description="Translation output",
    ),
    permissions=(_read_perm(PermissionResource.COMMUNICATION),),
    execution_policy=_default_policy(),
    metadata={"category": "utility", "tags": "translation,language"},
)

SUMMARIZATION: ToolDefinition = ToolDefinition(
    identifier="summarization",
    name="Summarization",
    description="Generate concise summaries of long-form content.",
    version="1.0.0",
    category=ToolCategory.ANALYSIS,
    capabilities=(ToolCapability.TEXT_SUMMARIZATION, ToolCapability.TEXT_ANALYSIS),
    input_schema=ToolSchema(
        properties=(
            _prop("content", "string", "Content to summarize"),
            _prop("max_length", "integer", "Maximum summary length", required=False),
            _prop("format", "string", "Summary format style", required=False),
        ),
        description="Summarization parameters",
    ),
    output_schema=ToolSchema(
        properties=(_prop("summary", "string", "Generated summary"),),
        description="Summarization output",
    ),
    permissions=(_read_perm(PermissionResource.KNOWLEDGE),),
    execution_policy=_default_policy(),
    metadata={"category": "analysis", "tags": "summarization,text"},
)

NOTIFICATION: ToolDefinition = ToolDefinition(
    identifier="notification",
    name="Notification",
    description="Send notifications through configured channels.",
    version="1.0.0",
    category=ToolCategory.NOTIFICATION,
    capabilities=(ToolCapability.NOTIFICATION,),
    input_schema=ToolSchema(
        properties=(
            _prop("message", "string", "Notification message content"),
            _prop("channel", "string", "Notification delivery channel", required=False),
            _prop("priority", "string", "Message priority level", required=False),
        ),
        description="Notification parameters",
    ),
    output_schema=ToolSchema(
        properties=(_prop("status", "string", "Delivery status"),),
        description="Notification output",
    ),
    permissions=(_write_perm(PermissionResource.COMMUNICATION),),
    execution_policy=_default_policy(),
    metadata={"category": "communication", "tags": "notification,alert"},
)

BUILT_IN_TOOLS: tuple[ToolDefinition, ...] = (
    KNOWLEDGE_SEARCH,
    MEMORY_LOOKUP,
    IMAGE_GENERATION,
    DOCUMENT_ANALYSIS,
    CODE_EXECUTION,
    TRANSLATION,
    SUMMARIZATION,
    NOTIFICATION,
)
