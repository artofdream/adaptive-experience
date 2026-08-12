import os

import psycopg

from .internal_api import InternalOrchestrationApp


dsn = os.environ.get("AEA_POSTGRES_DSN")
token = os.environ.get("AEA_ORCHESTRATION_TOKEN")
if not dsn or not token:
    raise RuntimeError("AEA_POSTGRES_DSN and AEA_ORCHESTRATION_TOKEN are required")
app = InternalOrchestrationApp(psycopg.connect(dsn, autocommit=True), token)
