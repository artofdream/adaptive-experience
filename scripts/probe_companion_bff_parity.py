#!/usr/bin/env python3
"""Companion BFF weekday/CI API parity probe (#369).

Exercises the same Need → Pick → Pay HTTP contracts as Android
``BffClient`` / ``SessionRepository.completeCheckout`` against live Path B
(``https://aea.artof.link`` by default, or ``AEA_BFF_BASE_URL``).

Contract mirror (!376 / !379 / !367 / !388):
  - Cookie jar (``__Host-aea_session`` + ``__Host-aea_recall``) + ``X-CSRF-Token``
  - Public Bearer ``local-browser-token`` (not a secret / not session auth)
  - ``X-AEA-Client: companion-android`` (observability only, #368)
  - Conversation ``message_text`` + ``observed_context_version``
  - Selection → delivery → workspace ``order_summary.total`` → order → checkout
  - Checkout ``observed_total`` from workspace after delivery (not product-only)

Honesty (do not soften):
  - Probe success ≠ Play honesty gate (App Dist / debug ≠ Play internal).
  - Probe success ≠ operator / website write-through (#360 dual-probe still open).
  - T-09 Lily's Florist Operator sample inbox ≠ live atelier orders.
  - Do not claim dual-probe write-through from a green run of this script.

On failure: exit non-zero with correlation ids in the log. This job does **not**
auto-open GitLab issues (avoid spam); open one finding issue manually if drift
is confirmed (one finding → one issue → one MR).
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse

DEFAULT_BASE_URL = "https://aea.artof.link"
PUBLIC_BROWSER_BEARER = "local-browser-token"
CLIENT_HEADER_NAME = "X-AEA-Client"
CLIENT_HEADER_VALUE = "companion-android"
SESSION_PAYMENT_REFERENCE = "session_pay_ref"
SESSION_DESTINATION_REFERENCE = "home"
REFERENCE_DELIVERY_FEE = 12.0
USER_AGENT = "aea-companion-bff-parity-probe/1.0 (#369)"


@dataclass
class StepRecord:
    name: str
    method: str
    path: str
    status: int | None = None
    correlation_id: str | None = None
    context_version: int | None = None
    ok: bool = False
    detail: str = ""
    error_code: str | None = None


@dataclass
class ProbeReport:
    base_url: str
    client: str = CLIENT_HEADER_VALUE
    started_at: str = ""
    finished_at: str = ""
    result: str = "fail"  # pass | fail | skip
    steps: list[StepRecord] = field(default_factory=list)
    correlation_ids: list[str] = field(default_factory=list)
    product_id: str | None = None
    product_price: float | None = None
    observed_total: float | None = None
    order_id: str | None = None
    checkout_status: str | None = None
    notes: list[str] = field(default_factory=list)
    honesty: list[str] = field(
        default_factory=lambda: [
            "probe ≠ Play honesty gate",
            "probe ≠ #360 dual-probe / operator write-through",
            "T-09 operator sample ≠ live orders",
        ]
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "probe": "companion-bff-parity",
            "issue": "#369",
            "base_url": self.base_url,
            "client": self.client,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result": self.result,
            "product_id": self.product_id,
            "product_price": self.product_price,
            "observed_total": self.observed_total,
            "order_id": self.order_id,
            "checkout_status": self.checkout_status,
            "correlation_ids": self.correlation_ids,
            "steps": [
                {
                    "name": s.name,
                    "method": s.method,
                    "path": s.path,
                    "status": s.status,
                    "correlation_id": s.correlation_id,
                    "context_version": s.context_version,
                    "ok": s.ok,
                    "detail": s.detail,
                    "error_code": s.error_code,
                }
                for s in self.steps
            ],
            "notes": self.notes,
            "honesty": self.honesty,
        }


def is_weekend_utc(now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    return now.weekday() >= 5  # Sat=5 Sun=6


def validate_base_url(url: str) -> str:
    parsed = urlparse(url.rstrip("/"))
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("base URL must be HTTPS with a hostname")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("base URL must not include credentials, query, or fragment")
    if parsed.path not in ("", "/"):
        raise ValueError("base URL must be an origin (no path)")
    return f"{parsed.scheme}://{parsed.hostname}" + (
        f":{parsed.port}" if parsed.port else ""
    )


def extract_error_code(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("code", "error"):
        val = payload.get(key)
        if isinstance(val, str) and val:
            return val
    return None


def pick_available_product(workspace: dict[str, Any]) -> dict[str, Any] | None:
    facets = workspace.get("facets") or {}
    recs = facets.get("recommendations") or {}
    items = recs.get("items") if isinstance(recs, dict) else recs
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, dict) and item.get("available") and item.get("product_id"):
            return item
    return None


def order_summary_total(workspace: dict[str, Any]) -> float | None:
    facets = workspace.get("facets") or {}
    summary = facets.get("order_summary") or {}
    if not isinstance(summary, dict):
        return None
    total = summary.get("total")
    if isinstance(total, (int, float)):
        return float(total)
    return None


class CompanionBffProbe:
    """HTTP client mirroring companion BffClient cookie + CSRF + client header."""

    def __init__(
        self,
        base_url: str,
        *,
        bearer: str = PUBLIC_BROWSER_BEARER,
        client_value: str = CLIENT_HEADER_VALUE,
        timeout: float = 45.0,
        insecure: bool = False,
    ) -> None:
        self.base_url = validate_base_url(base_url)
        self.bearer = bearer
        self.client_value = client_value
        self.timeout = timeout
        self.csrf_token = ""
        self.cookie_jar = http.cookiejar.CookieJar()
        ctx = ssl._create_unverified_context() if insecure else ssl.create_default_context()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
            urllib.request.HTTPSHandler(context=ctx),
        )

    def clear_session_state(self) -> None:
        self.cookie_jar.clear()
        self.csrf_token = ""

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        csrf: bool = False,
    ) -> tuple[int, dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.bearer}",
            CLIENT_HEADER_NAME: self.client_value,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if csrf and self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            status = exc.code
        except urllib.error.URLError as exc:
            raise RuntimeError(f"network error {method} {path}: {exc}") from exc

        if not raw.strip():
            payload: dict[str, Any] = {}
        else:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"non-JSON body {method} {path} status={status}: {raw[:240]}"
                ) from exc
            payload = parsed if isinstance(parsed, dict) else {"_value": parsed}
        return status, payload


def _log(msg: str) -> None:
    print(msg, flush=True)


def run_probe(args: argparse.Namespace) -> ProbeReport:
    report = ProbeReport(base_url=validate_base_url(args.base_url))
    report.started_at = datetime.now(timezone.utc).isoformat()
    report.client = args.client

    if args.skip_weekends and is_weekend_utc():
        report.result = "skip"
        report.notes.append("weekend UTC — skipped (weekday schedule)")
        report.finished_at = datetime.now(timezone.utc).isoformat()
        _log("SKIP: weekend UTC (AEA_PARITY_PROBE_SKIP_WEEKENDS)")
        return report

    client = CompanionBffProbe(
        args.base_url,
        bearer=args.bearer,
        client_value=args.client,
        timeout=args.timeout,
        insecure=args.insecure,
    )

    def step(
        name: str,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        csrf: bool = False,
        expect: set[int],
    ) -> dict[str, Any]:
        status, payload = client.request(method, path, body=body, csrf=csrf)
        corr = payload.get("correlation_id")
        if isinstance(corr, str) and corr:
            report.correlation_ids.append(corr)
        cv = payload.get("context_version")
        cv_int = cv if isinstance(cv, int) else None
        code = extract_error_code(payload)
        ok = status in expect
        rec = StepRecord(
            name=name,
            method=method,
            path=path,
            status=status,
            correlation_id=corr if isinstance(corr, str) else None,
            context_version=cv_int,
            ok=ok,
            detail="" if ok else f"expected {sorted(expect)} got {status} code={code}",
            error_code=code,
        )
        report.steps.append(rec)
        _log(
            f"{'OK' if ok else 'FAIL'} {name}: {method} {path} -> {status}"
            f" corr={rec.correlation_id} cv={cv_int} code={code}"
        )
        if not ok:
            raise RuntimeError(
                f"{name} failed: HTTP {status} code={code} corr={rec.correlation_id}"
            )
        return payload

    try:
        # 1) Session (+ CSRF); cookies land in jar
        sess = step("session", "POST", "/api/v1/session", expect={201})
        csrf = sess.get("csrf_token")
        if not isinstance(csrf, str) or not csrf:
            raise RuntimeError("session response missing csrf_token")
        client.csrf_token = csrf
        cookie_names = sorted({c.name for c in client.cookie_jar})
        report.notes.append(f"cookies={cookie_names}")
        if not any(n.startswith("__Host-aea_") for n in cookie_names):
            raise RuntimeError(f"expected __Host-aea_* cookies, got {cookie_names}")

        # 2) Need — conversation
        msg = step(
            "conversation",
            "POST",
            "/api/v1/conversation/messages",
            body={
                "message_text": args.message,
                "observed_context_version": 0,
            },
            csrf=True,
            expect={202},
        )
        context_version = int(msg.get("context_version") or 0)

        # 3) Poll workspace for available recommendation (catalog may lag)
        product: dict[str, Any] | None = None
        workspace: dict[str, Any] = {}
        for attempt in range(args.poll_attempts):
            time.sleep(args.poll_interval)
            workspace = step(
                f"workspace_poll_{attempt}",
                "GET",
                "/api/v1/workspace",
                expect={200},
            )
            context_version = int(workspace.get("context_version") or context_version)
            product = pick_available_product(workspace)
            if product:
                break
        if not product:
            raise RuntimeError(
                "no available recommendation after polling — catalog drift or empty facets"
            )
        report.product_id = str(product["product_id"])
        price = product.get("price")
        report.product_price = float(price) if isinstance(price, (int, float)) else None

        # 4) Pick — selection
        sel = step(
            "selection",
            "POST",
            "/api/v1/selection",
            body={
                "product_id": report.product_id,
                "options": {"card_message": args.card_message[:280]},
                "observed_context_version": context_version,
            },
            csrf=True,
            expect={202},
        )
        if isinstance(sel.get("context_version"), int) and sel["context_version"] > 0:
            context_version = sel["context_version"]

        # 5) Delivery
        delivery_date = (
            date.today() + timedelta(days=args.delivery_offset_days)
        ).isoformat()
        deliv = step(
            "delivery",
            "POST",
            "/api/v1/delivery",
            body={
                "delivery": {
                    "timing": {"date": delivery_date, "window": args.delivery_window},
                    "destination_reference": SESSION_DESTINATION_REFERENCE,
                },
                "observed_context_version": context_version,
            },
            csrf=True,
            expect={202},
        )
        if isinstance(deliv.get("context_version"), int) and deliv["context_version"] > 0:
            context_version = deliv["context_version"]

        # 6) Workspace after delivery — authoritative order_summary.total
        after_delivery = step(
            "workspace_after_delivery",
            "GET",
            "/api/v1/workspace",
            expect={200},
        )
        summary_total = order_summary_total(after_delivery)
        if summary_total is None:
            raise RuntimeError(
                "parity drift: facets.order_summary.total missing after delivery"
            )
        if (
            report.product_price is not None
            and abs(summary_total - report.product_price) < 0.001
        ):
            raise RuntimeError(
                f"parity drift: order_summary.total={summary_total} equals product-only "
                f"price (expected +{REFERENCE_DELIVERY_FEE} delivery fee shape)"
            )

        # 7) Order
        order = step(
            "order",
            "POST",
            "/api/v1/order",
            body={},
            csrf=True,
            expect={202},
        )
        if isinstance(order.get("order_id"), str):
            report.order_id = order["order_id"]

        # 8) Workspace after order (prefer latest total)
        after_order = step(
            "workspace_after_order",
            "GET",
            "/api/v1/workspace",
            expect={200},
        )
        observed = order_summary_total(after_order) or summary_total
        report.observed_total = observed

        # 9) Checkout with observed_total from order_summary (web confirmAndPay)
        checkout = step(
            "checkout",
            "POST",
            "/api/v1/checkout",
            body={
                "payment_reference": SESSION_PAYMENT_REFERENCE,
                "observed_total": observed,
            },
            csrf=True,
            expect={202},
        )
        if isinstance(checkout.get("order_id"), str):
            report.order_id = checkout["order_id"]
        report.checkout_status = (
            str(checkout.get("status"))
            if checkout.get("status") is not None
            else ("confirmed" if checkout.get("confirmed") else "accepted")
        )
        if checkout.get("accepted") is not True and checkout.get("confirmed") is not True:
            # 202 with code accepted is the live Path B shape; require accepted.
            if checkout.get("code") != "accepted":
                raise RuntimeError(
                    f"checkout not accepted: status={checkout.get('status')} "
                    f"code={checkout.get('code')} decline={checkout.get('decline_code')}"
                )

        report.result = "pass"
        report.notes.append(
            f"observed_total={observed} (product={report.product_price} "
            f"+ fee shape includes delivery; REFERENCE_DELIVERY_FEE={REFERENCE_DELIVERY_FEE})"
        )
        report.notes.append(
            "checkout submitted on BFF path — does NOT prove website/operator write-through"
        )
    except Exception as exc:
        report.result = "fail"
        report.notes.append(str(exc))
        _log(f"ERROR: {exc}")
    finally:
        report.finished_at = datetime.now(timezone.utc).isoformat()

    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    env_base = os.environ.get("AEA_BFF_BASE_URL") or os.environ.get(
        "AEA_EDGE_BASE_URL", DEFAULT_BASE_URL
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=env_base,
        help=f"BFF origin (default {DEFAULT_BASE_URL} or AEA_BFF_BASE_URL)",
    )
    parser.add_argument(
        "--bearer",
        default=os.environ.get("AEA_BFF_BEARER", PUBLIC_BROWSER_BEARER),
        help="Public browser Bearer (default local-browser-token)",
    )
    parser.add_argument(
        "--client",
        default=os.environ.get("AEA_BFF_CLIENT", CLIENT_HEADER_VALUE),
        help="X-AEA-Client value (default companion-android)",
    )
    parser.add_argument(
        "--message",
        default=os.environ.get(
            "AEA_PARITY_PROBE_MESSAGE",
            "I need flowers for Mom's birthday, roses, around $70",
        ),
        help="Need-stage conversation message_text",
    )
    parser.add_argument(
        "--card-message",
        default="Happy Birthday Mom! (#369 parity probe)",
        help="Optional card_message on selection options",
    )
    parser.add_argument("--delivery-window", default="afternoon")
    parser.add_argument("--delivery-offset-days", type=int, default=1)
    parser.add_argument("--poll-attempts", type=int, default=20)
    parser.add_argument("--poll-interval", type=float, default=1.5)
    parser.add_argument("--timeout", type=float, default=45.0)
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Skip TLS verify (localhost / lab only)",
    )
    parser.add_argument(
        "--skip-weekends",
        action="store_true",
        default=os.environ.get("AEA_PARITY_PROBE_SKIP_WEEKENDS", "").strip().lower()
        in {"1", "true", "yes"},
        help="Exit 0 on Sat/Sun UTC (for schedules that fire daily)",
    )
    parser.add_argument(
        "--json-out",
        default=os.environ.get("AEA_PARITY_PROBE_JSON_OUT", ""),
        help="Optional path to write machine-readable report JSON",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _log("=== companion BFF parity probe (#369) ===")
    _log(f"base_url={args.base_url} client={args.client}")
    _log("honesty: probe ≠ Play gate; T-09 ≠ orders; ≠ #360 dual-probe write-through")

    report = run_probe(args)
    payload = report.to_dict()
    _log("--- report ---")
    _log(json.dumps(payload, indent=2, sort_keys=True))
    if args.json_out:
        out_path = args.json_out
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
        _log(f"wrote {out_path}")

    if report.result == "pass":
        _log(
            f"PASS observed_total={report.observed_total} order_id={report.order_id} "
            f"corrs={report.correlation_ids}"
        )
        return 0
    if report.result == "skip":
        _log("SKIP")
        return 0
    _log(
        "FAIL — do not auto-open issues from CI; if confirmed drift, open ONE finding "
        "issue (comment on #360 only when dual-probe related) and one MR."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
