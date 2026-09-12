import os

import psycopg

from .internal_api import InternalOrchestrationApp
from .generative_ai import (
    AvailableIntentInterpreter,
    AvailableReminderCopyAuthor,
    OpenAICompatibleIntentInterpreter,
    OpenAICompatibleReminderCopyAuthor,
)


dsn = os.environ.get("AEA_POSTGRES_DSN")
token = os.environ.get("AEA_ORCHESTRATION_TOKEN")
if not dsn or not token:
    raise RuntimeError("AEA_POSTGRES_DSN and AEA_ORCHESTRATION_TOKEN are required")
endpoint = os.environ.get("AEA_AI_ENDPOINT")
api_key = os.environ.get("AEA_AI_API_KEY")
model = os.environ.get("AEA_AI_MODEL")
interpreter = None
reminder_copy_author = None
if os.environ.get("AEA_LOAD_TEST_MOCK_AI") == "1":
    from .intent import ReferenceIntentInterpreter
    interpreter = ReferenceIntentInterpreter()
elif endpoint or api_key or model:
    if not endpoint or not api_key or not model:
        raise RuntimeError("AEA_AI_ENDPOINT, AEA_AI_API_KEY, and AEA_AI_MODEL must be set together")
    timeout_seconds = float(os.environ.get("AEA_AI_TIMEOUT", "2.5"))
    interpreter = AvailableIntentInterpreter(OpenAICompatibleIntentInterpreter(
        endpoint, api_key, model, timeout_seconds=timeout_seconds))
    reminder_copy_author = AvailableReminderCopyAuthor(
        OpenAICompatibleReminderCopyAuthor(
            endpoint, api_key, model, timeout_seconds=timeout_seconds))
app = InternalOrchestrationApp(
    psycopg.connect(dsn, autocommit=True), token, interpreter,
    reminder_copy_author=reminder_copy_author)
