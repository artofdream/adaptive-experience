"""Path B rewalk after merged !219 (T-05 past dates) and !220 (mobile Help).

URL: https://aea.artof.link/  (ACM TLS — do not ignore certificate errors)
Mother-birthday T-01…T-06. Payment / T-07 Place Order skipped.
Do not open /florist.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://aea.artof.link/"
OUT = Path(__file__).with_name("2026-08-17-mother-birthday-t05-help.json")
SHOTS = Path(__file__).with_name("_walk_shots_t05_help")
SHOTS.mkdir(exist_ok=True)

TODAY = date.today()
YESTERDAY = (TODAY - timedelta(days=1)).isoformat()
DELIVERY_DATE = (TODAY + timedelta(days=7)).isoformat()

report: dict = {
    "url": URL,
    "scenario": "mother-birthday",
    "payment_included": False,
    "origin": "https://aea.artof.link",
    "assignment": "Path B rewalk after !219 T-05 past dates and !220 mobile Help FAB",
    "steps": [],
    "api": {
        "suggestions": [],
        "csrf_rejected": False,
        "posts": [],
        "session_mint": None,
        "auth_errors": [],
        "status_codes": [],
        "ai_modes": [],
        "select_enabled": None,
        "availability_badges": [],
    },
    "t05_past_dates": {},
    "mobile_help": {},
    "tablet_column_order": {},
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
    with sync_playwright() as p:
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
                report["notes"].append(
                    f"launch {channel}: {type(launch_exc).__name__}: {launch_exc}"
                )
        if browser is None:
            raise RuntimeError(
                "No Playwright browser available (tried msedge, chrome, chromium)"
            )
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
                mode = body.get("assistant_mode") or body.get("mode")
                if mode:
                    report["api"]["ai_modes"].append(
                        {"path": rec["path"], "mode": mode}
                    )
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
                        "has_session": bool(
                            body.get("session_id")
                            or body.get("id")
                            or body.get("csrf_token")
                        ),
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
                    (c) => {
                      const select = c.querySelector('button.primary');
                      return {
                        text: (c.innerText || '').replace(/\\n/g, ' | ').slice(0, 240),
                        title: c.querySelector('h3')?.textContent || '',
                        badge: c.querySelector('.badge')?.textContent || '',
                        selectDisabled: select ? !!select.disabled : null,
                      };
                    }
                  );
                  const dateInput = document.querySelector('#delivery-date');
                  return {
                    title: document.title,
                    understanding: document.querySelector('#understanding')?.innerText,
                    listHidden: list ? list.hidden : null,
                    listCount: list ? list.children.length : 0,
                    formError: err && !err.hidden ? err.innerText : '',
                    notice: notice && !notice.hidden ? notice.innerText : '',
                    continueDisabled: cont ? cont.disabled : null,
                    chips,
                    suggestionsHidden: document.querySelector('#suggestions')?.hidden,
                    messageForm: !!document.querySelector('#message-form'),
                    composer: !!document.querySelector('#message'),
                    cards,
                    selectEnabledCount: cards.filter((c) => c.selectDisabled === false).length,
                    availabilityBadges: cards.map((c) => ({
                      title: c.title,
                      badge: c.badge,
                      selectDisabled: c.selectDisabled,
                    })),
                    stepCaption: document.querySelector('#step-caption')?.innerText || '',
                    checkoutVisible: !!document.querySelector('#checkout-form, #payment-form, [data-tile="checkout"]'),
                    hasCardNumber: !!document.querySelector('input[autocomplete="cc-number"], input[name="card"], input[name="pan"]'),
                    sessionPayRef: document.querySelector('#session-pay-ref, [data-session-pay-ref]')?.innerText || '',
                    deliveryMin: dateInput ? dateInput.min : null,
                    deliveryValue: dateInput ? dateInput.value : null,
                    deliveryHint: document.querySelector('#delivery-date-hint')?.innerText || '',
                    deliveryFormError: (() => {
                      const e = document.querySelector('#delivery-form-error');
                      return e && !e.hidden ? e.innerText : '';
                    })(),
                    deliveryValidity: dateInput ? dateInput.validationMessage : '',
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

        def wait_intent_facets(timeout_ms: int = 12000) -> dict:
            try:
                page.wait_for_function(
                    """() => {
                      const list = document.querySelector('#understanding-list');
                      return list && !list.hidden && list.children.length > 0;
                    }""",
                    timeout=timeout_ms,
                )
            except Exception:
                pass
            page.wait_for_timeout(400)
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
                report["notes"].append("Stop: session/boot blocked.")
                report["crash"] = actual
                page.screenshot(path=str(SHOTS / "crash.png"), full_page=True)
                raise SystemExit(0)

            page.wait_for_timeout(2500)
            mint = report["api"].get("session_mint")
            if mint and mint.get("status") == 500:
                page.screenshot(path=str(SHOTS / "00-session-500.png"), full_page=True)
                step(
                    "Boot / session mint",
                    "POST /api/v1/session succeeds so the shopper can start",
                    f"Session mint HTTP {mint.get('status')} error={mint.get('error')!r} "
                    f"correlation_id={mint.get('correlation_id')}. "
                    f"Composer error: {dump().get('formError')!r}",
                    "fail",
                )
                report["notes"].append("Stop: session mint 500.")
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
                f"formError: {after_partial.get('formError')!r}.",
                thought_result,
            )

            after_full = send_and_wait("Birthday flowers for Mum, under $75")
            after_full = wait_intent_facets()
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

            def goto_recommendations():
                continue_rec = page.locator("button[data-goto-step='3']")
                step3 = page.locator("#journey-steps button[data-step='3']")
                if continue_rec.count() and continue_rec.first.is_enabled():
                    continue_rec.first.click()
                elif step3.count() and step3.first.is_enabled():
                    step3.first.click()
                else:
                    report["notes"].append(f"step 3 still locked: {dump()}")
                page.wait_for_timeout(2000)

            goto_recommendations()

            def rec_snapshot():
                cards = page.locator("#recommendation-cards .card")
                count = cards.count()
                copy = [
                    cards.nth(i).inner_text().replace("\n", " | ") for i in range(count)
                ]
                snap = dump()
                return count, copy, snap, snap.get("availabilityBadges") or []

            card_count, card_copy, snap, badges = rec_snapshot()
            available = any("Available" in (c or "") for c in card_copy) or any(
                (b.get("badge") or "") == "Available" for b in badges
            )
            select_enabled = int(snap.get("selectEnabledCount") or 0)
            if not available and select_enabled == 0:
                report["notes"].append(
                    "T-03 first look: no Available badge / Select disabled. "
                    "Waiting one 30s heartbeat cycle, then re-opening recommendations."
                )
                page.screenshot(
                    path=str(SHOTS / "04-recommendations-unknown.png"), full_page=True
                )
                page.wait_for_timeout(35000)
                goto_recommendations()
                card_count, card_copy, snap, badges = rec_snapshot()
                available = any("Available" in (c or "") for c in card_copy) or any(
                    (b.get("badge") or "") == "Available" for b in badges
                )
                select_enabled = int(snap.get("selectEnabledCount") or 0)

            report["api"]["select_enabled"] = select_enabled > 0
            report["api"]["availability_badges"] = badges
            page.screenshot(path=str(SHOTS / "04-recommendations.png"), full_page=True)
            empty_copy = ""
            if page.locator("#recommendation-empty, #recommendations").count():
                empty_copy = page.locator(
                    "#recommendation-empty, #recommendations"
                ).inner_text()
            caption = (
                page.locator("#step-caption").inner_text()
                if page.locator("#step-caption").count()
                else ""
            )
            unknown = any(
                "Unknown" in (b.get("badge") or "") for b in badges
            )
            if card_count == 0:
                t03 = "fail"
                report["notes"].append("T-03 empty: no ranked cards after intent.")
            elif not available or select_enabled == 0:
                t03 = "fail"
            else:
                t03 = "pass"
            step(
                "T-03 Curated Recommendations",
                "Validated options matching birthday / Mum / budget; available options selectable (REFERENCE_CATALOG SKUs, Available badges)",
                f"Caption: {caption!r}. Cards ({card_count}): {card_copy}. "
                f"badges={badges}. select_enabled={select_enabled}. unknown={unknown}. "
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
                    f"No enabled Select button. card_count={card_count} copy={card_copy} "
                    f"badges={badges} select_enabled={select_enabled}",
                    "fail",
                )
                step(
                    "T-05 Delivery",
                    "Date + named window; confirm saved destination reference; past dates disabled/min-date",
                    "Not reached: Select stayed disabled.",
                    "blocked",
                )
                step(
                    "T-05 past dates (!219)",
                    "Past days disabled / min=today; past value rejected",
                    "Not reached: Select stayed disabled.",
                    "blocked",
                )
                step(
                    "T-06 Order Summary",
                    "Itemized charges update after selection and delivery",
                    "Not reached: Select stayed disabled.",
                    "blocked",
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

                # --- T-05 past-date guard (!219) before confirming a future date ---
                page.locator("#delivery-date").click()
                page.wait_for_timeout(200)
                t05_probe = page.evaluate(
                    """([yesterday]) => {
                      const input = document.querySelector('#delivery-date');
                      if (!input) return { missing: true };
                      const before = { min: input.min, value: input.value, hint: document.querySelector('#delivery-date-hint')?.innerText || '' };
                      input.value = yesterday;
                      input.dispatchEvent(new Event('input', { bubbles: true }));
                      input.dispatchEvent(new Event('change', { bubbles: true }));
                      const afterSet = {
                        min: input.min,
                        value: input.value,
                        validity: input.validationMessage,
                        customError: input.validity.customError,
                        rangeUnderflow: input.validity.rangeUnderflow,
                        formError: (() => {
                          const e = document.querySelector('#delivery-form-error');
                          return e && !e.hidden ? e.innerText : '';
                        })(),
                      };
                      return { before, afterSet, today: input.min };
                    }""",
                    [YESTERDAY],
                )
                page.screenshot(path=str(SHOTS / "06a-past-date.png"), full_page=True)
                if page.locator("#delivery-form button[type='submit']").count():
                    page.click("#delivery-form button[type='submit']")
                    page.wait_for_timeout(800)
                after_submit_past = dump()
                page.screenshot(
                    path=str(SHOTS / "06b-past-date-submit.png"), full_page=True
                )
                confirmed_after_past = False
                if page.locator("#delivery-confirmed").count():
                    confirmed_after_past = page.locator("#delivery-confirmed").is_visible()
                min_ok = (t05_probe or {}).get("today") == TODAY.isoformat() or (
                    (t05_probe or {}).get("before") or {}
                ).get("min") == TODAY.isoformat()
                past_copy = (
                    (after_submit_past.get("deliveryFormError") or "")
                    + " "
                    + (after_submit_past.get("deliveryValidity") or "")
                    + " "
                    + ((t05_probe or {}).get("afterSet") or {}).get("formError", "")
                    + " "
                    + ((t05_probe or {}).get("afterSet") or {}).get("validity", "")
                )
                rejected = (
                    "past" in past_copy.lower()
                    or "today or later" in past_copy.lower()
                    or ((t05_probe or {}).get("afterSet") or {}).get("customError")
                    or ((t05_probe or {}).get("afterSet") or {}).get("rangeUnderflow")
                    or not confirmed_after_past
                )
                report["t05_past_dates"] = {
                    "today": TODAY.isoformat(),
                    "yesterday": YESTERDAY,
                    "probe": t05_probe,
                    "after_submit": {
                        "formError": after_submit_past.get("deliveryFormError"),
                        "validity": after_submit_past.get("deliveryValidity"),
                        "value": after_submit_past.get("deliveryValue"),
                        "min": after_submit_past.get("deliveryMin"),
                        "hint": after_submit_past.get("deliveryHint"),
                        "confirmed_visible": confirmed_after_past,
                    },
                }
                t05_past_result = "pass" if min_ok and rejected and not confirmed_after_past else "fail"
                if confirmed_after_past:
                    t05_past_result = "fail"
                    report["notes"].append(
                        "Past delivery date appeared to confirm — !219 regression."
                    )
                step(
                    "T-05 past dates (!219)",
                    "Date input min=today; past days cannot be delivered; Confirm does not persist a past date",
                    f"min={((t05_probe or {}).get('before') or {}).get('min')!r} today={TODAY.isoformat()} "
                    f"yesterday_set={((t05_probe or {}).get('afterSet') or {})} "
                    f"after_submit_error={after_submit_past.get('deliveryFormError')!r} "
                    f"validity={after_submit_past.get('deliveryValidity')!r} "
                    f"confirmed_after_past={confirmed_after_past} hint={after_submit_past.get('deliveryHint')!r}",
                    t05_past_result,
                )

                page.fill("#delivery-date", DELIVERY_DATE)
                if page.locator("input[name='window'][value='morning']").count():
                    page.check("input[name='window'][value='morning']")
                dest_mode = page.locator(
                    "input[name='destination-mode'][value='session']"
                )
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
                    f"Date {DELIVERY_DATE}, window morning, destination ref {dest_ref!r}. "
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

            # Desktop ASO FAB still present at 1440.
            if page.locator("button.aso").count():
                page.click("button.aso")
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
                page.screenshot(path=str(SHOTS / "08-help-desktop.png"), full_page=True)
                not_a_person = (
                    "not a person" in help_copy.lower() or "Automated" in help_copy
                )
                step(
                    "ASO Help (desktop FAB)",
                    "Help available without leaving the workspace; labeled as not a person",
                    f"Help dialog: {help_copy[:280]!r}. Answer: {answer!r}.",
                    "pass" if not_a_person else "fail",
                )
                if page.locator("[data-close-help]").count():
                    page.click("[data-close-help]")
                    page.wait_for_timeout(300)
            else:
                step(
                    "ASO Help (desktop FAB)",
                    "Help available without leaving the workspace; labeled as not a person",
                    "Desktop ? FAB not found after walk.",
                    "fail",
                )

            # Tablet: T-01 vs T-02 column order (known friction — observe only).
            page.set_viewport_size({"width": 768, "height": 1024})
            page.wait_for_timeout(500)
            tablet = page.evaluate(
                """() => {
                  const conv = document.querySelector('#conversation');
                  const und = document.querySelector('#understanding');
                  const cr = conv ? conv.getBoundingClientRect() : null;
                  const ur = und ? und.getBoundingClientRect() : null;
                  const orderConv = conv ? getComputedStyle(conv).order : null;
                  const orderUnd = und ? getComputedStyle(und).order : null;
                  const mainCols = getComputedStyle(document.querySelector('main.workspace')).gridTemplateColumns;
                  return {
                    conversationTop: cr ? Math.round(cr.top) : null,
                    understandingTop: ur ? Math.round(ur.top) : null,
                    conversationOrder: orderConv,
                    understandingOrder: orderUnd,
                    workspaceColumns: mainCols,
                    t02AboveT01: ur && cr ? ur.top < cr.top - 8 : null,
                  };
                }"""
            )
            report["tablet_column_order"] = tablet
            page.screenshot(path=str(SHOTS / "09-tablet-column.png"), full_page=True)
            t02_above = bool(tablet.get("t02AboveT01"))
            step(
                "Tablet T-01 vs T-02 column order (known friction)",
                "Observe whether Intent Summary (T-02) still paints above Conversation (T-01) at tablet width; do not implement",
                f"viewport 768x1024. t02AboveT01={t02_above}. "
                f"conversationTop={tablet.get('conversationTop')} understandingTop={tablet.get('understandingTop')} "
                f"orders conv={tablet.get('conversationOrder')} und={tablet.get('understandingOrder')} "
                f"workspaceColumns={tablet.get('workspaceColumns')!r}.",
                "pass",
            )
            if t02_above:
                report["notes"].append(
                    "Known friction still present: tablet stacks T-02 above T-01."
                )

            # Mobile Help (!220): FAB hidden so it cannot cover Send; header Help usable.
            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(500)
            if page.locator("#help").count() and page.locator("#help").evaluate(
                "el => el.open"
            ):
                if page.locator("[data-close-help]").count():
                    page.click("[data-close-help]")
                    page.wait_for_timeout(200)
            mobile = page.evaluate(
                """() => {
                  const fab = document.querySelector('button.aso');
                  const header = document.querySelector('.help-button');
                  const send = document.querySelector('button.send');
                  const fabStyle = fab ? getComputedStyle(fab) : null;
                  const headerStyle = header ? getComputedStyle(header) : null;
                  const sendBox = send ? send.getBoundingClientRect() : null;
                  const fabBox = fab ? fab.getBoundingClientRect() : null;
                  const headerBox = header ? header.getBoundingClientRect() : null;
                  const overlap = (a, b) => {
                    if (!a || !b) return false;
                    return !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom);
                  };
                  return {
                    fabDisplay: fabStyle ? fabStyle.display : null,
                    fabVisible: fab ? fabStyle.display !== 'none' && fabStyle.visibility !== 'hidden' && fabBox.width > 0 : false,
                    headerHelpDisplay: headerStyle ? headerStyle.display : null,
                    headerHelpVisible: header ? headerStyle.display !== 'none' && headerBox.width > 0 && headerBox.height > 0 : false,
                    headerHelpHeight: headerBox ? Math.round(headerBox.height) : null,
                    sendVisible: send ? sendBox.width > 0 : false,
                    fabOverlapsSend: overlap(fabBox, sendBox) && fabStyle && fabStyle.display !== 'none',
                    headerText: header ? header.textContent.trim() : '',
                  };
                }"""
            )
            page.screenshot(path=str(SHOTS / "10-mobile-before-help.png"), full_page=True)
            help_opened = False
            help_copy_m = ""
            answer_m = ""
            if mobile.get("headerHelpVisible") and page.locator(".help-button").count():
                page.locator(".help-button").click()
                page.wait_for_timeout(500)
                help_opened = page.locator("#help").evaluate("el => el.open")
                help_copy_m = page.locator("#help").inner_text() if help_opened else ""
                if help_opened and page.locator("#support-question").count():
                    page.fill("#support-question", "When will delivery arrive?")
                    page.click("#support-form button[type='submit']")
                    page.wait_for_timeout(1500)
                    if page.locator("#support-answer").is_visible():
                        answer_m = page.locator("#support-answer").inner_text()
                page.screenshot(path=str(SHOTS / "11-mobile-help.png"), full_page=True)
                if page.locator("[data-close-help]").count():
                    page.click("[data-close-help]")
                    page.wait_for_timeout(300)
            composer_still = page.locator("#message").is_visible()
            report["mobile_help"] = {
                **mobile,
                "help_opened": help_opened,
                "help_copy": help_copy_m[:280],
                "answer": answer_m,
                "composer_after_close": composer_still,
            }
            not_person = "not a person" in help_copy_m.lower() or "Automated" in help_copy_m
            mobile_ok = (
                mobile.get("headerHelpVisible")
                and help_opened
                and not_person
                and composer_still
                and not mobile.get("fabOverlapsSend")
            )
            step(
                "ASO Help (mobile, !220)",
                "On a phone-sized viewport, Help is usable without covering Send; labeled as not a person; close and continue",
                f"fabDisplay={mobile.get('fabDisplay')!r} fabVisible={mobile.get('fabVisible')} "
                f"headerHelpVisible={mobile.get('headerHelpVisible')} headerHeight={mobile.get('headerHelpHeight')} "
                f"fabOverlapsSend={mobile.get('fabOverlapsSend')} help_opened={help_opened} "
                f"not_a_person={not_person} answer={answer_m!r} composer_after_close={composer_still}.",
                "pass" if mobile_ok else "fail",
            )

            report["workspace"] = dump()
            report["delivery_date"] = DELIVERY_DATE
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.screenshot(path=str(SHOTS / "12-final.png"), full_page=True)
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
                "select_enabled": report["api"].get("select_enabled"),
                "availability_badges": report["api"].get("availability_badges"),
                "t05_past_dates": report.get("t05_past_dates"),
                "tablet_column_order": report.get("tablet_column_order"),
                "mobile_help": {
                    k: report.get("mobile_help", {}).get(k)
                    for k in (
                        "fabDisplay",
                        "fabVisible",
                        "headerHelpVisible",
                        "help_opened",
                        "fabOverlapsSend",
                        "answer",
                    )
                },
                "ai_modes": report["api"].get("ai_modes"),
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
