"""Mother-birthday customer walk against the public Path B pilot.

URL: https://aea.artof.link/  (ACM TLS — do not ignore certificate errors)
Payment / T-07 Place Order is skipped unless checkout is clearly available
without inventing card fields. Default: skip Place Order.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://aea.artof.link/"
OUT = Path(__file__).with_name("2026-08-16-pilot-mother-birthday-migrated.json")
SHOTS = Path(__file__).with_name("_walk_shots_pilot_migrated")
SHOTS.mkdir(exist_ok=True)

report: dict = {
    "url": URL,
    "scenario": "mother-birthday",
    "payment_included": False,
    "origin": "https://aea.artof.link",
    "steps": [],
    "api": {
        "suggestions": [],
        "csrf_rejected": False,
        "posts": [],
        "session_mint": None,
        "auth_errors": [],
        "status_codes": [],
    },
    "workspace": {},
    "notes": [],
    "first_blocker": None,
}


def step(tile: str, expected: str, actual: str, result: str) -> None:
    report["steps"].append(
        {"tile": tile, "expected": expected, "actual": actual, "result": result}
    )
    if result in ("fail", "blocked") and report["first_blocker"] is None:
        if result == "fail" or "session" in tile.lower() or "boot" in tile.lower():
            report["first_blocker"] = {"tile": tile, "actual": actual, "result": result}


def sanitize_post(rec: dict) -> dict:
    """Keep status/error evidence; drop session tokens and payloads."""
    keep = {
        "path": rec.get("path"),
        "status": rec.get("status"),
        "method": rec.get("method"),
        "error": rec.get("error"),
        "code": rec.get("code"),
    }
    if rec.get("structured_intent"):
        keep["structured_intent_keys"] = list(
            (rec.get("structured_intent") or {}).keys()
        )
    if rec.get("rec_count") is not None:
        keep["rec_count"] = rec["rec_count"]
    if rec.get("order_status"):
        keep["order_status"] = rec["order_status"]
    return keep


def main() -> int:
    delivery_date = (date.today() + timedelta(days=7)).isoformat()
    with sync_playwright() as p:
        # Public ACM TLS — do not ignore certificate errors.
        launch_kwargs = {"headless": True}
        browser = None
        for channel in ("msedge", "chrome", None):
            try:
                if channel:
                    browser = p.chromium.launch(channel=channel, **launch_kwargs)
                    report["browser"] = f"playwright channel={channel}"
                else:
                    browser = p.chromium.launch(**launch_kwargs)
                    report["browser"] = "playwright chromium"
                break
            except Exception as launch_exc:
                report["notes"].append(f"launch {channel}: {type(launch_exc).__name__}: {launch_exc}")
        if browser is None:
            raise RuntimeError("No Playwright browser available (tried msedge, chrome, chromium)")
        context = browser.new_context(
            ignore_https_errors=False,
            viewport={"width": 1440, "height": 1100},
        )
        page = context.new_page()

        def on_response(response):
            url = response.url
            if "aea.artof.link" not in url:
                return
            path = url.split("aea.artof.link")[-1]
            rec = {
                "path": path.split("?")[0],
                "status": response.status,
                "method": response.request.method,
            }
            report["api"]["status_codes"].append(
                {
                    "method": rec["method"],
                    "path": rec["path"],
                    "status": rec["status"],
                }
            )
            body = None
            try:
                if "/api/" in url:
                    body = response.json()
            except Exception:
                body = None
            rec["error"] = None
            if isinstance(body, dict):
                rec["error"] = body.get("error") or body.get("code")
                rec["code"] = body.get("code")
                if rec["error"] == "csrf_rejected":
                    report["api"]["csrf_rejected"] = True
                if rec["error"] in (
                    "authentication_required",
                    "orchestration_unavailable",
                ) or rec["status"] in (401, 403, 500):
                    report["api"]["auth_errors"].append(
                        {
                            "path": rec["path"],
                            "status": rec["status"],
                            "error": rec["error"],
                            "correlation_id": body.get("correlation_id"),
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
                    }
                    rec["rec_count"] = len(items or [])
                if rec["path"].endswith("/api/v1/session") and rec["method"] == "POST":
                    report["api"]["session_mint"] = {
                        "status": rec["status"],
                        "error": rec["error"],
                        "has_session": bool(body.get("session_id") or body.get("id") or body.get("csrf_token")),
                        "correlation_id": body.get("correlation_id"),
                    }
                if rec["path"].endswith("/api/v1/checkout"):
                    rec["order_status"] = body.get("status")
            if rec["path"].startswith("/api/") or rec["method"] in (
                "POST",
                "PATCH",
                "PUT",
            ):
                report["api"]["posts"].append(sanitize_post(rec))

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
                  const cards = [...document.querySelectorAll('#recommendation-cards .card')].map(
                    (c) => (c.innerText || '').replace(/\\n/g, ' | ').slice(0, 240)
                  );
                  return {
                    title: document.title,
                    understanding: document.querySelector('#understanding')?.innerText,
                    listHidden: list ? list.hidden : null,
                    formError: err && !err.hidden ? err.innerText : '',
                    notice: notice && !notice.hidden ? notice.innerText : '',
                    continueDisabled: cont ? cont.disabled : null,
                    chips,
                    suggestionsHidden: document.querySelector('#suggestions')?.hidden,
                    messageForm: !!document.querySelector('#message-form'),
                    composer: !!document.querySelector('#message'),
                    cards,
                    stepCaption: document.querySelector('#step-caption')?.innerText || '',
                    checkoutVisible: !!document.querySelector('#checkout-form, #payment-form, [data-tile="checkout"]'),
                    hasCardNumber: !!document.querySelector('input[autocomplete="cc-number"], input[name="card"], input[name="pan"]'),
                    sessionPayRef: document.querySelector('#session-pay-ref, [data-session-pay-ref]')?.innerText || '',
                  };
                }"""
            )

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

        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector("#message-form", timeout=25000)
            except Exception as boot_exc:
                shot = SHOTS / "00-boot-fail.png"
                page.screenshot(path=str(shot), full_page=True)
                mint = report["api"].get("session_mint")
                actual = (
                    f"Workspace did not show #message-form. "
                    f"title={page.title()!r} url={page.url!r} "
                    f"session_mint={mint} auth_errors={report['api']['auth_errors']} "
                    f"boot_exc={type(boot_exc).__name__}: {boot_exc}"
                )
                step(
                    "Boot / session mint",
                    "Customer workspace boots; session mint succeeds so composer is usable",
                    actual,
                    "fail",
                )
                report["notes"].append(
                    "Stop: session/boot blocked. Post-migration rewalk."
                )
                report["crash"] = actual
                page.screenshot(path=str(SHOTS / "crash.png"), full_page=True)
                raise SystemExit(0)

            page.wait_for_timeout(2500)
            mint = report["api"].get("session_mint")
            if mint and mint.get("status") == 500:
                shot = SHOTS / "00-session-500.png"
                page.screenshot(path=str(shot), full_page=True)
                step(
                    "Boot / session mint",
                    "POST /api/v1/session succeeds so the shopper can start",
                    f"Session mint HTTP {mint.get('status')} error={mint.get('error')!r} "
                    f"correlation_id={mint.get('correlation_id')}. Likely missing "
                    f"orchestration.experience_session (RDS migrations not applied). "
                    f"Composer error: {dump().get('formError')!r}",
                    "fail",
                )
                report["notes"].append(
                    "Stop: session mint still 500 after migrate."
                )
                report["first_blocker"] = {
                    "tile": "Boot / session mint",
                    "actual": "POST /api/v1/session returned 500",
                    "result": "fail",
                }
                page.screenshot(path=str(SHOTS / "crash.png"), full_page=True)
                raise SystemExit(0)

            report["boot"] = dump()
            chips = page.locator("#suggestions button").all_text_contents()
            assistant = page.locator("#messages").inner_text()
            page.screenshot(path=str(SHOTS / "01-landing.png"), full_page=True)
            step(
                "T-01 Enter / Discovery",
                "Welcome + composer; customer can describe the occasion in own words",
                f"Welcome visible. Assistant: {assistant.strip()[:160]!r}. Chips: {chips}. "
                f"Composer present. session_mint={mint}.",
                "pass" if page.locator("#message").is_visible() else "fail",
            )

            after_partial = send_and_wait("I need flowers...", timeout_ms=20000)
            chips_after = [c["text"] for c in (after_partial.get("chips") or [])]
            log = page.locator("#messages").inner_text()
            page.screenshot(path=str(SHOTS / "02-partial-thought.png"), full_page=True)
            joined = " ".join(chips_after)
            thought_fail = "for Mom" not in joined and "Mum" not in joined
            if after_partial.get("formError"):
                thought_result = "fail"
            else:
                thought_result = "fail" if thought_fail else "pass"
            step(
                "T-01 thought completion (ADR-003)",
                "Partial 'I need flowers…' yields evolving suggestions such as 'for Mom'; chips optional; typing always allowed",
                f"Notice: {after_partial.get('notice')!r}. Chips: {chips_after}. "
                f"Customer line in log: {'I need flowers' in log}. "
                f"formError: {after_partial.get('formError')!r}. "
                f"API suggestions: {report['api']['suggestions']}.",
                thought_result,
            )

            after_full = send_and_wait("Birthday flowers for Mum, under $75")
            intent_text = ""
            if page.locator("#understanding").count():
                intent_text = page.locator("#understanding").inner_text()
            page.screenshot(path=str(SHOTS / "03-intent.png"), full_page=True)
            intent_ok = any(
                token in intent_text.lower()
                for token in ("birthday", "mother", "mum", "75")
            )
            csrf = report["api"]["csrf_rejected"]
            form_err = after_full.get("formError") or ""
            step(
                "T-01 Conversation Send + T-02 Shared Understanding",
                "Message posts; occasion/recipient/budget appear; Review and correct exists",
                f"Intent panel: {intent_text[:400]!r}. Review and correct: "
                f"{page.locator('#correct-open').is_visible()}. "
                f"csrf_rejected={csrf}. formError={form_err!r}.",
                "fail" if csrf or form_err or not intent_ok else "pass",
            )

            if page.locator("#correct-open").is_visible():
                page.click("#correct-open")
                page.select_option("#correct-facet", "recipient")
                page.fill("#correct-value", "Mum")
                page.click("#correct-form button[type='submit']")
                page.wait_for_timeout(1500)
                intent_after = page.locator("#understanding").inner_text()
                step(
                    "T-02 Review and correct",
                    "Customer can correct a wrong or incomplete facet (FR-021)",
                    f"Saved recipient correction to 'Mum'. Panel now: {intent_after[:300]!r}",
                    "pass"
                    if any(x in intent_after.lower() for x in ("mum", "mother"))
                    else "fail",
                )

            continue_rec = page.locator("button[data-goto-step='3']")
            step3 = page.locator("#journey-steps button[data-step='3']")
            if continue_rec.count() and continue_rec.first.is_enabled():
                continue_rec.first.click()
            elif step3.count() and step3.first.is_enabled():
                step3.first.click()
            else:
                report["notes"].append(f"step 3 still locked: {dump()}")
            page.wait_for_timeout(2000)

            cards = page.locator("#recommendation-cards .card")
            card_count = cards.count()
            card_copy = [
                cards.nth(i).inner_text().replace("\n", " | ") for i in range(card_count)
            ]
            page.screenshot(path=str(SHOTS / "04-recommendations.png"), full_page=True)
            empty_copy = page.locator("#recommendation-empty, #recommendations").inner_text() if page.locator("#recommendation-empty, #recommendations").count() else ""
            caption = (
                page.locator("#step-caption").inner_text()
                if page.locator("#step-caption").count()
                else ""
            )
            available = any("Available" in c for c in card_copy)
            if card_count == 0:
                t03 = "fail"
                report["notes"].append(
                    "T-03 empty/unknown: inventory may be unseeded on Path B. "
                    "Friction vs blocker: customer cannot Select if there are no cards."
                )
            elif not available:
                t03 = "fail"
            else:
                t03 = "pass"
            step(
                "T-03 Curated Recommendations",
                "Validated options matching birthday / Mum / budget; available options selectable",
                f"Caption: {caption!r}. Cards ({card_count}): {card_copy}. "
                f"empty={empty_copy[:240]!r}. last_workspace={report['api'].get('last_workspace')}",
                t03,
            )

            select_btns = page.locator(
                "#recommendation-cards button.primary:not([disabled])"
            )
            if select_btns.count() == 0:
                step(
                    "T-04 Select + customize",
                    "Select an available arrangement; size; physical card message; optional flower/colour/ribbon",
                    f"No enabled Select button. card_count={card_count} copy={card_copy}",
                    "fail" if card_count == 0 else "fail",
                )
            else:
                select_btns.first.click()
                page.wait_for_timeout(2000)
                page.fill("#size", "Standard")
                if page.locator("#colour").count():
                    try:
                        page.select_option("#colour", "pink")
                    except Exception:
                        pass
                if page.locator("#ribbon").count():
                    try:
                        page.select_option("#ribbon", "satin")
                    except Exception:
                        pass
                page.fill("#card-message", "Happy Birthday Mum — love you")
                page.click("#selection-form button[type='submit']")
                page.wait_for_timeout(2000)
                page.screenshot(path=str(SHOTS / "05-customize.png"), full_page=True)
                arrangement = (
                    page.locator("#arrangement").input_value()
                    if page.locator("#arrangement").count()
                    else ""
                )
                step(
                    "T-04 Select + customize",
                    "Select arrangement; size; physical card message; optional flower/colour/ribbon",
                    f"Arrangement={arrangement!r} size={page.locator('#size').input_value()!r} "
                    f"card={page.locator('#card-message').input_value()!r}",
                    "pass" if arrangement else "fail",
                )

                to_delivery = page.locator("button[data-goto-step='5']")
                if to_delivery.count() and to_delivery.first.is_enabled():
                    to_delivery.first.click()
                    page.wait_for_timeout(800)
                page.fill("#delivery-date", delivery_date)
                if page.locator("input[name='window'][value='morning']").count():
                    page.check("input[name='window'][value='morning']")
                dest_mode = page.locator("input[name='destination-mode'][value='session']")
                if dest_mode.count():
                    dest_mode.check()
                dest_ref = (
                    page.locator("#session-destination-ref").inner_text()
                    if page.locator("#session-destination-ref").count()
                    else ""
                )
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
                page.screenshot(path=str(SHOTS / "06-delivery.png"), full_page=True)
                step(
                    "T-05 Delivery",
                    "Date + named window; confirm saved destination reference (not a street address); Confirm persists",
                    f"Date {delivery_date}, window morning, destination ref {dest_ref!r}. "
                    f"Street-address fields={street.count()}. Banner={banner_text!r} "
                    f"error={err!r} csrf={report['api']['csrf_rejected']}",
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
                if not summary and page.locator("button[data-goto-step='6']").count():
                    btn = page.locator("button[data-goto-step='6']").first
                    if btn.is_enabled():
                        btn.click()
                        page.wait_for_timeout(800)
                    summary = (
                        page.locator("#order-summary").inner_text()
                        if page.locator("#order-summary").is_visible()
                        else ""
                    )
                page.screenshot(path=str(SHOTS / "07-summary.png"), full_page=True)
                has_total = "Total" in summary or "total" in summary.lower()
                step(
                    "T-06 Order Summary",
                    "Itemized charges update after selection and delivery",
                    f"Summary panel: {summary[:500]!r}",
                    "pass" if has_total else "fail",
                )

                # Observe checkout tile only. Do not Place Order / invent card fields.
                checkout_visible = page.locator(
                    "#checkout-form, button:has-text('Create order'), button:has-text('Place Order')"
                ).count()
                has_pan = page.locator(
                    "input[autocomplete='cc-number'], input[name='cardNumber'], input[name='pan']"
                ).count()
                pay_ref = (
                    page.locator("#session-pay-ref").inner_text()
                    if page.locator("#session-pay-ref").count()
                    else ""
                )
                step(
                    "T-07 Checkout",
                    "Stop before payment unless Path B checkout is clearly available without card fields",
                    f"Checkout controls visible={checkout_visible}. PAN fields={has_pan}. "
                    f"session pay ref present={bool(pay_ref)}. Default skip Place Order.",
                    "blocked",
                )

            if not any(s["tile"].startswith("T-07") for s in report["steps"]):
                step(
                    "T-07 Checkout",
                    "Stop before payment unless asked",
                    "Did not reach checkout. Payment not included. Did not Place Order.",
                    "blocked",
                )
            step(
                "T-08 Tracking",
                "Tracking after confirmed order",
                "Skipped with payment. Contact Florist lives on tracking.",
                "blocked",
            )

            if page.locator("button.help-button").count():
                page.click("button.help-button")
                page.wait_for_timeout(400)
                help_copy = (
                    page.locator("#help").inner_text()
                    if page.locator("#help").count()
                    else ""
                )
                if page.locator("#support-question").count():
                    page.fill("#support-question", "When will delivery arrive?")
                    page.click("#support-form button[type='submit']")
                    page.wait_for_timeout(1500)
                answer = (
                    page.locator("#support-answer").inner_text()
                    if page.locator("#support-answer").is_visible()
                    else ""
                )
                page.screenshot(path=str(SHOTS / "08-help.png"), full_page=True)
                not_a_person = (
                    "not a person" in help_copy.lower() or "Automated" in help_copy
                )
                step(
                    "ASO Help",
                    "Help available without leaving the workspace; labeled as not a person",
                    f"Help dialog: {help_copy[:280]!r}. Answer: {answer!r}.",
                    "pass" if not_a_person else "fail",
                )
                if page.locator("[data-close-help]").count():
                    page.click("[data-close-help]")
            else:
                step(
                    "ASO Help",
                    "Help available without leaving the workspace; labeled as not a person",
                    "Help button not found after walk.",
                    "fail",
                )

            report["workspace"] = dump()
            report["delivery_date"] = delivery_date
            page.screenshot(path=str(SHOTS / "09-final.png"), full_page=True)
        except SystemExit:
            pass
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

    # Cap status_codes so the file is not a session dump
    codes = report["api"]["status_codes"]
    report["api"]["status_codes"] = codes[:80]
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(OUT),
                "results": [
                    {"tile": s["tile"], "result": s["result"]} for s in report["steps"]
                ],
                "csrf": report["api"]["csrf_rejected"],
                "session_mint": report["api"].get("session_mint"),
                "auth_errors": report["api"]["auth_errors"],
                "first_blocker": report.get("first_blocker"),
                "crash": report.get("crash"),
                "notes": report.get("notes"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
