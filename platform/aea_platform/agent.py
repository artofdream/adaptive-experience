from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .support import SupportService, SupportValidationError

TOOL_NAME_MAX_LENGTH = 80
ARGUMENT_KEY_MAX_LENGTH = 80
ARGUMENT_VALUE_MAX_LENGTH = 500
MAX_ARGUMENT_KEYS = 8
MAX_RESULT_CHARS = 4000
LOOKUP_APPROVED_KNOWLEDGE = "lookup_approved_knowledge"
ALLOWED_SIDE_EFFECTS = frozenset({"read"})
FORBIDDEN_TOOL_NAMES = frozenset({
    "shell", "exec", "subprocess", "filesystem", "read_file", "write_file",
    "http", "http_fetch", "fetch", "sql", "query_sql", "psql",
    "place_order", "charge_payment", "submit_checkout", "mutate_inventory",
})


class AgentToolError(ValueError):
    """A tool call is unknown, denied, or malformed."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[[Mapping[str, object]], dict]
    argument_keys: frozenset[str]
    side_effect: str = "read"


@dataclass(frozen=True)
class ToolResult:
    tool: str
    ok: bool
    result: dict
    authoritative: bool = False


class AgentRuntime:
    """Fail-closed tool-calling boundary (ADR-016).

    The agent may invoke approved read tools and receive non-authoritative
    results. It does not hold DB credentials for orders, payments, inventory,
    or experience-state tables, and it does not publish governed events.
    """

    def __init__(self, tools: Sequence[ToolSpec], *, allowlist: Sequence[str] | None = None):
        specs: dict[str, ToolSpec] = {}
        for spec in tools:
            name = _tool_name(spec.name)
            if name in FORBIDDEN_TOOL_NAMES:
                raise AgentToolError(f"tool {name!r} is not permitted")
            if spec.side_effect not in ALLOWED_SIDE_EFFECTS:
                raise AgentToolError(f"tool {name!r} side effect is not permitted")
            if name in specs:
                raise AgentToolError(f"tool {name!r} is duplicated")
            specs[name] = spec
        if allowlist is None:
            allowed = frozenset(specs)
        else:
            allowed = frozenset(_tool_name(item) for item in allowlist)
            unknown = allowed - set(specs)
            if unknown:
                raise AgentToolError(
                    "allowlist contains unknown tools: " + ", ".join(sorted(unknown)))
        if not allowed:
            raise AgentToolError("tool allowlist is empty")
        self._tools = specs
        self._allowlist = allowed

    def allowed_tools(self) -> tuple[str, ...]:
        return tuple(sorted(name for name in self._allowlist if name in self._tools))

    def invoke(self, tool_name, arguments=None) -> ToolResult:
        name = _tool_name(tool_name)
        if name not in self._allowlist or name not in self._tools:
            raise AgentToolError(f"unknown tool {name!r}")
        spec = self._tools[name]
        payload = spec.handler(_arguments(arguments, spec.argument_keys))
        if not isinstance(payload, dict):
            raise AgentToolError(f"tool {name!r} result is invalid")
        if len(repr(payload)) > MAX_RESULT_CHARS:
            raise AgentToolError(f"tool {name!r} result is invalid")
        return ToolResult(tool=name, ok=True, result=payload, authoritative=False)


def approved_knowledge_tool(support: SupportService) -> ToolSpec:
    """Read-only concierge lookup against approved knowledge / optional retrieval."""

    def handler(arguments: Mapping[str, object]) -> dict:
        try:
            looked = support.lookup(arguments.get("question"))
        except SupportValidationError as error:
            raise AgentToolError(str(error)) from error
        return {
            "answer": looked["answer"],
            "approved_source_references": list(looked["approved_source_references"]),
            "matched": looked["matched"],
            "authoritative": False,
        }

    return ToolSpec(
        name=LOOKUP_APPROVED_KNOWLEDGE,
        description=(
            "Look up an approved FAQ or policy answer. Results are not business "
            "truth until a domain service validates them."
        ),
        handler=handler,
        argument_keys=frozenset({"question"}),
        side_effect="read",
    )


def reference_concierge_runtime(*, knowledge=None, retriever=None) -> AgentRuntime:
    """Reference ADR-016 path: one approved-knowledge read tool, fail-closed."""
    support = SupportService(
        _AgentMustNotPersistStore(), knowledge=knowledge, retriever=retriever)
    return AgentRuntime((approved_knowledge_tool(support),))


class _AgentMustNotPersistStore:
    def record_answer(self, **kwargs):
        raise AgentToolError("agent tools must not persist or publish FAQ answers")


def _tool_name(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentToolError("tool name is required")
    name = value.strip()
    if len(name) > TOOL_NAME_MAX_LENGTH or not name.replace("_", "").isalnum() or name[0] == "_":
        raise AgentToolError("tool name is invalid")
    return name


def _arguments(value, allowed_keys: frozenset[str]) -> dict[str, str]:
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise AgentToolError("tool arguments must be an object")
    if len(value) > MAX_ARGUMENT_KEYS:
        raise AgentToolError("tool arguments are invalid")
    cleaned: dict[str, str] = {}
    for key, item in value.items():
        if (not isinstance(key, str) or not key.strip()
                or len(key) > ARGUMENT_KEY_MAX_LENGTH):
            raise AgentToolError("tool argument key is invalid")
        name = key.strip()
        if name not in allowed_keys:
            raise AgentToolError(f"unknown tool argument {name!r}")
        if not isinstance(item, str):
            raise AgentToolError("tool argument values must be strings")
        text = item.strip()
        if (not text or len(text) > ARGUMENT_VALUE_MAX_LENGTH
                or any(ord(character) < 32 and character not in "\n\t" for character in text)):
            raise AgentToolError("tool argument is invalid")
        cleaned[name] = text
    missing = allowed_keys - set(cleaned)
    if missing:
        raise AgentToolError("tool argument is required")
    return cleaned
