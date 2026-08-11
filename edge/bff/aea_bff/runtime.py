import os

from .app import BffApp
from .ports import UnavailableOrchestration
from .security import StaticTokenAuthenticator


def create_app() -> BffApp:
    token = os.environ.get("AEA_LOCAL_BEARER_TOKEN")
    if not token:
        raise RuntimeError("AEA_LOCAL_BEARER_TOKEN is required")
    return BffApp(
        UnavailableOrchestration(),
        StaticTokenAuthenticator(token),
        allowed_origin=os.environ.get("AEA_ALLOWED_ORIGIN", "https://localhost:8443"),
    )


app = create_app()
