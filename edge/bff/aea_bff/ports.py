from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class CommandResult:
    accepted: bool
    code: str


@dataclass(frozen=True)
class ConversationResult:
    accepted: bool
    code: str
    context_version: int
    message_id: str | None = None


class OrchestrationPort(Protocol):
    def accept_command(self, *, session_id: str, subject: str, command: dict,
                       observed_context_version: int, correlation_id: str) -> CommandResult: ...
    def workspace_projection(self, *, session_id: str, subject: str) -> dict: ...
    def stream_events(self, *, session_id: str, subject: str,
                      after_event_id: str | None) -> Iterable[dict]: ...
    def submit_conversation_message(self, *, session_id: str, subject: str,
                                    message_text: str, observed_context_version: int,
                                    correlation_id: str) -> ConversationResult: ...
    def conversation_projection(self, *, session_id: str, subject: str) -> dict: ...


class UnavailableOrchestration:
    """Safe runtime placeholder until an Orchestration adapter is configured."""

    def accept_command(self, **kwargs) -> CommandResult:
        return CommandResult(False, "orchestration_unavailable")

    def workspace_projection(self, **kwargs) -> dict:
        return {"context_version": 0, "tiles": []}

    def stream_events(self, **kwargs):
        return ()

    def submit_conversation_message(self, **kwargs) -> ConversationResult:
        return ConversationResult(False, "orchestration_unavailable", 0)

    def conversation_projection(self, **kwargs) -> dict:
        return {"context_version": 0, "messages": []}
