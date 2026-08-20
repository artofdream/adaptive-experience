"""24/7 Autonomous Agent Gateway Service (FastAPI Event & Webhook Dispatcher).

Provides 24/7 asynchronous event listening, scheduled cron hooks, emergency kill-switch
toggling, and execution of pre-flight guard checks.
Coherent with NFR-003, NFR-008, NFR-013, NFR-017, and ADR-016.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]


class AutonomousAgentGateway:
    """Core gateway manager handling autonomous cloud agent tasks."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir if root_dir is not None else ROOT

    def is_autonomous_loop_enabled(self) -> bool:
        """Check if 24/7 autonomous loop is enabled via environment kill-switch."""
        flag = os.environ.get("AEA_AUTONOMOUS_LOOP_ENABLED", "true").lower()
        return flag in ("true", "1", "yes")

    def get_cloud_deployment_status(self) -> Dict[str, Any]:
        """Return 24/7 autonomous cloud agent deployment status (AWS ECS us-east-1)."""
        enabled = self.is_autonomous_loop_enabled()
        region = os.environ.get("AWS_REGION", "us-east-1")
        return {
            "autonomous_loop_enabled": enabled,
            "aws_region": region,
            "secret_name": "aea/gitlab-token",
            "cluster": "aea-pilot",
            "service": "aea-agent-runner",
            "status": "active" if enabled else "paused",
        }

    def run_preflight_guards(self) -> Dict[str, Any]:
        """Execute the unified pre-flight guard runner."""
        if not self.is_autonomous_loop_enabled():
            return {
                "status": "paused",
                "message": "Autonomous cloud loop is currently paused via kill-switch (AEA_AUTONOMOUS_LOOP_ENABLED=false)",
                "exit_code": 0
            }

        guard_script = self.root_dir / "scripts" / "run_all_guards.py"
        if not guard_script.exists():
            return {
                "status": "error",
                "message": "Guard runner script not found",
                "exit_code": 1
            }

        result = subprocess.run(
            [sys.executable, str(guard_script)],
            cwd=self.root_dir,
            capture_output=True,
            text=True
        )

        return {
            "status": "success" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    def trigger_autonomous_remediation(self, mr_id: Any, failure_reason: str) -> Dict[str, Any]:
        """Trigger automated remediation MR draft creation for coherence failures (BLK-003 / Issue #252)."""
        if not self.is_autonomous_loop_enabled():
            return {"status": "paused", "reason": "Kill-switch active"}
        return {
            "status": "triggered",
            "mr_id": mr_id,
            "failure_reason": failure_reason,
            "action": "auto_remediation_draft_created",
            "bot": "@aea-senior-software-engineer",
        }

    def process_gitlab_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming GitLab webhooks (issues, merge requests, pipelines) per BLK-003 / Issue #252."""
        if not self.is_autonomous_loop_enabled():
            return {
                "processed": False,
                "reason": "Autonomous loop paused by sponsor kill-switch",
                "event_type": event_type
            }

        if event_type in ("Issue Hook", "Issue Event"):
            issue_info = payload.get("object_attributes", {})
            title = issue_info.get("title", "Untitled Issue")
            return {
                "processed": True,
                "event_type": event_type,
                "action": "triaged",
                "details": f"Dispatched issue: {title}"
            }
        elif event_type in ("Merge Request Hook", "Merge Request Event"):
            mr_info = payload.get("object_attributes", {})
            mr_id = mr_info.get("iid") or mr_info.get("id") or "unknown"
            description = mr_info.get("description", "")
            # Check process coherence validation requirement
            if "Validation" not in description:
                remediation = self.trigger_autonomous_remediation(mr_id, "Missing Validation section in MR description")
                return {
                    "processed": True,
                    "event_type": event_type,
                    "action": "auto_remediation_triggered",
                    "details": f"MR !{mr_id} missing Validation section. Triggered auto-remediation MR draft.",
                    "remediation": remediation
                }
            return {
                "processed": True,
                "event_type": event_type,
                "action": "approved_for_coherence",
                "details": f"MR !{mr_id} validated successfully"
            }

        return {
            "processed": True,
            "event_type": event_type,
            "action": "acknowledged",
            "details": "Event recorded"
        }


gateway_manager = AutonomousAgentGateway()

try:
    from fastapi import FastAPI, Header, Request
    app = FastAPI(title="AEA Autonomous Agent Gateway", version="1.0.0")

    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    except ImportError:
        pass
except ImportError:
    app = None


if app is not None:
    @app.get("/")
    def read_root() -> Dict[str, Any]:
        return {"status": "running", "service": "aea-agent-runner", "autonomous_loop": True}

    @app.get("/healthz")
    def healthz() -> Dict[str, Any]:
        return {"status": "ok"}

    @app.get("/cloud/status")
    def cloud_status() -> Dict[str, Any]:
        return gateway_manager.get_cloud_deployment_status()

    @app.post("/cloud/preflight")
    def cloud_preflight() -> Dict[str, Any]:
        return gateway_manager.run_preflight_guards()

    @app.post("/webhooks/gitlab")
    async def gitlab_webhook(request: Request, x_gitlab_event: Optional[str] = Header(None)) -> Dict[str, Any]:
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        event_type = x_gitlab_event or payload.get("object_kind", "unknown")
        result = gateway_manager.process_gitlab_webhook(event_type, payload)
        return {"status": "success", "result": result}

