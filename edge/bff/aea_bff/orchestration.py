from __future__ import annotations

import json
import urllib.error
import urllib.request

from .ports import CommandResult, ConversationResult, CorrectionResult


class OrchestrationUnavailable(RuntimeError):
    pass


class HttpOrchestration:
    """Authenticated service-to-service adapter; the BFF never reaches persistence."""

    def __init__(self, base_url: str, token: str, *, timeout_seconds: float = 3.0,
                 transport=None):
        if not base_url or not token:
            raise ValueError("orchestration URL and token are required")
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = timeout_seconds
        self.transport = transport or self._urllib

    def _call(self, method: str, path: str, *, subject: str, payload=None) -> dict:
        headers = {"authorization": f"Bearer {self.token}", "x-subject-reference": subject}
        try:
            status, body = self.transport(method, self.base_url + path, headers, payload,
                                          self.timeout_seconds)
        except (OSError, TimeoutError, urllib.error.URLError) as error:
            raise OrchestrationUnavailable("orchestration unavailable") from error
        data = json.loads(body or "{}")
        if status >= 500:
            raise OrchestrationUnavailable("orchestration unavailable")
        return {"status": status, **data}

    @staticmethod
    def _urllib(method, url, headers, payload, timeout):
        data = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(url, data=data, method=method, headers={
            **headers, **({"content-type": "application/json"} if data else {}),
        })
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, response.read().decode()
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode()

    def submit_conversation_message(self, **kwargs):
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/conversation",
                          subject=kwargs["subject"], payload={
                              "message_text": kwargs["message_text"],
                              "observed_context_version": kwargs["observed_context_version"],
                              "correlation_id": kwargs["correlation_id"],
                          })
        return ConversationResult(data["status"] == 202, data.get("code", "rejected"),
                                  int(data.get("context_version", 0)), data.get("message_id"))

    def ensure_session(self, **kwargs):
        self._call("PUT", f"/internal/v1/sessions/{kwargs['session_id']}",
                   subject=kwargs["subject"], payload={})

    def conversation_projection(self, **kwargs):
        return self._call("GET", f"/internal/v1/sessions/{kwargs['session_id']}/conversation",
                          subject=kwargs["subject"])

    def shared_understanding_projection(self, **kwargs):
        return self._call("GET", f"/internal/v1/sessions/{kwargs['session_id']}/shared-understanding",
                          subject=kwargs["subject"])

    def correct_shared_understanding(self, **kwargs):
        data = self._call(
            "PATCH", f"/internal/v1/sessions/{kwargs['session_id']}/shared-understanding",
            subject=kwargs["subject"], payload={
                "corrections": kwargs["corrections"],
                "observed_context_version": kwargs["observed_context_version"],
                "correlation_id": kwargs["correlation_id"],
            })
        return CorrectionResult(data["status"] == 202, data.get("code", "rejected"),
                                int(data.get("context_version", 0)), data.get("message_id"))

    def accept_command(self, **kwargs):
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/commands",
                          subject=kwargs["subject"], payload=kwargs)
        return CommandResult(data["status"] == 202, data.get("code", "rejected"))

    def workspace_projection(self, **kwargs):
        return self._call("GET", f"/internal/v1/sessions/{kwargs['session_id']}/workspace",
                          subject=kwargs["subject"])

    def stream_events(self, **kwargs):
        return ()
