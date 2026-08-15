import json
import ssl
import urllib.error
import urllib.request


def disclosure_is_honest(payload):
    """NFR-005: claim AI generation only when assistant_mode is primary."""
    mode = payload.get("assistant_mode")
    disclosure = payload.get("disclosure") or ""
    generated = payload.get("ai_generated")
    if not disclosure:
        return False
    if mode == "primary":
        return generated is True and "AI-generated" in disclosure
    if mode in ("fallback", "reference"):
        return generated is False and "AI-generated" not in disclosure
    return False


context = ssl._create_unverified_context()
with urllib.request.urlopen("https://localhost:8443/", context=context, timeout=5) as response:
    page = response.read().decode()
    if (response.status != 200 or 'id="message-form"' not in page
            or 'id="understanding-title"' not in page
            or 'id="recommendations"' not in page
            or 'id="order-tracking"' not in page
            or "T-01" not in page
            or 'id="suggestions"' not in page
            or 'data-suggest="Birthday' in page
            or ">Wedding</button>" in page
            or ">Sympathy</button>" in page):
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

reuse_request = urllib.request.Request(
    "https://localhost:8443/api/v1/session", method="POST",
    headers={**base_headers, "Cookie": cookie})
with urllib.request.urlopen(reuse_request, context=context, timeout=5) as response:
    reused = json.load(response)
    if response.status != 201 or reused.get("csrf_token") != session["csrf_token"]:
        raise SystemExit("second session boot rotated CSRF and would reject the first tab")
print("session reuse preserves CSRF across a second boot")

projection_request = urllib.request.Request(
    "https://localhost:8443/api/v1/shared-understanding",
    headers={**base_headers, "Cookie": cookie})
with urllib.request.urlopen(projection_request, context=context, timeout=5) as response:
    projection = json.load(response)
    if (response.status != 200 or projection.get("context_version") != 0
            or projection.get("structured_intent") != {}
            or projection.get("suggestions") != []
            or not disclosure_is_honest(projection)):
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
            or not disclosure_is_honest(acceptance)):
        raise SystemExit("assistant did not analyze the accepted conversation")

with urllib.request.urlopen(projection_request, context=context, timeout=5) as response:
    projection = json.load(response)
    if projection["structured_intent"] != {
        "occasion": "birthday", "flower_preference": "roses"
    } or not projection["suggestions"] or not disclosure_is_honest(projection):
        raise SystemExit("assistant intent/fallback projection is unexpected")
print("24/7 assistant analysis and fallback path is healthy")

workspace_request = urllib.request.Request(
    "https://localhost:8443/api/v1/workspace",
    headers={**base_headers, "Cookie": cookie})
with urllib.request.urlopen(workspace_request, context=context, timeout=5) as response:
    workspace = json.load(response)
    items = workspace.get("facets", {}).get("recommendations", {}).get("items", [])
    available = next((item for item in items if item.get("available")), None)
    if available is None:
        raise SystemExit("T-03 recommendations have no available product")
    shared = workspace.get("facets", {}).get("shared_understanding") or {}
    if shared.get("suggestions") != projection["suggestions"] or not shared.get("suggestions"):
        raise SystemExit("T-01 workspace suggestions do not match Shared Understanding API")
print("T-01 thought-completion suggestions match Shared Understanding API")

selection_request = urllib.request.Request(
    "https://localhost:8443/api/v1/selection", method="POST",
    data=json.dumps({"product_id": available["product_id"],
                     "observed_context_version": workspace["context_version"]}).encode(),
    headers={**base_headers, "Cookie": cookie, "X-CSRF-Token": session["csrf_token"],
             "Content-Type": "application/json"})
try:
    with urllib.request.urlopen(selection_request, context=context, timeout=5) as response:
        selected = json.load(response)
        if response.status != 202 or selected.get("accepted") is not True:
            raise SystemExit("T-03 Select did not succeed against seeded inventory")
except urllib.error.HTTPError as exc:
    raise SystemExit(f"T-03 Select failed: {exc.code} {exc.read().decode()}") from exc
print("T-03 Select against seeded inventory is healthy")
