from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from .state import StatePatch


class ConversationValidationError(ValueError):
    pass


class ConversationSessionNotFound(LookupError):
    pass


@dataclass(frozen=True)
class ConversationSubmission:
    message_id: str
    context_version: int
    correlation_id: str


class ConversationService:
    """Authoritative T-01 customer-message acceptance boundary (FR-001)."""

    MAX_MESSAGE_CHARS = 2000
    MAX_VISIBLE_MESSAGES = 50

    def __init__(self, state_store, *,
                 now: Callable[[], datetime] | None = None,
                 new_id: Callable[[], uuid.UUID] | None = None):
        self.state_store = state_store
        self.now = now or (lambda: datetime.now(timezone.utc))
        self.new_id = new_id or uuid.uuid4

    def submit(self, *, session_id: str, subject_reference: str,
               message_text: str, observed_context_version: int,
               correlation_id: str) -> ConversationSubmission:
        text = self._message_text(message_text)
        if (not isinstance(observed_context_version, int)
                or isinstance(observed_context_version, bool)
                or observed_context_version < 0):
            raise ConversationValidationError("observed context version is invalid")
        if not isinstance(subject_reference, str) or not subject_reference.strip():
            raise ConversationValidationError("subject reference is required")
        if not isinstance(correlation_id, str) or not correlation_id.strip():
            raise ConversationValidationError("correlation ID is required")
        current = self.state_store.load(session_id)
        if current is None:
            raise ConversationSessionNotFound(session_id)

        state = current.get("state") or {}
        conversation = state.get("conversation") or {}
        existing = conversation.get("messages") or []
        if not isinstance(existing, list):
            raise ConversationValidationError("conversation state is invalid")

        message_id = str(self.new_id())
        submitted_at = self.now().astimezone(timezone.utc).isoformat()
        entry = {
            "message_id": message_id,
            "role": "customer",
            "text": text,
            "status": "submitted",
            "submitted_at": submitted_at,
        }
        messages = (existing + [entry])[-self.MAX_VISIBLE_MESSAGES:]
        envelope = {
            "message_id": message_id,
            "topic": "customer.message.submitted",
            "message_type": "event",
            "schema_version": "1.0.0",
            "session_id": session_id,
            "correlation_id": correlation_id,
            "source": "orchestration",
            "context_version": observed_context_version + 1,
            "publication_time": submitted_at,
            "security_context": {
                "classification": "confidential",
                "subject_reference": subject_reference.strip(),
            },
            "payload": {"message_text": text},
            "outcome": {},
        }
        version = self.state_store.apply_patch(
            session_id,
            observed_context_version,
            int(current["state_schema_version"]),
            StatePatch.create(
                {"conversation": {"messages": messages}},
                ["conversation.messages"],
            ),
            [{
                "message_id": message_id,
                "topic": "customer.message.submitted",
                "aggregate_key": session_id,
                "envelope": envelope,
            }],
        )
        return ConversationSubmission(message_id, version, correlation_id)

    def projection(self, *, session_id: str) -> dict:
        current = self.state_store.load(session_id)
        if current is None:
            raise ConversationSessionNotFound(session_id)
        messages = ((current.get("state") or {}).get("conversation") or {}).get("messages") or []
        safe = []
        for item in messages[-self.MAX_VISIBLE_MESSAGES:]:
            if not isinstance(item, dict):
                continue
            safe.append({key: item[key] for key in
                         ("message_id", "role", "text", "status", "submitted_at")
                         if key in item})
        return {"context_version": int(current["context_version"]), "messages": safe}

    def _message_text(self, value: str) -> str:
        if not isinstance(value, str):
            raise ConversationValidationError("message text must be a string")
        text = value.strip()
        if not text or len(text) > self.MAX_MESSAGE_CHARS:
            raise ConversationValidationError("message text length is invalid")
        if any(ord(character) < 32 and character not in "\n\t" for character in text):
            raise ConversationValidationError("message text contains control characters")
        return text
