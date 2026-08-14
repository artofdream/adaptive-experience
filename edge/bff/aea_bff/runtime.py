import os

from .app import BffApp
from .orchestration import HttpOrchestration
from .security import StaticTokenAuthenticator


def create_app() -> BffApp:
    token = os.environ.get("AEA_LOCAL_BEARER_TOKEN")
    if not token:
        raise RuntimeError("AEA_LOCAL_BEARER_TOKEN is required")
    orchestration_url = os.environ.get("AEA_ORCHESTRATION_URL")
    orchestration_token = os.environ.get("AEA_ORCHESTRATION_TOKEN")
    if not orchestration_url or not orchestration_token:
        raise RuntimeError("AEA_ORCHESTRATION_URL and AEA_ORCHESTRATION_TOKEN are required")
    florist_operator_enabled = BffApp.florist_operator_enabled_for(
        environment=os.environ.get("AEA_ENVIRONMENT", "local"),
        flag=os.environ.get("AEA_FLORIST_OPERATOR"),
    )
    return BffApp(
        HttpOrchestration(orchestration_url, orchestration_token),
        StaticTokenAuthenticator(token),
        allowed_origin=os.environ.get("AEA_ALLOWED_ORIGIN", "https://localhost:8443"),
        florist_operator_enabled=florist_operator_enabled,
    )


app = create_app()
