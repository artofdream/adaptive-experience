from __future__ import annotations

import json
import urllib.error
import urllib.request

from .ports import (CheckoutResult, CommandResult, ConversationResult, CorrectionResult,
                    DeliveryResult, EscalationResult, OrderResult, SelectionResult, SupportResult)


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
                                  int(data.get("context_version", 0)), data.get("message_id"),
                                  bool(data.get("ai_generated", False)),
                                  data.get("assistant_mode"), data.get("disclosure"))

    def ensure_session(self, **kwargs):
        payload = {}
        recall_id = kwargs.get("recall_id")
        if recall_id:
            payload["recall_id"] = recall_id
        self._call("PUT", f"/internal/v1/sessions/{kwargs['session_id']}",
                   subject=kwargs["subject"], payload=payload)

    def load_session(self, **kwargs):
        return self._call("GET", f"/internal/v1/sessions/{kwargs['session_id']}",
                          subject=kwargs["subject"])

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
        # Deferred by design: selection and later actions use dedicated endpoints
        # (POST /api/v1/selection, #142). The generic command envelope is not
        # adopted until deliberately standardized. See #144 and
        # research/design-notes/edge-workspace-projection-contract.md.
        return CommandResult(False, "orchestration_unavailable")

    def select_product(self, **kwargs):
        payload = {
            "product_id": kwargs["product_id"],
            "options": kwargs["options"],
            "observed_context_version": kwargs["observed_context_version"],
            "correlation_id": kwargs["correlation_id"],
        }
        if "items" in kwargs and kwargs["items"] is not None:
            payload["items"] = kwargs["items"]
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/selection",
                          subject=kwargs["subject"], payload=payload)
        return SelectionResult(data["status"] == 202, data.get("code", "rejected"),
                               int(data.get("context_version", 0)), data.get("message_id"))

    def update_delivery(self, **kwargs):
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/delivery",
                          subject=kwargs["subject"], payload={
                              "delivery": kwargs["delivery"],
                              "observed_context_version": kwargs["observed_context_version"],
                              "correlation_id": kwargs["correlation_id"],
                          })
        return DeliveryResult(data["status"] == 202, data.get("code", "rejected"),
                              int(data.get("context_version", 0)), data.get("message_id"))

    def create_order(self, **kwargs):
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/order",
                          subject=kwargs["subject"],
                          payload={"correlation_id": kwargs["correlation_id"]})
        return OrderResult(data["status"] == 202, data.get("code", "rejected"),
                           data.get("order_id"), data.get("order_status"))

    def checkout(self, **kwargs):
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/checkout",
                          subject=kwargs["subject"], payload={
                              "payment_reference": kwargs["payment_reference"],
                              "observed_total": kwargs["observed_total"],
                              "correlation_id": kwargs["correlation_id"],
                          })
        return CheckoutResult(data["status"] == 202, data.get("code", "rejected"),
                              data.get("order_id"), data.get("order_status"),
                              data.get("decline_code"))

    def ask_support(self, **kwargs):
        data = self._call("POST", f"/internal/v1/sessions/{kwargs['session_id']}/support",
                          subject=kwargs["subject"], payload={
                              "question": kwargs["question"],
                              "correlation_id": kwargs["correlation_id"],
                          })
        return SupportResult(data["status"] == 200, data.get("code", "rejected"),
                             data.get("answer"),
                             tuple(data.get("approved_source_references") or ()),
                             bool(data.get("matched", False)),
                             data.get("kind") or "faq",
                             tuple(data.get("fact_references") or ()))

    def request_escalation(self, **kwargs):
        data = self._call("POST",
                          f"/internal/v1/sessions/{kwargs['session_id']}/support/escalation",
                          subject=kwargs["subject"], payload={
                              "reason": kwargs["reason"],
                              "correlation_id": kwargs["correlation_id"],
                          })
        return EscalationResult(data["status"] == 202, data.get("code", "rejected"),
                                data.get("message_id"), data.get("acknowledgement"),
                                data.get("escalation_reason"))

    def list_operator_escalations(self, **kwargs):
        return self._call("GET", "/internal/v1/operator/escalations",
                          subject=kwargs["subject"])

    def list_operator_orders(self, **kwargs):
        return self._call("GET", "/internal/v1/operator/orders",
                          subject=kwargs["subject"])

    def list_operator_forecasts(self, **kwargs):
        return self._call(
            "GET",
            f"/internal/v1/operator/forecasts?session_id={kwargs['session_id']}",
            subject=kwargs["subject"])

    def operator_session_summary(self, **kwargs):
        return self._call("GET", f"/internal/v1/operator/sessions/{kwargs['session_id']}",
                          subject=kwargs["subject"])

    def workspace_projection(self, **kwargs):
        return self._call("GET", f"/internal/v1/sessions/{kwargs['session_id']}/workspace",
                          subject=kwargs["subject"])

    def stream_events(self, **kwargs):
        path = f"/internal/v1/sessions/{kwargs['session_id']}/stream"
        after = kwargs.get("after_event_id")
        if after:
            path += f"?after={after}"
        data = self._call("GET", path, subject=kwargs["subject"])
        return data.get("events", [])

    def list_crm_reminders(self, **kwargs):
        return self._call(
            "GET",
            f"/internal/v1/crm/reminders?browser_hash={kwargs['browser_hash']}",
            subject=kwargs["subject"])

    def record_crm_occasion(self, **kwargs):
        return self._call(
            "POST",
            "/internal/v1/crm/occasions",
            subject=kwargs["subject"], payload={
                "browser_hash": kwargs["browser_hash"],
                "session_id": kwargs["session_id"],
                "occasion_type": kwargs["occasion_type"],
                "event_month": kwargs["event_month"],
                "event_day": kwargs["event_day"],
                "recipient_relation": kwargs.get("recipient_relation", "other"),
            })

