"""Live mother-birthday customer walk against https://localhost:8443/."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://localhost:8443/"
OUT = Path(__file__).with_name("2026-08-15-mother-birthday-e2e-walk.json")
SHOTS = Path(__file__).with_name("_walk_shots")
SHOTS.mkdir(exist_ok=True)

report: dict = {
    "url": "https://localhost:8443/",
    "scenario": "mother-birthday",
    "payment_included": False,
    "steps": [],
    "api": {"suggestions": [], "csrf_rejected": False, "posts": []},
    "workspace": {},
    "notes": [],
}


def step(tile: str, expected: str, actual: str, result: str) -> None:
    report["steps"].append(
        {"tile": tile, "expected": expected, "actual": actual, "result": result}
    )


def main() -> int:
    delivery_date = (date.today() + timedelta(days=7)).isoformat()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--ignore-certificate-errors",
                "--host-resolver-rules=MAP localhost 127.0.0.1",
            ],
        )
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
                if rec["error"] == "csrf_rejected":
                    report["api"]["csrf_rejected"] = True
                if "suggestions" in body:
                    report["api"]["suggestions"].append(body.get("suggestions"))
                if "structured_intent" in body:
                    rec["structured_intent"] = body.get("structured_intent")
                if "facets" in body:
                    recs = (body.get("facets") or {}).get("recommendations") or {}
                    items = recs.get("items") if isinstance(recs, dict) else recs
                    report["api"]["last_workspace"] = {
                        "context_version": body.get("context_version"),
                        "shared": (body.get("facets") or {}).get("shared_understanding"),
                        "rec_count": len(items or []),
                    }
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
                  return {
                    understanding: document.querySelector('#understanding')?.innerText,
                    listHidden: list ? list.hidden : null,
                    formError: err && !err.hidden ? err.innerText : '',
                    notice: notice && !notice.hidden ? notice.innerText : '',
                    continueDisabled: cont ? cont.disabled : null,
                    chips,
                    suggestionsHidden: document.querySelector('#suggestions')?.hidden,
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
                f"Welcome visible. Assistant: {assistant.strip()[:120]!r}. Chips: {chips}. Composer present.",
                "pass" if page.locator("#message").is_visible() else "fail",
            )

            after_partial = send_and_wait("I need flowers...", timeout_ms=12000)
            chips_after = [c["text"] for c in (after_partial.get("chips") or [])]
            log = page.locator("#messages").inner_text()
            page.screenshot(path=str(SHOTS / "02-partial-thought.png"), full_page=True)
            joined = " ".join(chips_after)
            thought_fail = "for Mom" not in joined and "Mum" not in joined
            step(
                "T-01 thought completion (ADR-003)",
                "Partial 'I need flowers…' yields evolving suggestions such as 'for Mom'; chips optional; typing always allowed",
                f"Notice: {after_partial.get('notice')!r}. Chips: {chips_after}. Customer line in log: {'I need flowers' in log}. API suggestions: {report['api']['suggestions']}.",
                "fail" if thought_fail else "pass",
            )

            after_full = send_and_wait("Birthday flowers for Mum, under €75")
            intent_text = page.locator("#understanding").inner_text()
            page.screenshot(path=str(SHOTS / "03-intent.png"), full_page=True)
            intent_ok = any(
                token in intent_text.lower() for token in ("birthday", "mother", "mum", "75")
            )
            step(
                "T-01 Conversation Send + T-02 Shared Understanding",
                "Message posts; occasion/recipient/budget appear; Review and correct exists",
                f"Intent panel: {intent_text[:400]!r}. Review and correct: {page.locator('#correct-open').is_visible()}. csrf_rejected={report['api']['csrf_rejected']}. dump={after_full}",
                "fail"
                if report["api"]["csrf_rejected"]
                else ("pass" if intent_ok else "fail"),
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
            page.wait_for_timeout(1500)

            cards = page.locator("#recommendation-cards .card")
            card_count = cards.count()
            card_copy = [
                cards.nth(i).inner_text().replace("\n", " | ") for i in range(card_count)
            ]
            page.screenshot(path=str(SHOTS / "04-recommendations.png"), full_page=True)
            step(
                "T-03 Curated Recommendations",
                "Validated options matching birthday / Mum / budget; available options selectable",
                f"Caption: {page.locator('#step-caption').inner_text()!r}. Cards ({card_count}): {card_copy}. last_workspace={report['api'].get('last_workspace')}",
                "pass" if card_count > 0 and any("Available" in c for c in card_copy) else "fail",
            )

            select_btns = page.locator("#recommendation-cards button.primary:not([disabled])")
            if select_btns.count() == 0:
                step("T-04 Select", "Select an available arrangement", "No enabled Select button", "fail")
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
                page.screenshot(path=str(SHOTS / "05-customize.png"), full_page=True)
                step(
                    "T-04 Select + customize",
                    "Select arrangement; size; physical card message; optional flower/colour/ribbon",
                    f"Arrangement={page.locator('#arrangement').input_value()!r} size={page.locator('#size').input_value()!r} colour={page.locator('#colour').input_value()!r} ribbon={page.locator('#ribbon').input_value()!r} card={page.locator('#card-message').input_value()!r}",
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
                    f"Date {delivery_date}, window morning (label 10:00–12:00), destination ref {dest_ref!r}. Street-address fields={street.count()}. Banner={banner_text!r} error={err!r} csrf={report['api']['csrf_rejected']}",
                    "fail"
                    if street.count() or report["api"]["csrf_rejected"] or (not banner_text and err)
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

            step(
                "T-07 Checkout",
                "Stop before payment unless asked",
                "Payment not included. Did not Place Order or enter a card/token confirmation.",
                "blocked",
            )
            step(
                "T-08 Tracking",
                "Tracking after confirmed order",
                "Skipped with payment. Contact Florist lives on tracking (CF-009 intentional).",
                "blocked",
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
            page.screenshot(path=str(SHOTS / "08-help.png"), full_page=True)
            not_a_person = "not a person" in help_copy.lower() or "Automated" in help_copy
            step(
                "ASO Help",
                "Help available without leaving the workspace; labeled as not a person",
                f"Help dialog: {help_copy[:280]!r}. Answer: {answer!r}. Contact Florist not in Help.",
                "pass" if not_a_person else "fail",
            )
            if page.locator("[data-close-help]").count():
                page.click("[data-close-help]")

            report["workspace"] = dump()
            report["delivery_date"] = delivery_date
            page.screenshot(path=str(SHOTS / "09-final.png"), full_page=True)
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
                "results": [s["result"] for s in report["steps"]],
                "csrf": report["api"]["csrf_rejected"],
                "crash": report.get("crash"),
            },
            indent=2,
        )
    )
    return 0 if not report.get("crash") else 1


if __name__ == "__main__":
    sys.exit(main())
