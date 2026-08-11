import json
import ssl
import urllib.request


context = ssl._create_unverified_context()
with urllib.request.urlopen("https://localhost:8443/healthz", context=context, timeout=5) as response:
    payload = json.load(response)
    if response.status != 200 or payload != {"status": "ok"}:
        raise SystemExit("edge health check returned an unexpected response")
print("edge gateway and BFF are healthy")
