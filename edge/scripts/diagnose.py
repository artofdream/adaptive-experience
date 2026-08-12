import json
import ssl
import urllib.request


context = ssl._create_unverified_context()
with urllib.request.urlopen("https://localhost:8443/", context=context, timeout=5) as response:
    page = response.read().decode()
    if (response.status != 200 or 'id="message-form"' not in page
            or 'id="understanding-title"' not in page):
        raise SystemExit("guided browser interface is unavailable")
print("guided browser interface is available")

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
    if (response.status != 200 or projection.get("context_version") != 0
            or projection.get("structured_intent") != {}
            or projection.get("suggestions") != []
            or projection.get("ai_generated") is not True
            or "AI-generated" not in projection.get("disclosure", "")):
        raise SystemExit("Shared Understanding projection is unexpected")
print("authenticated Edge-to-Orchestration Shared Understanding path is healthy")

message_request = urllib.request.Request(
    "https://localhost:8443/api/v1/conversation/messages", method="POST",
    data=json.dumps({"message_text": "birthday roses",
                     "observed_context_version": 0}).encode(),
    headers={**base_headers, "Cookie": cookie, "X-CSRF-Token": session["csrf_token"],
             "Content-Type": "application/json"})
with urllib.request.urlopen(message_request, context=context, timeout=5) as response:
    acceptance = json.load(response)
    if (response.status != 202 or acceptance.get("context_version") != 2
            or acceptance.get("ai_generated") is not True
            or "AI-generated" not in acceptance.get("disclosure", "")):
        raise SystemExit("assistant did not analyze the accepted conversation")

with urllib.request.urlopen(projection_request, context=context, timeout=5) as response:
    projection = json.load(response)
    if projection["structured_intent"] != {
        "occasion": "birthday", "flower_preference": "roses"
    } or not projection["suggestions"] or projection.get("ai_generated") is not True:
        raise SystemExit("assistant intent/fallback projection is unexpected")
print("24/7 assistant analysis and fallback path is healthy")
