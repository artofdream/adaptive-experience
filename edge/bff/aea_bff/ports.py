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
    ai_generated: bool = False
    assistant_mode: str | None = None
    disclosure: str | None = None


@dataclass(frozen=True)
class CorrectionResult:
    accepted: bool
    code: str
    context_version: int
    message_id: str | None = None


@dataclass(frozen=True)
class SelectionResult:
    accepted: bool
    code: str
    context_version: int
    message_id: str | None = None


@dataclass(frozen=True)
class DeliveryResult:
    accepted: bool
    code: str
    context_version: int
    message_id: str | None = None


class OrchestrationPort(Protocol):
    def ensure_session(self, *, session_id: str, subject: str) -> None: ...
    def accept_command(self, *, session_id: str, subject: str, command: dict,
                       observed_context_version: int, correlation_id: str) -> CommandResult: ...
    def select_product(self, *, session_id: str, subject: str, product_id: str,
                       options: dict, observed_context_version: int,
                       correlation_id: str) -> SelectionResult: ...
    def update_delivery(self, *, session_id: str, subject: str, delivery: dict,
                        observed_context_version: int, correlation_id: str) -> DeliveryResult: ...
    def workspace_projection(self, *, session_id: str, subject: str) -> dict: ...
    def stream_events(self, *, session_id: str, subject: str,
                      after_event_id: str | None) -> Iterable[dict]: ...
    def submit_conversation_message(self, *, session_id: str, subject: str,
                                    message_text: str, observed_context_version: int,
                                    correlation_id: str) -> ConversationResult: ...
    def conversation_projection(self, *, session_id: str, subject: str) -> dict: ...
    def shared_understanding_projection(self, *, session_id: str, subject: str) -> dict: ...
    def correct_shared_understanding(self, *, session_id: str, subject: str,
                                     corrections: dict, observed_context_version: int,
                                     correlation_id: str) -> CorrectionResult: ...


class UnavailableOrchestration:
    """Safe runtime placeholder until an Orchestration adapter is configured."""

    def accept_command(self, **kwargs) -> CommandResult:
        return CommandResult(False, "orchestration_unavailable")

    def select_product(self, **kwargs) -> SelectionResult:
        return SelectionResult(False, "orchestration_unavailable", 0)

    def update_delivery(self, **kwargs) -> DeliveryResult:
        return DeliveryResult(False, "orchestration_unavailable", 0)

    def workspace_projection(self, **kwargs) -> dict:
        return {"context_version": 0, "tiles": []}

    def stream_events(self, **kwargs):
        return ()

    def submit_conversation_message(self, **kwargs) -> ConversationResult:
        return ConversationResult(False, "orchestration_unavailable", 0)

    def conversation_projection(self, **kwargs) -> dict:
        return {"context_version": 0, "messages": []}

    def shared_understanding_projection(self, **kwargs) -> dict:
        return {"context_version": 0, "structured_intent": {}, "suggestions": []}

    def correct_shared_understanding(self, **kwargs) -> CorrectionResult:
        return CorrectionResult(False, "orchestration_unavailable", 0)
    def ensure_session(self, **kwargs) -> None:
        raise RuntimeError("orchestration unavailable")
