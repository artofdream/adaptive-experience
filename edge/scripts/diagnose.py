import json
import ssl
import urllib.request


context = ssl._create_unverified_context()
with urllib.request.urlopen("https://localhost:8443/healthz", context=context, timeout=5) as response:
    payload = json.load(response)
    if response.status != 200 or payload != {"status": "ok"}:
        raise SystemExit("edge health check returned an unexpected response")
print("edge gateway and BFF are healthy")

base_headers = {
    "Authorization": "Bearer local-browser-token",
    "Origin": "https://localhost:8443",
}
session_request = urllib.request.Request(
    "https://localhost:8443/api/v1/session", method="POST", headers=base_headers)
with urllib.request.urlopen(session_request, context=context, timeout=5) as response:
    session = json.load(response)
    cookie = response.headers["Set-Cookie"].split(";", 1)[0]
    if response.status != 201 or not session.get("csrf_token") or not cookie:
        raise SystemExit("browser session did not reach orchestration")

projection_request = urllib.request.Request(
    "https://localhost:8443/api/v1/shared-understanding",
    headers={**base_headers, "Cookie": cookie})
with urllib.request.urlopen(projection_request, context=context, timeout=5) as response:
    projection = json.load(response)
    if response.status != 200 or projection != {
        "context_version": 0, "structured_intent": {}, "suggestions": []
    }:
        raise SystemExit("Shared Understanding projection is unexpected")
print("authenticated Edge-to-Orchestration Shared Understanding path is healthy")
