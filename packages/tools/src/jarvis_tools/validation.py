from __future__ import annotations

from jarvis_tools.models import (
    ToolDefinition,
    ToolValidationReport,
)


class InMemoryValidationEngine:
    def validate_input(
        self,
        definition: ToolDefinition,
        parameters: dict[str, str],
    ) -> ToolValidationReport:
        errors: list[str] = []
        warnings: list[str] = []
        for prop in definition.input_schema.properties:
            if prop.required and prop.name not in parameters:
                errors.append(f"Missing required input: {prop.name}")
            elif prop.name in parameters:
                value = parameters[prop.name]
                if prop.type == "integer":
                    try:
                        int(value)
                    except ValueError:
                        errors.append(
                            f"Input {prop.name} expected integer, got {value}",
                        )
                elif prop.type == "number":
                    try:
                        float(value)
                    except ValueError:
                        errors.append(
                            f"Input {prop.name} expected number, got {value}",
                        )
                if prop.default is not None:
                    warnings.append(f"Input {prop.name} uses default value")
        return ToolValidationReport(
            tool_identifier=definition.identifier,
            valid=len(errors) == 0,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    def validate_output(
        self,
        definition: ToolDefinition,
        output: str,
    ) -> ToolValidationReport:
        errors: list[str] = []
        if not output and any(p.required for p in definition.output_schema.properties):
            errors.append("Tool produced no output but output is required")
        return ToolValidationReport(
            tool_identifier=definition.identifier,
            valid=len(errors) == 0,
            errors=tuple(errors),
        )

    def validate_permissions(
        self,
        definition: ToolDefinition,
        agent_id: str,
        workspace: str,
    ) -> ToolValidationReport:
        _ = (agent_id, workspace)
        errors: list[str] = []
        for perm in definition.permissions:
            if perm.scope != "*" and perm.scope != workspace:
                errors.append(
                    f"Permission scope mismatch for {perm.resource.value}: "
                    f"required {perm.scope}, got {workspace}",
                )
        return ToolValidationReport(
            tool_identifier=definition.identifier,
            valid=len(errors) == 0,
            errors=tuple(errors),
        )

    def validate_execution_policy(
        self,
        definition: ToolDefinition,
        workspace: str,
    ) -> ToolValidationReport:
        errors: list[str] = []
        if (
            "*" not in definition.execution_policy.allowed_workspaces
            and workspace not in definition.execution_policy.allowed_workspaces
        ):
            errors.append(
                f"Workspace '{workspace}' not allowed by tool policy",
            )
        return ToolValidationReport(
            tool_identifier=definition.identifier,
            valid=len(errors) == 0,
            errors=tuple(errors),
        )

    def validate_all(
        self,
        definition: ToolDefinition,
        parameters: dict[str, str],
        agent_id: str,
        workspace: str,
    ) -> ToolValidationReport:
        all_errors: list[str] = []
        all_warnings: list[str] = []
        for validator in (
            self.validate_input(definition, parameters),
            self.validate_permissions(definition, agent_id, workspace),
            self.validate_execution_policy(definition, workspace),
        ):
            all_errors.extend(validator.errors)
            all_warnings.extend(validator.warnings)
        return ToolValidationReport(
            tool_identifier=definition.identifier,
            valid=len(all_errors) == 0,
            errors=tuple(all_errors),
            warnings=tuple(all_warnings),
        )
