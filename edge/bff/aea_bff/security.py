from __future__ import annotations

import secrets
import time
import uuid
from dataclasses import dataclass


@dataclass
class Session:
    session_id: str
    subject: str
    csrf_token: str
    expires_at: float
    recall_id: str | None = None


class SessionStore:
    def __init__(self, ttl_seconds: int = 1800):
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, Session] = {}

    def create(self, subject: str, recall_id: str | None = None) -> Session:
        session = Session(str(uuid.uuid4()), subject, secrets.token_urlsafe(32),
                          time.time() + self.ttl_seconds, recall_id)
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str | None) -> Session | None:
        session = self._sessions.get(session_id or "")
        if session is None or session.expires_at <= time.time():
            self._sessions.pop(session_id or "", None)
            return None
        return session


class StaticTokenAuthenticator:
    def __init__(self, token: str):
        if not token:
            raise ValueError("authentication token must be supplied by the environment")
        self.token = token

    def authenticate(self, authorization: str | None) -> str | None:
        prefix = "Bearer "
        if not authorization or not authorization.startswith(prefix):
            return None
        candidate = authorization[len(prefix):]
        return "local-user" if secrets.compare_digest(candidate, self.token) else None


class FixedWindowRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._windows: dict[str, tuple[int, int]] = {}

    def allow(self, key: str) -> bool:
        window = int(time.time() // self.window_seconds)
        current_window, count = self._windows.get(key, (window, 0))
        if current_window != window:
            current_window, count = window, 0
        count += 1
        self._windows[key] = (current_window, count)
        return count <= self.limit
