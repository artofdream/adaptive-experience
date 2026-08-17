#!/usr/bin/env python3
"""Returning-shopper (recall → reorder) walk for GitLab #195.

Path A Compose (https://localhost:8443/) is the full script. Path B
(https://aea.artof.link/) xfails T-03 Select when availability is unknown.
Does not implement recall, seed inventory, or open /florist.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

PATH_A_URL = "https://localhost:8443/"
PATH_B_URL = "https://aea.artof.link/"
REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO / "research" / "assessments" / "2026-08-17-returning-shopper-walk.json"
DEFAULT_SHOTS = REPO / "research" / "assessments" / "_walk_shots_returning"


def is_path_b(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == "aea.artof.link" or host.endswith(".artof.link")


def classify_select(
    *, path_b: bool, enabled_selects: int, card_texts: list[str]
) -> tuple[str, str]:
    """Classify T-03 Select. Path B unknown availability is xfail, not fail."""
    unknown = any("Unknown" in text for text in card_texts)
    available = any("Available" in text for text in card_texts)
    if enabled_selects > 0:
        return "pass", "at least one Select enabled"
    if path_b and (unknown or not available):
        return (
            "xfail",
            "Path B Select disabled with unknown availability; skip later tiles; do not invent a warehouse seeder",
        )
    return (
        "fail",
        "no enabled Select on Path A Compose (inventory seeder expected)",
    )


def classify_same_session_hint(
    *, payment_included: bool, hint_visible: bool
) -> tuple[str, str]:
    if not payment_included:
        return (
            "blocked",
            "same-session hint needs an accepted order; payment excluded this run",
        )
    if hint_visible:
        return "pass", "Ordered earlier in this session visible on T-03"
    return "fail", "accepted order in this session but T-03 prior-order hint missing"


def classify_durable_recall(*, recalled: bool, issue_193_open: bool = True) -> tuple[str, str]:
    if recalled:
        return "pass", "prior order visible in a new browser without login"
    if issue_193_open:
        return (
            "blocked",
            "durable prior-order recall is not implemented until #193",
        )
    return "fail", "durable recall expected after #193 but not visible"


def classify_reorder(*, recall_result: str, reordered: bool) -> tuple[str, str]:
    if recall_result in {"blocked", "xfail"}:
        return "blocked", "reorder not attempted; recall not available"
    if reordered:
        return "pass", "selected recalled product and confirmed destination reference"
    return "fail", "recall visible but reorder did not complete"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.environ.get("AEA_JOURNEY_URL", PATH_A_URL),
        help="Customer workspace origin (default Path A Compose)",
    )
    payment_env = os.environ.get("AEA_JOURNEY_PAYMENT", "").strip() in {"1", "true", "yes"}
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--payment",
        action="store_true",
        default=payment_env,
        help="Include T-07 session payment reference (needed for same-session hint)",
    )
    group.add_argument(
        "--skip-payment",
        action="store_true",
        help="Stop before Place Order (skill default)",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--shots", type=Path, default=DEFAULT_SHOTS)
    return parser.parse_args(argv)


def _step(report: dict, tile: str, expected: str, actual: str, result: str) -> None:
    report["steps"].append(
        {"tile": tile, "expected": expected, "actual": actual, "result": result}
    )


def _launch_browser(playwright, *, ignore_certs: bool):
    args = ["--host-resolver-rules=MAP localhost 127.0.0.1"]
    if ignore_certs:
        args.append("--ignore-certificate-errors")
    launch_kwargs = dict(headless=True, args=args)
    notes = []
    for channel in ("msedge", "chrome", None):
        try:
            kwargs = dict(launch_kwargs)
            if channel:
                kwargs["channel"] = channel
            browser = playwright.chromium.launch(**kwargs)
            label = f"playwright channel={channel}" if channel else "playwright chromium"
            return browser, label, notes
        except Exception as exc:
            notes.append(f"{channel or 'chromium'} failed: {exc}")
    raise RuntimeError("could not launch a Chromium-family browser: " + "; ".join(notes))


def _dump_js() -> str:
    return """() => {
      const list = document.querySelector('#understanding-list');
      const err = document.querySelector('#message-form-error');
      const notice = document.querySelector('#notice');
      const cards = [...document.querySelectorAll('#recommendation-cards .card')].map(
        (c) => c.innerText.replace(/\\n/g, ' | ')
      );
      const selects = [...document.querySelectorAll('#recommendation-cards button.primary')].map(
        (b) => ({ text: b.textContent, disabled: b.disabled })
      );
      return {
        understanding: document.querySelector('#understanding')?.innerText || '',
        listHidden: list ? list.hidden : null,
        formError: err && !err.hidden ? err.innerText : '',
        notice: notice && !notice.hidden ? notice.innerText : '',
        chips: [...document.querySelectorAll('#suggestions button')].map((b) => b.textContent),
        cards,
        selects,
        hints: [...document.querySelectorAll('#recommendation-cards .hint')].map((h) => h.textContent),
        sessionPayRef: document.querySelector('#session-payment-ref')?.innerText || '',
        confirmDestination: document.querySelector('#confirm-destination')?.innerText || '',
        checkoutError: document.querySelector('#checkout-form-error:not([hidden])')?.innerText || '',
        orderStatus: document.querySelector('#order-status')?.innerText || '',
        floristPath: location.pathname,
      };
    }"""


def run_walk(args: argparse.Namespace) -> dict:
    from playwright.sync_api import sync_playwright

    url = args.url if args.url.endswith("/") else args.url + "/"
    path_b = is_path_b(url)
    payment_included = bool(args.payment) and not args.skip_payment
    shots: Path = args.shots
    shots.mkdir(parents=True, exist_ok=True)
    delivery_date = (date.today() + timedelta(days=7)).isoformat()

    report: dict = {
        "url": url,
        "path": "B" if path_b else "A",
        "scenario": "returning-shopper",
        "payment_included": payment_included,
        "issue": "#195",
        "related": ["#27", "#190", "#193"],
        "nfr_007_012_proof": False,
        "steps": [],
        "api": {"suggestions": [], "csrf_rejected": False, "posts": [], "errors": []},
        "notes": [],
        "florist_opened": False,
    }

    def on_response(response, origin_marker: str) -> None:
        resp_url = response.url
        if "/api/" not in resp_url:
            return
        rec = {
            "url": resp_url.split(origin_marker)[-1] if origin_marker in resp_url else resp_url,
            "status": response.status,
            "method": response.request.method,
        }
        try:
            body = response.json()
        except Exception:
            body = None
        rec["error"] = None
        if isinstance(body, dict):
            rec["error"] = body.get("error")
            rec["code"] = body.get("code")
            rec["accepted"] = body.get("accepted")
            rec["order_id"] = body.get("order_id")
            rec["confirmed"] = body.get("confirmed")
            rec["order_status"] = body.get("status")
            if rec["error"] == "csrf_rejected" or rec["code"] == "csrf_rejected":
                report["api"]["csrf_rejected"] = True
            if rec["error"] and rec["error"] not in {"accepted"}:
                report["api"]["errors"].append(
                    {"url": rec["url"], "status": rec["status"], "error": rec["error"]}
                )
            if "suggestions" in body:
                report["api"]["suggestions"].append(body.get("suggestions"))
            if "facets" in body:
                recs = (body.get("facets") or {}).get("recommendations") or {}
                items = recs.get("items") if isinstance(recs, dict) else recs
                hints = [
                    item.get("product_id")
                    for item in (items or [])
                    if isinstance(item, dict) and item.get("prior_order_hint")
                ]
                report["api"]["last_workspace"] = {
                    "context_version": body.get("context_version"),
                    "rec_count": len(items or []),
                    "prior_order_hints": hints,
                    "order": (body.get("facets") or {}).get("order"),
                }
        if response.request.method in ("POST", "PATCH", "PUT"):
            report["api"]["posts"].append(rec)

    origin_marker = urlparse(url).netloc

    with sync_playwright() as playwright:
        browser, browser_label, launch_notes = _launch_browser(
            playwright, ignore_certs=not path_b
        )
        report["browser"] = browser_label
        report["notes"].extend(launch_notes)
        context = browser.new_context(
            ignore_https_errors=not path_b, viewport={"width": 1440, "height": 1100}
        )
        page = context.new_page()
        page.on("response", lambda response: on_response(response, origin_marker))

        def dump() -> dict:
            return page.evaluate(_dump_js())

        def send_and_wait(text: str, timeout_ms: int = 20000) -> dict:
            page.fill("#message", text)
            page.click("button.send")
            try:
                page.wait_for_function(
                    """() => {
                      const list = document.querySelector('#understanding-list');
                      const err = document.querySelector('#message-form-error');
                      if (err && !err.hidden && err.textContent.trim()) return 'error';
                      if (list && !list.hidden && list.children.length) return 'intent';
                      const notice = document.querySelector('#notice');
                      if (notice && !notice.hidden && /Thanks/.test(notice.textContent || '')) return 'sent';
                      return false;
                    }""",
                    timeout=timeout_ms,
                )
            except Exception:
                pass
            page.wait_for_timeout(1200)
            return dump()

        def goto_step(step_id: str) -> None:
            nav = page.locator(f"#journey-steps button[data-step='{step_id}']")
            if nav.count() and nav.first.is_visible() and nav.first.is_enabled():
                nav.first.click()
                page.wait_for_timeout(1200)
                return
            candidates = page.locator(f"button[data-goto-step='{step_id}']")
            for index in range(candidates.count()):
                button = candidates.nth(index)
                if button.is_visible() and button.is_enabled():
                    button.click()
                    page.wait_for_timeout(1200)
                    return
            report["notes"].append(f"no visible control for journey step {step_id}")

        try:
            page.goto(url, wait_until="domcontentloaded")
            if not path_b:
                page.reload(wait_until="networkidle")
            page.wait_for_selector("#message-form", timeout=20000)
            page.wait_for_timeout(2000)
            if page.evaluate("() => location.pathname") == "/florist":
                report["florist_opened"] = True
                report["notes"].append("refusing: landed on /florist")
                _step(
                    report,
                    "T-01 Enter / Discovery",
                    "Customer workspace / only",
                    "Landed on /florist",
                    "fail",
                )
                return report

            page.screenshot(path=str(shots / "01-landing.png"), full_page=True)
            assistant = page.locator("#messages").inner_text()
            _step(
                report,
                "T-01 Enter / Discovery",
                "Welcome + composer; no login; customer can type freely",
                f"Assistant: {assistant.strip()[:160]!r}. Composer visible.",
                "pass" if page.locator("#message").is_visible() else "fail",
            )

            after_partial = send_and_wait("I need flowers...", timeout_ms=12000)
            page.screenshot(path=str(shots / "02-partial-thought.png"), full_page=True)
            chips = after_partial.get("chips") or []
            _step(
                report,
                "T-01 thought completion",
                "Partial thought; chips optional; typing always allowed",
                f"Notice: {after_partial.get('notice')!r}. Chips: {chips}.",
                "pass" if page.locator("#message").is_visible() else "fail",
            )

            after_full = send_and_wait("Birthday flowers for Mum, under $75")
            intent_text = page.locator("#understanding").inner_text()
            page.screenshot(path=str(shots / "03-intent.png"), full_page=True)
            intent_ok = any(
                token in intent_text.lower() for token in ("birthday", "mother", "mum", "75")
            )
            _step(
                report,
                "T-01 Send + T-02 Shared Understanding",
                "Occasion / recipient / budget appear; Review and correct exists",
                f"Intent: {intent_text[:400]!r}. Review: {page.locator('#correct-open').is_visible()}. csrf={report['api']['csrf_rejected']}. dump={after_full.get('formError')!r}",
                "fail"
                if report["api"]["csrf_rejected"]
                else ("pass" if intent_ok else "fail"),
            )

            goto_step("3")
            page.wait_for_timeout(1500)
            cards = page.locator("#recommendation-cards .card")
            card_copy = [
                cards.nth(i).inner_text().replace("\n", " | ") for i in range(cards.count())
            ]
            page.screenshot(path=str(shots / "04-recommendations.png"), full_page=True)
            select_btns = page.locator(
                "#recommendation-cards button.primary:not([disabled])"
            )
            select_result, select_reason = classify_select(
                path_b=path_b,
                enabled_selects=select_btns.count(),
                card_texts=card_copy,
            )
            _step(
                report,
                "T-03 Curated Recommendations",
                "Validated options; Path A Available+Select; Path B unknown Select is xfail",
                f"Cards ({len(card_copy)}): {card_copy}. {select_reason}",
                "pass"
                if select_result == "pass" and card_copy
                else ("xfail" if select_result == "xfail" else "fail"),
            )

            if select_result != "pass":
                for tile, expected in (
                    (
                        "T-04 Select + customize",
                        "Select an available arrangement; size; card message",
                    ),
                    (
                        "T-05 Delivery",
                        "Date + window; confirm saved destination reference",
                    ),
                    ("T-06 Order Summary", "Itemized charges"),
                    (
                        "T-07 Checkout",
                        "Session payment reference; skip unless --payment",
                    ),
                    (
                        "M8 same-session recall",
                        "Ordered earlier in this session on T-03 after accepted order",
                    ),
                ):
                    _step(report, tile, expected, select_reason, "blocked")
            else:
                select_btns.first.click()
                page.wait_for_timeout(2000)
                page.fill("#size", "Standard")
                if page.locator("#colour").count():
                    page.select_option("#colour", "pink")
                if page.locator("#ribbon").count():
                    page.select_option("#ribbon", "satin")
                page.fill("#card-message", "Happy Birthday Mum — love you")
                page.click("#selection-form button[type='submit']")
                page.wait_for_timeout(2000)
                page.screenshot(path=str(shots / "05-customize.png"), full_page=True)
                _step(
                    report,
                    "T-04 Select + customize",
                    "Select arrangement; size; physical card message; optional colour/ribbon",
                    f"Arrangement={page.locator('#arrangement').input_value()!r}",
                    "pass" if page.locator("#arrangement").input_value() else "fail",
                )

                goto_step("5")
                page.fill("#delivery-date", delivery_date)
                page.check("input[name='window'][value='morning']")
                dest_mode = page.locator(
                    "input[name='destination-mode'][value='session']"
                )
                if dest_mode.count():
                    dest_mode.check()
                dest_ref = page.locator("#session-destination-ref").inner_text()
                street = page.locator(
                    "input[autocomplete='street-address'], input[name='address']"
                )
                page.click("#delivery-form button[type='submit']")
                page.wait_for_timeout(2500)
                banner = page.locator("#delivery-confirmed")
                banner_text = banner.inner_text() if banner.is_visible() else ""
                err = (
                    page.locator("#delivery-form-error").inner_text()
                    if page.locator("#delivery-form-error").is_visible()
                    else ""
                )
                page.screenshot(path=str(shots / "06-delivery.png"), full_page=True)
                _step(
                    report,
                    "T-05 Delivery",
                    "Date + named window; confirm saved destination reference (not a street address)",
                    f"Date {delivery_date}, dest {dest_ref!r}, street_fields={street.count()}, banner={banner_text!r} error={err!r}",
                    "fail"
                    if street.count()
                    or report["api"]["csrf_rejected"]
                    or (not banner_text and err)
                    else "pass",
                )

                goto_step("6")
                summary = (
                    page.locator("#order-summary").inner_text()
                    if page.locator("#order-summary").is_visible()
                    else ""
                )
                page.screenshot(path=str(shots / "07-summary.png"), full_page=True)
                _step(
                    report,
                    "T-06 Order Summary",
                    "Itemized charges update after selection and delivery",
                    f"Summary: {summary[:500]!r}",
                    "pass" if ("Total" in summary or "total" in summary.lower()) else "fail",
                )

                if not payment_included:
                    _step(
                        report,
                        "T-07 Checkout",
                        "Stop before payment unless --payment",
                        "Payment not included. Did not Create order.",
                        "blocked",
                    )
                    hint_result, hint_reason = classify_same_session_hint(
                        payment_included=False, hint_visible=False
                    )
                    _step(
                        report,
                        "M8 same-session recall",
                        "Ordered earlier in this session on T-03 after accepted order",
                        hint_reason,
                        hint_result,
                    )
                else:
                    session_mode = page.locator(
                        "input[name='payment-mode'][value='session']"
                    )
                    if session_mode.count():
                        session_mode.check()
                    page.check("#checkout-ack")
                    page.screenshot(
                        path=str(shots / "08-checkout-before.png"), full_page=True
                    )
                    with page.expect_response(
                        lambda response: "/api/v1/checkout" in response.url
                        and response.request.method == "POST",
                        timeout=30000,
                    ) as checkout_wait:
                        page.click("#create-order")
                    checkout_resp = checkout_wait.value
                    try:
                        checkout_body = checkout_resp.json()
                    except Exception:
                        checkout_body = None
                    page.wait_for_timeout(3000)
                    page.screenshot(
                        path=str(shots / "09-checkout-after.png"), full_page=True
                    )
                    pay_ok = checkout_resp.status == 202 and (
                        isinstance(checkout_body, dict)
                        and (
                            checkout_body.get("accepted")
                            or checkout_body.get("order_id")
                            or checkout_body.get("confirmed")
                        )
                    )
                    _step(
                        report,
                        "T-07 Checkout",
                        "Confirm session payment reference; ack; Create order. No PAN fields.",
                        f"status={checkout_resp.status} body={checkout_body}",
                        "pass" if pay_ok else "fail",
                    )

                    goto_step("3")
                    page.wait_for_timeout(2000)
                    page.screenshot(
                        path=str(shots / "10-same-session-t03.png"), full_page=True
                    )
                    hinted = page.locator(
                        "#recommendation-cards .hint",
                        has_text="Ordered earlier in this session",
                    )
                    hint_result, hint_reason = classify_same_session_hint(
                        payment_included=True, hint_visible=hinted.count() > 0
                    )
                    _step(
                        report,
                        "M8 same-session recall",
                        "Ordered earlier in this session on T-03 after accepted order",
                        f"{hint_reason}. cards={dump().get('cards')}",
                        hint_result,
                    )

                    reordered = False
                    if hint_result == "pass":
                        hinted_card = page.locator("#recommendation-cards .card").filter(
                            has=page.locator(
                                ".hint", has_text="Ordered earlier in this session"
                            )
                        )
                        hinted_select = hinted_card.locator(
                            "button.primary:not([disabled])"
                        )
                        if hinted_select.count():
                            hinted_select.first.click()
                            page.wait_for_timeout(1500)
                            goto_step("5")
                            dest_mode = page.locator(
                                "input[name='destination-mode'][value='session']"
                            )
                            if dest_mode.count():
                                dest_mode.check()
                            dest_ref = page.locator(
                                "#session-destination-ref"
                            ).inner_text()
                            page.click("#delivery-form button[type='submit']")
                            page.wait_for_timeout(2000)
                            banner = page.locator("#delivery-confirmed")
                            reordered = banner.is_visible() and dest_ref.strip() != ""
                            page.screenshot(
                                path=str(shots / "11-reorder-delivery.png"),
                                full_page=True,
                            )
                    reorder_result, reorder_reason = classify_reorder(
                        recall_result=hint_result, reordered=reordered
                    )
                    _step(
                        report,
                        "M8 reorder",
                        "Select recalled product; confirm destination reference (ADR-013)",
                        reorder_reason,
                        reorder_result,
                    )

            page.click("button.help-button")
            page.wait_for_timeout(400)
            help_copy = page.locator("#help").inner_text()
            page.fill("#support-question", "When will delivery arrive?")
            page.click("#support-form button[type='submit']")
            page.wait_for_timeout(1500)
            answer = (
                page.locator("#support-answer").inner_text()
                if page.locator("#support-answer").is_visible()
                else ""
            )
            page.screenshot(path=str(shots / "12-help.png"), full_page=True)
            not_a_person = "not a person" in help_copy.lower() or "Automated" in help_copy
            _step(
                report,
                "ASO Help",
                "Help available without leaving the workspace; labeled as not a person",
                f"Help: {help_copy[:240]!r}. Answer: {answer[:200]!r}",
                "pass" if not_a_person else "fail",
            )
            if page.locator("[data-close-help]").count():
                page.click("[data-close-help]")
            page.screenshot(path=str(shots / "13-final.png"), full_page=True)

            recalled = False
            recall_note = ""
            fresh = None
            try:
                fresh = browser.new_context(
                    ignore_https_errors=not path_b,
                    viewport={"width": 1440, "height": 1100},
                )
                fresh_page = fresh.new_page()
                last_error = None
                for _attempt in range(3):
                    try:
                        fresh_page.goto(url, wait_until="domcontentloaded")
                        last_error = None
                        break
                    except Exception as exc:
                        last_error = exc
                        fresh_page.wait_for_timeout(1500)
                if last_error is not None:
                    raise last_error
                fresh_page.wait_for_selector("#message-form", timeout=20000)
                fresh_page.wait_for_timeout(1500)
                body_text = (fresh_page.inner_text("body") or "").lower()
                recalled = (
                    fresh_page.locator(
                        "#recommendation-cards .hint",
                        has_text="Ordered earlier in this session",
                    ).count()
                    > 0
                    or "reorder" in body_text
                    or "ordered earlier" in body_text
                )
            except Exception as exc:
                recall_note = f" new-browser navigation: {type(exc).__name__}: {exc}"
                report["notes"].append(recall_note.strip())
            finally:
                if fresh is not None:
                    try:
                        fresh.close()
                    except Exception:
                        pass
            recall_result, recall_reason = classify_durable_recall(recalled=recalled)
            _step(
                report,
                "M8 durable recall",
                "Prior order offered in a new browser without login (#193)",
                recall_reason + recall_note,
                recall_result,
            )
            if "M8 reorder" not in {row["tile"] for row in report["steps"]}:
                reorder_result, reorder_reason = classify_reorder(
                    recall_result=recall_result, reordered=False
                )
                _step(
                    report,
                    "M8 reorder",
                    "Select recalled product; confirm destination reference (ADR-013)",
                    reorder_reason,
                    reorder_result,
                )
        except Exception as exc:
            report["crash"] = f"{type(exc).__name__}: {exc}"
            try:
                page.screenshot(path=str(shots / "crash.png"), full_page=True)
            except Exception:
                pass
        finally:
            try:
                browser.close()
            except Exception:
                pass

    return report


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        report = run_walk(args)
    except ModuleNotFoundError as exc:
        if "playwright" in str(exc):
            print(
                "Playwright is not installed. pip install playwright && playwright install chromium",
                file=sys.stderr,
            )
            return 2
        raise
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    results = [row["result"] for row in report.get("steps", [])]
    print(
        json.dumps(
            {
                "wrote": str(args.out),
                "url": report.get("url"),
                "path": report.get("path"),
                "payment_included": report.get("payment_included"),
                "results": results,
                "csrf": report.get("api", {}).get("csrf_rejected"),
                "crash": report.get("crash"),
                "florist_opened": report.get("florist_opened"),
            },
            indent=2,
        )
    )
    if report.get("crash") or report.get("florist_opened"):
        return 1
    if any(result == "fail" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
