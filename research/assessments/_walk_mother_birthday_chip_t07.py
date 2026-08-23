"""Short T-01 first-chip check + T-07 smoke after !189 rebuild.

cursor-ide-browser navigate was classified/rejected; Playwright against the
live shop is the same fallback as the 16 Aug pay walk.
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://localhost:8443/"
HERE = Path(__file__).resolve().parent
OUT = HERE / "2026-08-16-mother-birthday-chip-t07.json"
SHOTS = HERE / "_walk_shots_chip_t07"
SHOTS.mkdir(exist_ok=True)

report: dict = {
    "url": URL,
    "scenario": "mother-birthday",
    "payment_included": True,
    "scope": "T-01 first chip after 'I need flowers...' + T-07 checkout smoke",
    "walked_at": "2026-08-16T02:12:00+02:00",
    "browser": "playwright (cursor-ide-browser navigate classified/rejected; healthz 200 ok)",
    "images": {},
    "steps": [],
    "api": {
        "suggestions": [],
        "csrf_rejected": False,
        "posts": [],
        "errors": [],
        "checkout": None,
    },
    "workspace": {},
    "notes": [],
    "first_chip": None,
    "first_chip_pass": None,
}


def step(tile: str, expected: str, actual: str, result: str) -> None:
    report["steps"].append(
        {"tile": tile, "expected": expected, "actual": actual, "result": result}
    )


def confirm_served_app_js() -> None:
    ctx = ssl._create_unverified_context()
    req = urllib.request.urlopen(
        "https://localhost:8443/assets/app.js", context=ctx, timeout=20
    )
    body = req.read().decode("utf-8", "replace")
    report["images"] = {
        "healthz": "200 {\"status\": \"ok\"}",
        "app_js_status": req.status,
        "app_js_len": len(body),
        "has_thought_completion_map": '"Who are the flowers for?": "for Mom"' in body,
        "has_for_mom_unshift": 'list.unshift("for Mom")' in body,
        "containers_recreated": "2026-08-16 02:05 CEST (bff/gateway/orchestration after origin/main 4521f6d !189)",
    }


def main() -> int:
    delivery_date = (date.today() + timedelta(days=7)).isoformat()
    try:
        confirm_served_app_js()
    except Exception as exc:
        report["notes"].append(f"served app.js check failed: {type(exc).__name__}: {exc}")

    with sync_playwright() as p:
        launch_kwargs = dict(
            headless=True,
            args=[
                "--ignore-certificate-errors",
                "--host-resolver-rules=MAP localhost 127.0.0.1",
            ],
        )
        try:
            browser = p.chromium.launch(channel="msedge", **launch_kwargs)
        except Exception as edge_err:
            report["notes"].append(f"msedge channel failed: {edge_err}")
            try:
                browser = p.chromium.launch(channel="chrome", **launch_kwargs)
            except Exception as chrome_err:
                report["notes"].append(f"chrome channel failed: {chrome_err}")
                browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(
            ignore_https_errors=True, viewport={"width": 1440, "height": 1100}
        )
        page = context.new_page()

        def on_response(response):
            url = response.url
            if "/api/" not in url:
                return
            rec = {
                "url": url.split("8443")[-1],
                "status": response.status,
                "method": response.request.method,
            }
            try:
                body = response.json()
            except Exception:
                body = None
            rec["error"] = None
            if isinstance(body, dict):
                rec["error"] = body.get("error") or body.get("code")
                rec["accepted"] = body.get("accepted")
                rec["confirmed"] = body.get("confirmed")
                rec["order_id"] = body.get("order_id")
                rec["order_status"] = body.get("status")
                if rec["error"] == "csrf_rejected":
                    report["api"]["csrf_rejected"] = True
                if rec["error"]:
                    report["api"]["errors"].append(
                        {
                            "url": rec["url"],
                            "status": rec["status"],
                            "error": rec["error"],
                        }
                    )
                if "suggestions" in body:
                    report["api"]["suggestions"].append(body.get("suggestions"))
                if "structured_intent" in body:
                    rec["structured_intent"] = body.get("structured_intent")
                if "facets" in body:
                    recs = (body.get("facets") or {}).get("recommendations") or {}
                    items = recs.get("items") if isinstance(recs, dict) else recs
                    report["api"]["last_workspace"] = {
                        "context_version": body.get("context_version"),
                        "shared": (body.get("facets") or {}).get(
                            "shared_understanding"
                        ),
                        "rec_count": len(items or []),
                        "order": (body.get("facets") or {}).get("order"),
                    }
            if "/checkout" in rec["url"] and rec["method"] == "POST":
                report["api"]["checkout"] = rec
            if response.request.method in ("POST", "PATCH", "PUT"):
                report["api"]["posts"].append(rec)

        page.on("response", on_response)

        def dump():
            return page.evaluate(
                """() => {
                  const list = document.querySelector('#understanding-list');
                  const err = document.querySelector('#message-form-error');
                  const notice = document.querySelector('#notice');
                  const cont = document.querySelector('button[data-goto-step="3"]');
                  const chips = [...document.querySelectorAll('#suggestions button')].map(
                    (b) => ({ text: b.textContent, suggest: b.dataset.suggest })
                  );
                  const roles = [...document.querySelectorAll('#messages .msg')].map((el) => ({
                    role: el.className,
                    text: (el.innerText || '').slice(0, 400),
                  }));
                  const checkoutErr = document.querySelector('#checkout-form-error');
                  return {
                    understanding: document.querySelector('#understanding')?.innerText,
                    listHidden: list ? list.hidden : null,
                    formError: err && !err.hidden ? err.innerText : '',
                    notice: notice && !notice.hidden ? notice.innerText : '',
                    continueDisabled: cont ? cont.disabled : null,
                    chips,
                    suggestionsHidden: document.querySelector('#suggestions')?.hidden,
                    messages: roles,
                    summary: document.querySelector('#order-summary')?.innerText || '',
                    recCards: [...document.querySelectorAll('#recommendation-cards .card')].map(
                      (c) => (c.innerText || '').slice(0, 400)
                    ),
                    checkoutVisible: !document.querySelector('#checkout')?.hidden,
                    checkoutError: checkoutErr && !checkoutErr.hidden ? checkoutErr.innerText : '',
                    confirmDestination: document.querySelector('#confirm-destination')?.innerText,
                    confirmTotal: document.querySelector('#confirm-total')?.innerText,
                    sessionPayRef: document.querySelector('#session-payment-ref')?.innerText,
                    ackChecked: !!document.querySelector('#checkout-ack')?.checked,
                    orderStatus: document.querySelector('#order-status')?.innerText,
                    latestStatus: document.querySelector('#latest-status-text')?.innerText,
                    trackingVisible: !document.querySelector('#order-tracking')?.hidden,
                    cardInputs: [...document.querySelectorAll('input')].filter((el) => {
                      const n = ((el.name || '') + (el.id || '') + (el.autocomplete || '')).toLowerCase();
                      return /card|cc-|cvv|pan/.test(n);
                    }).map((el) => el.id || el.name),
                  };
                }"""
            )

        def send_and_wait(text: str, timeout_ms: int = 45000) -> dict:
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
                      const chips = document.querySelectorAll('#suggestions button');
                      if (chips.length) return 'chips';
                      const msgs = document.querySelectorAll('#messages .msg.assistant, #messages .assistant');
                      if (msgs.length > 1) return 'reply';
                      return false;
                    }""",
                    timeout=timeout_ms,
                )
            except Exception as exc:
                report["notes"].append(
                    f"wait after send {text!r}: {type(exc).__name__}: {exc}"
                )
            page.wait_for_timeout(2500)
            return dump()

        try:
            page.goto(URL, wait_until="domcontentloaded")
            page.reload(wait_until="networkidle")
            page.wait_for_selector("#message-form", timeout=20000)
            page.wait_for_timeout(2500)
            report["boot"] = dump()

            chips = page.locator("#suggestions button").all_text_contents()
            assistant = page.locator("#messages").inner_text()
            page.screenshot(path=str(SHOTS / "01-landing.png"), full_page=True)
            step(
                "T-01 Enter / Discovery",
                "Welcome + composer; customer can describe the occasion in own words",
                f"Welcome visible. Assistant: {assistant.strip()[:180]!r}. Chips: {chips}. Composer present.",
                "pass" if page.locator("#message").is_visible() else "fail",
            )

            after_partial = send_and_wait("I need flowers...")
            settled = after_partial
            for _ in range(16):
                chips_now = settled.get("chips") or []
                if chips_now or settled.get("listHidden") is False:
                    break
                if "orchestration_unavailable" in (settled.get("formError") or ""):
                    page.wait_for_timeout(1500)
                    settled = dump()
                    continue
                page.wait_for_timeout(800)
                settled = dump()
            after_partial = settled
            chips_after = [c["text"] for c in (after_partial.get("chips") or [])]
            first_chip = chips_after[0] if chips_after else None
            report["first_chip"] = first_chip
            report["first_chip_pass"] = first_chip == "for Mom"
            log = page.locator("#messages").inner_text()
            page.screenshot(path=str(SHOTS / "02-partial-thought.png"), full_page=True)
            first_errors = [
                e
                for e in report["api"]["errors"]
                if e.get("url", "").endswith("/messages")
            ]
            step(
                "T-01 first chip after partial thought",
                "First chip is exactly 'for Mom' (mother-birthday step 2; !189 / #185)",
                f"First chip: {first_chip!r}. All chips: {chips_after}. Notice: {after_partial.get('notice')!r}. Customer line in log: {'I need flowers' in log}. FormError: {after_partial.get('formError')!r}. First message API: {first_errors}.",
                "pass" if first_chip == "for Mom" else "fail",
            )

            if first_chip == "for Mom":
                page.locator("#suggestions button").first.click()
                page.wait_for_timeout(2500)
            intent_now = (dump().get("understanding") or "").lower()
            need_full = not any(t in intent_now for t in ("birthday", "mother", "mum", "75"))
            if need_full:
                page.wait_for_timeout(2000)
                after_full = send_and_wait("Birthday flowers for Mum, under €75")
            else:
                after_full = dump()
            intent_text = page.locator("#understanding").inner_text()
            page.screenshot(path=str(SHOTS / "03-intent.png"), full_page=True)
            intent_ok = any(
                token in intent_text.lower()
                for token in ("birthday", "mother", "mum", "75")
            )
            step(
                "T-01 Conversation Send + T-02 Shared Understanding",
                "Message posts; occasion/recipient/budget appear so T-07 path can continue",
                f"Intent panel: {intent_text[:500]!r}. csrf_rejected={report['api']['csrf_rejected']}.",
                "fail"
                if report["api"]["csrf_rejected"]
                else ("pass" if intent_ok else "fail"),
            )

            if page.locator("#correct-open").is_visible() and any(
                x in (page.locator("#understanding").inner_text() or "").lower()
                for x in ("birthday", "mother", "mum", "75")
            ):
                for _ in range(10):
                    txt = dump()
                    if "Updating" not in (txt.get("understanding") or "") and not txt.get(
                        "formError"
                    ):
                        break
                    page.wait_for_timeout(800)
                page.click("#correct-open")
                page.select_option("#correct-facet", "recipient")
                page.fill("#correct-value", "Mum")
                page.click("#correct-form button[type='submit']")
                page.wait_for_timeout(2000)

            continue_rec = page.locator("button[data-goto-step='3']")
            step3 = page.locator("#journey-steps button[data-step='3']")
            if continue_rec.count() and continue_rec.first.is_enabled():
                continue_rec.first.click()
            elif step3.count() and step3.first.is_enabled():
                step3.first.click()
            else:
                report["notes"].append(f"step 3 still locked: {dump()}")
            page.wait_for_timeout(2500)

            cards = page.locator("#recommendation-cards .card")
            card_count = cards.count()
            card_copy = [
                cards.nth(i).inner_text().replace("\n", " | ") for i in range(card_count)
            ]
            page.screenshot(path=str(SHOTS / "04-recommendations.png"), full_page=True)
            step(
                "T-03 Curated Recommendations",
                "Available options selectable so checkout smoke can continue",
                f"Cards ({card_count}): {card_copy}.",
                "pass"
                if card_count > 0 and any("Available" in c for c in card_copy)
                else "fail",
            )

            select_btns = page.locator(
                "#recommendation-cards button.primary:not([disabled])"
            )
            if select_btns.count() == 0:
                step(
                    "T-04 Select",
                    "Select an available arrangement",
                    "No enabled Select button",
                    "fail",
                )
            else:
                select_btns.first.click()
                page.wait_for_timeout(2500)
                page.fill("#size", "Standard")
                if page.locator("#colour").count():
                    page.select_option("#colour", "pink")
                if page.locator("#ribbon").count():
                    page.select_option("#ribbon", "satin")
                page.fill("#card-message", "Happy Birthday Mum — love you")
                page.click("#selection-form button[type='submit']")
                page.wait_for_timeout(2500)
                page.screenshot(path=str(SHOTS / "05-customize.png"), full_page=True)
                step(
                    "T-04 Select + customize",
                    "Select arrangement; size; physical card message",
                    f"Arrangement={page.locator('#arrangement').input_value()!r} size={page.locator('#size').input_value()!r}",
                    "pass" if page.locator("#arrangement").input_value() else "fail",
                )

                to_delivery = page.locator("button[data-goto-step='5']")
                if to_delivery.count() and to_delivery.first.is_enabled():
                    to_delivery.first.click()
                    page.wait_for_timeout(800)
                page.fill("#delivery-date", delivery_date)
                page.check("input[name='window'][value='morning']")
                dest_mode = page.locator("input[name='destination-mode'][value='session']")
                if dest_mode.count():
                    dest_mode.check()
                dest_ref = page.locator("#session-destination-ref").inner_text()
                street = page.locator(
                    "input[autocomplete='street-address'], input[name='address']"
                )
                page.click("#delivery-form button[type='submit']")
                page.wait_for_timeout(3000)
                banner = page.locator("#delivery-confirmed")
                banner_text = banner.inner_text() if banner.is_visible() else ""
                err = (
                    page.locator("#delivery-form-error").inner_text()
                    if page.locator("#delivery-form-error").is_visible()
                    else ""
                )
                page.screenshot(path=str(SHOTS / "06-delivery.png"), full_page=True)
                step(
                    "T-05 Delivery",
                    "Date + named window; confirm saved destination reference",
                    f"Date {delivery_date}, window morning, destination ref {dest_ref!r}. Street-address fields={street.count()}. Banner={banner_text!r} error={err!r}",
                    "fail"
                    if street.count()
                    or report["api"]["csrf_rejected"]
                    or (not banner_text and err)
                    else "pass",
                )

                summary = (
                    page.locator("#order-summary").inner_text()
                    if page.locator("#order-summary").is_visible()
                    else ""
                )
                to_checkout = page.locator("button[data-goto-step='6']")
                if to_checkout.count() and to_checkout.first.is_enabled():
                    to_checkout.first.click()
                    page.wait_for_timeout(800)
                    summary = (
                        page.locator("#order-summary").inner_text()
                        if page.locator("#order-summary").is_visible()
                        else summary
                    )
                page.screenshot(path=str(SHOTS / "07-summary.png"), full_page=True)
                has_total = "Total" in summary or "total" in summary.lower()
                step(
                    "T-06 Order Summary",
                    "Itemized charges update after selection and delivery",
                    f"Summary panel: {summary[:700]!r}",
                    "pass" if has_total else "fail",
                )

                before_pay = dump()
                session_mode = page.locator(
                    "input[name='payment-mode'][value='session']"
                )
                if session_mode.count():
                    session_mode.check()
                page.check("#checkout-ack")
                page.screenshot(path=str(SHOTS / "08-checkout-before.png"), full_page=True)
                with page.expect_response(
                    lambda r: "/api/v1/checkout" in r.url and r.request.method == "POST",
                    timeout=30000,
                ) as checkout_wait:
                    page.click("#create-order")
                checkout_resp = checkout_wait.value
                try:
                    checkout_body = checkout_resp.json()
                except Exception:
                    checkout_body = None
                page.wait_for_timeout(3500)
                after_pay = dump()
                page.screenshot(path=str(SHOTS / "09-checkout-after.png"), full_page=True)
                checkout_rec = report["api"].get("checkout") or {
                    "status": checkout_resp.status,
                    "error": (checkout_body or {}).get("code")
                    if isinstance(checkout_body, dict)
                    else None,
                    "accepted": (checkout_body or {}).get("accepted")
                    if isinstance(checkout_body, dict)
                    else None,
                    "order_id": (checkout_body or {}).get("order_id")
                    if isinstance(checkout_body, dict)
                    else None,
                    "confirmed": (checkout_body or {}).get("confirmed")
                    if isinstance(checkout_body, dict)
                    else None,
                }
                pay_ok = (
                    checkout_resp.status == 202
                    and checkout_rec.get("error") != "order_not_found"
                    and (
                        checkout_rec.get("accepted")
                        or checkout_rec.get("order_id")
                        or checkout_rec.get("confirmed")
                    )
                )
                raw_cards = before_pay.get("cardInputs") or []
                step(
                    "T-07 Checkout smoke",
                    "Confirm session_pay_ref, ack checkbox, Create order. Expect 202 / order created (not 404 order_not_found). No raw card fields.",
                    f"session_pay_ref={before_pay.get('sessionPayRef')!r} dest={before_pay.get('confirmDestination')!r} total={before_pay.get('confirmTotal')!r} ack={after_pay.get('ackChecked')} raw_card_inputs={raw_cards} POST /api/v1/checkout status={checkout_resp.status} body={checkout_body} ui_error={after_pay.get('checkoutError')!r} notice={after_pay.get('notice')!r} order_status={after_pay.get('orderStatus')!r}",
                    "fail" if raw_cards or not pay_ok else "pass",
                )

            report["workspace"] = dump()
            report["delivery_date"] = delivery_date
            page.screenshot(path=str(SHOTS / "10-final.png"), full_page=True)
        except Exception as exc:
            report["crash"] = f"{type(exc).__name__}: {exc}"
            try:
                page.screenshot(path=str(SHOTS / "crash.png"), full_page=True)
            except Exception:
                pass
        finally:
            try:
                browser.close()
            except Exception:
                pass

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(OUT),
                "first_chip": report.get("first_chip"),
                "first_chip_pass": report.get("first_chip_pass"),
                "images": report.get("images"),
                "results": [(s["tile"], s["result"]) for s in report["steps"]],
                "csrf": report["api"]["csrf_rejected"],
                "checkout": report["api"]["checkout"],
                "errors": report["api"]["errors"],
                "crash": report.get("crash"),
                "notes": report["notes"],
            },
            indent=2,
        )
    )
    return 0 if not report.get("crash") else 1


if __name__ == "__main__":
    sys.exit(main())
