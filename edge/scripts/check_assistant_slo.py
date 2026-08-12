import json
import math
import ssl
import time
import urllib.request


BASE_URL = "https://localhost:8443"
SLO_SECONDS = 3.0
SAMPLE_COUNT = 10


def nearest_rank_percentile(samples, percentile):
    if not samples:
        raise ValueError("at least one latency sample is required")
    ordered = sorted(samples)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def post_json(url, payload, headers, context):
    request = urllib.request.Request(
        url, method="POST", data=json.dumps(payload).encode(),
        headers={**headers, "Content-Type": "application/json"},
    )
    started = time.monotonic()
    with urllib.request.urlopen(request, context=context, timeout=5) as response:
        body = json.load(response)
        elapsed = time.monotonic() - started
        return response.status, body, response.headers, elapsed


def main():
    context = ssl._create_unverified_context()
    base_headers = {
        "Authorization": "Bearer local-browser-token",
        "Origin": BASE_URL,
    }
    status, session, response_headers, _ = post_json(
        f"{BASE_URL}/api/v1/session", {}, base_headers, context)
    cookie = response_headers["Set-Cookie"].split(";", 1)[0]
    if status != 201 or not session.get("csrf_token") or not cookie:
        raise SystemExit("could not create an authenticated performance-test session")

    headers = {
        **base_headers,
        "Cookie": cookie,
        "X-CSRF-Token": session["csrf_token"],
    }
    context_version = 0
    latencies = []
    standard_queries = (
        "birthday roses for Mum",
        "keep the budget under 75 euros",
        "deliver them tomorrow",
        "make the style cheerful",
        "birthday tulips for Dad",
    )
    for index in range(SAMPLE_COUNT):
        status, result, _, elapsed = post_json(
            f"{BASE_URL}/api/v1/conversation/messages",
            {"message_text": standard_queries[index % len(standard_queries)],
             "observed_context_version": context_version},
            headers, context,
        )
        if status != 202 or not result.get("accepted"):
            raise SystemExit(f"standard query {index + 1} was not accepted: {result}")
        context_version = result["context_version"]
        latencies.append(elapsed)

    p95 = nearest_rank_percentile(latencies, 0.95)
    maximum = max(latencies)
    print(
        f"assistant standard-query SLO: samples={len(latencies)} "
        f"p95={p95:.3f}s max={maximum:.3f}s target={SLO_SECONDS:.1f}s"
    )
    if maximum > SLO_SECONDS:
        raise SystemExit(
            f"NFR-004 failed: a standard query took {maximum:.3f}s "
            f"(limit {SLO_SECONDS:.1f}s)"
        )


if __name__ == "__main__":
    main()
