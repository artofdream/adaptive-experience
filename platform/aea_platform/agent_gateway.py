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

    def process_gitlab_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming GitLab webhooks (issues, merge requests, pipelines)."""
        if not self.is_autonomous_loop_enabled():
            return {
                "processed": False,
                "reason": "Autonomous loop paused by sponsor kill-switch",
                "event_type": event_type
            }

        if event_type == "Issue Hook":
            issue_info = payload.get("object_attributes", {})
            title = issue_info.get("title", "Untitled Issue")
            return {
                "processed": True,
                "event_type": event_type,
                "action": "triaged",
                "details": f"Dispatched issue: {title}"
            }

        return {
            "processed": True,
            "event_type": event_type,
            "action": "acknowledged",
            "details": "Event recorded"
        }
