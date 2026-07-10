from __future__ import annotations

from jarvis_brain.models import BrainRequest, Capability, ExecutionContext, Intent, IntentKind


class RuleBasedIntentEngine:
    def determine_intent(self, request: BrainRequest, context: ExecutionContext) -> Intent:
        _ = context
        query = request.normalized_message.casefold()
        if not query:
            return Intent(
                kind=IntentKind.CLARIFICATION,
                confidence=1.0,
                ambiguous=True,
                required_capabilities=(Capability.CLARIFICATION,),
                missing_information=("message",),
                entities=(),
                normalized_query=query,
            )

        matched_intents = self._detect_intents(query)
        ambiguous = len(matched_intents) > 1
        primary_kind = matched_intents[0] if matched_intents else IntentKind.GENERAL_RESPONSE
        required_capabilities = self._capabilities_for(primary_kind)
        if ambiguous:
            required_capabilities = (*required_capabilities, Capability.CLARIFICATION)

        missing_information: tuple[str, ...] = ()
        if "?" in query and query.count("?") > 2:
            missing_information = ("focused_question",)
            ambiguous = True
        if "it" in query and "context" not in query and "conversation" not in query:
            missing_information = tuple(dict.fromkeys((*missing_information, "referent")))

        entities = tuple(word for word in query.replace("?", "").split(" ") if len(word) > 5)[:8]
        confidence = min(0.55 + (0.1 * len(matched_intents)), 0.95)
        if primary_kind == IntentKind.CLARIFICATION:
            confidence = 0.9

        return Intent(
            kind=primary_kind,
            confidence=confidence,
            ambiguous=ambiguous,
            required_capabilities=tuple(dict.fromkeys(required_capabilities)),
            missing_information=missing_information,
            entities=entities,
            normalized_query=query,
        )

    def _detect_intents(self, query: str) -> tuple[IntentKind, ...]:
        detected: list[IntentKind] = []
        if any(token in query for token in ("research", "investigate", "analyze", "compare")):
            detected.append(IntentKind.RESEARCH)
        if any(token in query for token in ("memory", "remember", "recall", "history")):
            detected.append(IntentKind.MEMORY)
        if any(token in query for token in ("knowledge", "kb", "documentation", "docs")):
            detected.append(IntentKind.KNOWLEDGE)
        if any(token in query for token in ("run", "execute", "tool", "build", "deploy")):
            detected.append(IntentKind.TOOL_WORKFLOW)
        if any(token in query for token in ("delegate", "agent", "specialist", "team")):
            detected.append(IntentKind.AGENT_WORKFLOW)
        if any(token in query for token in ("clarify", "what do you mean", "not clear")):
            detected.append(IntentKind.CLARIFICATION)
        return tuple(dict.fromkeys(detected))

    def _capabilities_for(self, kind: IntentKind) -> tuple[Capability, ...]:
        match kind:
            case IntentKind.RESEARCH:
                return (Capability.RESEARCH, Capability.KNOWLEDGE_QUERY, Capability.RESPOND)
            case IntentKind.MEMORY:
                return (Capability.MEMORY_ACCESS, Capability.RESPOND)
            case IntentKind.KNOWLEDGE:
                return (Capability.KNOWLEDGE_QUERY, Capability.RESPOND)
            case IntentKind.TOOL_WORKFLOW:
                return (Capability.TOOL_COORDINATION, Capability.RESPOND)
            case IntentKind.AGENT_WORKFLOW:
                return (Capability.AGENT_COORDINATION, Capability.RESPOND)
            case IntentKind.CLARIFICATION:
                return (Capability.CLARIFICATION,)
            case _:
                return (Capability.RESPOND,)
