"""Path B rewalk after !226 RDS session rebind (and !227 Track stepper).

URL: https://aea.artof.link/  (ACM TLS — do not ignore certificate errors)
Focus: T-02 Review and correct — PATCH /api/v1/shared-understanding must
succeed without toast "Correction failed (session_required)".
Desktop + phone-width. Mother-birthday through T-06. Skip Place Order.
Do not open /florist.
"""
from __future__ import annotations

import json
import ssl
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://aea.artof.link/"
ORIGIN = "https://aea.artof.link"
OUT = Path(__file__).with_name("2026-08-17-mother-birthday-t02-rebind.json")
SHOTS = Path(__file__).with_name("_walk_shots_t02_rebind")
SHOTS.mkdir(exist_ok=True)

DELIVERY_DATE = (date.today() + timedelta(days=7)).isoformat()
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1100},
    "phone": {"width": 390, "height": 844},
}

report: dict = {
    "url": URL,
    "scenario": "mother-birthday",
    "payment_included": False,
    "origin": ORIGIN,
    "claimed_main": "b62ef96",
    "assignment": (
        "Path B T-02 Review and correct after !226 RDS session rebind "
        "(origin/main b62ef96). Confirm PATCH succeeds — no toast "
        "Correction failed (session_required). Desktop + phone-width. "
        "Through T-06. Skip T-07 Place Order. Do not open /florist."
    ),
    "healthz": None,
    "mcp_browser": (
        "cursor-ide-browser: tabs new created a tab then navigate failed "
        "(No browser tab available / Browser view not found). Playwright fallback."
    ),
    "florist_opened": False,
    "viewports": {},
    "notes": [],
    "first_blocker": None,
}


def probe_healthz() -> dict:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(f"{ORIGIN}/healthz", method="GET")
    with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return {
            "status": resp.status,
            "body": body[:200],
            "content_type": resp.headers.get("content-type"),
        }


def sanitize_post(rec: dict) -> dict:
    keep = {
        "path": rec.get("path"),
        "status": rec.get("status"),
        "method": rec.get("method"),
        "error": rec.get("error"),
        "code": rec.get("code"),
        "viewport": rec.get("viewport"),
    }
    if rec.get("structured_intent"):
        keep["structured_intent_keys"] = list(
            (rec.get("structured_intent") or {}).keys()
        )
        intent = rec.get("structured_intent") or {}
        keep["recipient"] = intent.get("recipient")
        keep["occasion"] = intent.get("occasion")
        keep["budget"] = intent.get("budget")
    if rec.get("rec_count") is not None:
        keep["rec_count"] = rec["rec_count"]
    if rec.get("order_status"):
        keep["order_status"] = rec["order_status"]
    if rec.get("context_version") is not None:
        keep["context_version"] = rec["context_version"]
    return keep


def new_viewport_bucket(name: str) -> dict:
    return {
        "name": name,
        "viewport": VIEWPORTS[name],
        "steps": [],
        "api": {
            "suggestions": [],
            "csrf_rejected": False,
            "session_required": False,
            "total_mismatch": False,
            "posts": [],
            "patches": [],
            "session_mint": None,
            "auth_errors": [],
            "status_codes": [],
            "ai_modes": [],
            "select_enabled": None,
            "availability_badges": [],
        },
        "t02": {},
        "workspace": {},
        "notes": [],
        "crash": None,
    }


def add_step(bucket: dict, tile: str, expected: str, actual: str, result: str) -> None:
    bucket["steps"].append(
        {"tile": tile, "expected": expected, "actual": actual, "result": result}
    )
    if result in ("fail", "blocked") and report["first_blocker"] is None:
        if result == "fail" or "session" in tile.lower() or "boot" in tile.lower():
            report["first_blocker"] = {
                "viewport": bucket["name"],
                "tile": tile,
                "actual": actual,
                "result": result,
            }


def attach_listeners(page, bucket: dict) -> None:
    def on_response(response):
        url = response.url
        if "aea.artof.link" not in url:
            return
        path = url.split("aea.artof.link")[-1]
        rec = {
            "path": path.split("?")[0],
            "status": response.status,
            "method": response.request.method,
            "viewport": bucket["name"],
        }
        bucket["api"]["status_codes"].append(
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
            rec["code"] = body.get("code") or body.get("error")
            rec["context_version"] = body.get("context_version")
            mode = body.get("assistant_mode") or body.get("mode")
            if mode:
                bucket["api"]["ai_modes"].append(
                    {"path": rec["path"], "mode": mode}
                )
            if rec["error"] == "csrf_rejected":
                bucket["api"]["csrf_rejected"] = True
            if rec["error"] == "session_required" or rec["code"] == "session_required":
                bucket["api"]["session_required"] = True
            if rec["error"] == "total_mismatch" or rec["code"] == "total_mismatch":
                bucket["api"]["total_mismatch"] = True
                report["notes"].append(
                    f"{bucket['name']}: observed total_mismatch on {rec['method']} {rec['path']} "
                    f"status={rec['status']} (observe only — Support intake, not this walk)."
                )
            if rec["error"] in (
                "authentication_required",
                "orchestration_unavailable",
                "session_required",
            ) or rec["status"] in (401, 403, 500):
                bucket["api"]["auth_errors"].append(
                    {
                        "path": rec["path"],
                        "status": rec["status"],
                        "error": rec["error"],
                        "correlation_id": body.get("correlation_id"),
                    }
                )
            if "suggestions" in body:
                bucket["api"]["suggestions"].append(body.get("suggestions"))
            if "structured_intent" in body:
                rec["structured_intent"] = body.get("structured_intent")
            shared = None
            facets = body.get("facets") if isinstance(body.get("facets"), dict) else None
            if facets:
                shared = facets.get("shared_understanding")
                recs = facets.get("recommendations") or {}
                items = recs.get("items") if isinstance(recs, dict) else recs
                bucket["api"]["last_workspace"] = {
                    "context_version": body.get("context_version"),
                    "shared": shared,
                    "rec_count": len(items or []),
                }
                rec["rec_count"] = len(items or [])
            if rec["path"].endswith("/api/v1/session") and rec["method"] == "POST":
                bucket["api"]["session_mint"] = {
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
        if rec["path"].endswith("/api/v1/shared-understanding") and rec["method"] == "PATCH":
            bucket["api"]["patches"].append(sanitize_post(rec))
        if rec["path"].startswith("/api/") or rec["method"] in (
            "POST",
            "PATCH",
            "PUT",
        ):
            bucket["api"]["posts"].append(sanitize_post(rec))

    page.on("response", on_response)


def dump(page) -> dict:
    return page.evaluate(
        """() => {
          const list = document.querySelector('#understanding-list');
          const err = document.querySelector('#message-form-error');
          const notice = document.querySelector('#notice');
          const correctErr = document.querySelector('#correct-form-error');
          const checkoutErr = document.querySelector('#checkout-form-error, #payment-form-error');
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
          const steps = [...document.querySelectorAll('#journey-steps [data-step]')].map(
            (b) => ({
              step: b.getAttribute('data-step'),
              label: (b.querySelector('.step-label')?.textContent || b.textContent || '').trim(),
              current: b.getAttribute('aria-current') === 'step',
              disabled: !!b.disabled,
            })
          );
          return {
            title: document.title,
            url: location.pathname + location.search,
            understanding: document.querySelector('#understanding')?.innerText,
            listHidden: list ? list.hidden : null,
            listCount: list ? list.children.length : 0,
            formError: err && !err.hidden ? err.innerText : '',
            notice: notice && !notice.hidden ? notice.innerText : '',
            noticeIsError: notice ? notice.classList.contains('is-error') : false,
            correctFormHidden: document.querySelector('#correct-form')?.hidden ?? null,
            correctOpenVisible: !!document.querySelector('#correct-open'),
            correctFormError: correctErr && !correctErr.hidden ? correctErr.innerText : '',
            chips: [...document.querySelectorAll('#suggestions button')].map(
              (b) => b.textContent
            ),
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
            stepper: steps,
            trackStepPresent: steps.some((s) => /track/i.test(s.label)),
            checkoutVisible: !!document.querySelector(
              '#checkout-form, #payment-form, [data-tile="checkout"]'
            ),
            hasCardNumber: !!document.querySelector(
              'input[autocomplete="cc-number"], input[name="card"], input[name="pan"]'
            ),
            checkoutError: checkoutErr && !checkoutErr.hidden ? checkoutErr.innerText : '',
            sessionPayRef: document.querySelector(
              '#session-pay-ref, [data-session-pay-ref]'
            )?.innerText || '',
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
          };
        }"""
    )


def send_and_wait(page, text: str, timeout_ms: int = 20000) -> dict:
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
    return dump(page)


def wait_intent_facets(page, timeout_ms: int = 12000) -> dict:
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
    return dump(page)


def walk_viewport(browser, name: str) -> dict:
    bucket = new_viewport_bucket(name)
    prefix = "d" if name == "desktop" else "p"
    context = browser.new_context(
        ignore_https_errors=False,
        viewport=VIEWPORTS[name],
    )
    page = context.new_page()
    attach_listeners(page, bucket)
    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_selector("#message-form", timeout=25000)
        except Exception as boot_exc:
            page.screenshot(path=str(SHOTS / f"{prefix}00-boot-fail.png"), full_page=True)
            mint = bucket["api"].get("session_mint")
            actual = (
                f"Workspace did not show #message-form. title={page.title()!r} "
                f"url={page.url!r} session_mint={mint} "
                f"boot_exc={type(boot_exc).__name__}: {boot_exc}"
            )
            add_step(
                bucket,
                "Boot / session mint",
                "Customer workspace boots; session mint succeeds so composer is usable",
                actual,
                "fail",
            )
            bucket["notes"].append("Stop: session/boot blocked.")
            bucket["crash"] = actual
            return bucket

        page.wait_for_timeout(2500)
        mint = bucket["api"].get("session_mint")
        if mint and mint.get("status") == 500:
            page.screenshot(path=str(SHOTS / f"{prefix}00-session-500.png"), full_page=True)
            add_step(
                bucket,
                "Boot / session mint",
                "POST /api/v1/session succeeds so the shopper can start",
                f"Session mint HTTP {mint.get('status')} error={mint.get('error')!r}",
                "fail",
            )
            bucket["notes"].append("Stop: session mint 500.")
            return bucket

        boot = dump(page)
        page.screenshot(path=str(SHOTS / f"{prefix}01-landing.png"), full_page=True)
        chips = page.locator("#suggestions button").all_text_contents()
        assistant = page.locator("#messages").inner_text()
        add_step(
            bucket,
            "T-01 Enter / Discovery",
            "Welcome + composer; customer can describe the occasion in own words",
            f"Welcome visible. Assistant: {assistant.strip()[:160]!r}. Chips: {chips}. "
            f"innerWidth={boot.get('innerWidth')}. session_mint={mint}. "
            f"Track stepper present={boot.get('trackStepPresent')}.",
            "pass" if page.locator("#message").is_visible() else "fail",
        )

        after_partial = send_and_wait(page, "I need flowers...")
        chips_after = after_partial.get("chips") or []
        log = page.locator("#messages").inner_text()
        page.screenshot(path=str(SHOTS / f"{prefix}02-partial-thought.png"), full_page=True)
        joined = " ".join(chips_after)
        thought_fail = "for Mom" not in joined and "Mum" not in joined
        thought_result = "fail" if after_partial.get("formError") or thought_fail else "pass"
        add_step(
            bucket,
            "T-01 thought completion (ADR-003)",
            "Partial 'I need flowers…' yields evolving suggestions such as 'for Mom'; chips optional; typing always allowed",
            f"Notice: {after_partial.get('notice')!r}. Chips: {chips_after}. "
            f"Customer line in log: {'I need flowers' in log}. "
            f"formError: {after_partial.get('formError')!r}.",
            thought_result,
        )

        send_and_wait(page, "Birthday flowers for Mum, under $75")
        after_full = wait_intent_facets(page)
        intent_text = after_full.get("understanding") or ""
        page.screenshot(path=str(SHOTS / f"{prefix}03-intent.png"), full_page=True)
        intent_ok = any(
            token in intent_text.lower() for token in ("birthday", "mother", "mum", "75")
        )
        csrf = bucket["api"]["csrf_rejected"]
        form_err = after_full.get("formError") or ""
        add_step(
            bucket,
            "T-01 Conversation Send + T-02 Shared Understanding",
            "Message posts; occasion/recipient/budget appear; Review and correct exists",
            f"Intent panel: {intent_text[:400]!r}. Review and correct: "
            f"{after_full.get('correctOpenVisible')}. csrf_rejected={csrf}. "
            f"formError={form_err!r}. session_required_seen={bucket['api']['session_required']}.",
            "fail" if csrf or form_err or not intent_ok else "pass",
        )

        # --- T-02 Review and correct (the assignment) ---
        patches_before = len(bucket["api"]["patches"])
        if page.locator("#correct-open").count():
            page.locator("#correct-open").scroll_into_view_if_needed()
            page.click("#correct-open")
            page.select_option("#correct-facet", "recipient")
            page.fill("#correct-value", "Mum")
            page.click("#correct-form button[type='submit']")
            try:
                page.wait_for_function(
                    """() => {
                      const n = document.querySelector('#notice');
                      const e = document.querySelector('#correct-form-error');
                      const notice = n && !n.hidden ? (n.textContent || '') : '';
                      const err = e && !e.hidden ? (e.textContent || '') : '';
                      const joined = notice + ' ' + err;
                      if (/Shared Understanding updated/i.test(notice)) return 'ok';
                      if (/Correction failed|session_required/i.test(joined)) return 'fail';
                      const text = document.querySelector('#understanding')?.innerText || '';
                      if (/\\bMum\\b/i.test(text)) return 'ok';
                      return false;
                    }""",
                    timeout=15000,
                )
            except Exception:
                pass
            page.wait_for_timeout(600)
        after_correct = dump(page)
        page.screenshot(path=str(SHOTS / f"{prefix}04-t02-correct.png"), full_page=True)
        patches = bucket["api"]["patches"][patches_before:]
        notice = after_correct.get("notice") or ""
        correct_err = after_correct.get("correctFormError") or ""
        joined_copy = f"{notice} {correct_err}"
        toast_session = (
            "session_required" in joined_copy.lower()
            or "Correction failed (session_required)" in joined_copy
        )
        patch_ok = any(
            (p.get("status") or 0) >= 200 and (p.get("status") or 0) < 300 for p in patches
        )
        patch_401 = any((p.get("status") == 401) or (p.get("error") == "session_required") for p in patches)
        recipient_ok = "mum" in (after_correct.get("understanding") or "").lower()
        t02_fail = toast_session or not patch_ok or not recipient_ok
        bucket["t02"] = {
            "patches": patches,
            "notice": notice,
            "notice_is_error": after_correct.get("noticeIsError"),
            "correct_form_error": correct_err,
            "toast_session_required": toast_session,
            "patch_2xx": patch_ok,
            "patch_session_required_status": patch_401,
            "recipient_shows_mum": recipient_ok,
            "understanding": (after_correct.get("understanding") or "")[:400],
        }
        add_step(
            bucket,
            "T-02 Review and correct",
            "Customer can correct a facet; PATCH /api/v1/shared-understanding succeeds; no toast Correction failed (session_required)",
            f"PATCH responses={patches}. notice={notice!r} correct_form_error={correct_err!r} "
            f"toast_session_required={toast_session} patch_2xx={patch_ok} "
            f"api_session_required={bucket['api']['session_required']}. "
            f"Panel: {(after_correct.get('understanding') or '')[:280]!r}",
            "fail" if t02_fail else "pass",
        )
        if toast_session:
            bucket["notes"].append(
                "Shopper saw Correction failed (session_required) after Save correction."
            )

        def goto_recommendations():
            continue_rec = page.locator("button[data-goto-step='3']")
            step3 = page.locator("#journey-steps button[data-step='3']")
            if continue_rec.count() and continue_rec.first.is_enabled():
                continue_rec.first.click()
            elif step3.count() and step3.first.is_enabled():
                step3.first.click()
            else:
                bucket["notes"].append(f"step 3 still locked: {dump(page)}")
            page.wait_for_timeout(2000)

        goto_recommendations()

        def rec_snapshot():
            snap = dump(page)
            cards = page.locator("#recommendation-cards .card")
            count = cards.count()
            copy = [
                cards.nth(i).inner_text().replace("\n", " | ") for i in range(count)
            ]
            return count, copy, snap, snap.get("availabilityBadges") or []

        card_count, card_copy, snap, badges = rec_snapshot()
        available = any("Available" in (c or "") for c in card_copy) or any(
            (b.get("badge") or "") == "Available" for b in badges
        )
        select_enabled = int(snap.get("selectEnabledCount") or 0)
        if not available and select_enabled == 0:
            bucket["notes"].append(
                "T-03 first look: no Available badge / Select disabled. "
                "Waiting one 30s heartbeat cycle."
            )
            page.screenshot(
                path=str(SHOTS / f"{prefix}05-recommendations-unknown.png"), full_page=True
            )
            page.wait_for_timeout(35000)
            goto_recommendations()
            card_count, card_copy, snap, badges = rec_snapshot()
            available = any("Available" in (c or "") for c in card_copy) or any(
                (b.get("badge") or "") == "Available" for b in badges
            )
            select_enabled = int(snap.get("selectEnabledCount") or 0)

        bucket["api"]["select_enabled"] = select_enabled > 0
        bucket["api"]["availability_badges"] = badges
        page.screenshot(path=str(SHOTS / f"{prefix}05-recommendations.png"), full_page=True)
        if card_count == 0 or not available or select_enabled == 0:
            t03 = "fail"
        else:
            t03 = "pass"
        add_step(
            bucket,
            "T-03 Curated Recommendations",
            "Validated options matching birthday / Mum / budget; available options selectable",
            f"Caption: {snap.get('stepCaption')!r}. Cards ({card_count}): {card_copy}. "
            f"badges={badges}. select_enabled={select_enabled}.",
            t03,
        )

        select_btns = page.locator(
            "#recommendation-cards button.primary:not([disabled])"
        )
        if select_btns.count() == 0:
            add_step(
                bucket,
                "T-04 Select + customize",
                "Select an available arrangement; size; physical card message",
                f"No enabled Select button. card_count={card_count} copy={card_copy}",
                "fail",
            )
            add_step(
                bucket,
                "T-05 Delivery",
                "Date + named window; confirm saved destination reference",
                "Not reached: Select stayed disabled.",
                "blocked",
            )
            add_step(
                bucket,
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
            page.screenshot(path=str(SHOTS / f"{prefix}06-customize.png"), full_page=True)
            arrangement = (
                page.locator("#arrangement").input_value()
                if page.locator("#arrangement").count()
                else ""
            )
            add_step(
                bucket,
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
            page.screenshot(path=str(SHOTS / f"{prefix}07-delivery.png"), full_page=True)
            add_step(
                bucket,
                "T-05 Delivery",
                "Date + named window; confirm saved destination reference (not a street address)",
                f"Date {DELIVERY_DATE}, window morning, destination ref {dest_ref!r}. "
                f"Street-address fields={street.count()}. Banner={banner_text!r} "
                f"error={err!r} csrf={bucket['api']['csrf_rejected']}",
                "fail"
                if street.count()
                or bucket["api"]["csrf_rejected"]
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
            after_summary = dump(page)
            page.screenshot(path=str(SHOTS / f"{prefix}08-summary.png"), full_page=True)
            has_total = "Total" in summary or "total" in summary.lower()
            mismatch_copy = (
                "total_mismatch" in (after_summary.get("checkoutError") or "").lower()
                or "total_mismatch" in (after_summary.get("notice") or "").lower()
                or "Checkout failed (total_mismatch)" in (
                    (after_summary.get("notice") or "")
                    + (after_summary.get("checkoutError") or "")
                )
            )
            if mismatch_copy:
                bucket["api"]["total_mismatch"] = True
                report["notes"].append(
                    f"{name}: Checkout failed (total_mismatch) visible on summary/checkout chrome "
                    "(observe only — Support intake)."
                )
            add_step(
                bucket,
                "T-06 Order Summary",
                "Itemized charges update after selection and delivery",
                f"Summary panel: {summary[:500]!r} checkoutError={after_summary.get('checkoutError')!r} "
                f"total_mismatch={bucket['api']['total_mismatch']}",
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
            add_step(
                bucket,
                "T-07 Checkout",
                "Stop before payment; do not Place Order",
                f"Checkout controls visible={checkout_visible}. PAN fields={has_pan}. "
                f"session pay ref present={bool(pay_ref)}. "
                f"total_mismatch={bucket['api']['total_mismatch']}. Default skip Place Order.",
                "blocked",
            )

        if not any(s["tile"].startswith("T-07") for s in bucket["steps"]):
            add_step(
                bucket,
                "T-07 Checkout",
                "Stop before payment unless asked",
                "Did not reach checkout. Payment not included. Did not Place Order.",
                "blocked",
            )
        add_step(
            bucket,
            "T-08 Tracking",
            "Tracking after confirmed order",
            f"Skipped with payment. Track stepper present={dump(page).get('trackStepPresent')}.",
            "blocked",
        )

        if name == "desktop" and (
            page.locator("button.aso").count() or page.locator("button.help-button").count()
        ):
            help_btn = (
                page.locator("button.aso")
                if page.locator("button.aso").count()
                else page.locator("button.help-button")
            )
            help_btn.first.click()
            page.wait_for_timeout(400)
            help_copy = (
                page.locator("#help").inner_text() if page.locator("#help").count() else ""
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
            page.screenshot(path=str(SHOTS / f"{prefix}09-help.png"), full_page=True)
            not_a_person = "not a person" in help_copy.lower() or "Automated" in help_copy
            add_step(
                bucket,
                "ASO Help",
                "Help available without leaving the workspace; labeled as not a person",
                f"Help dialog: {help_copy[:280]!r}. Answer: {answer!r}.",
                "pass" if not_a_person else "fail",
            )
            if page.locator("[data-close-help]").count():
                page.click("[data-close-help]")

        bucket["workspace"] = dump(page)
        page.screenshot(path=str(SHOTS / f"{prefix}10-final.png"), full_page=True)
    except Exception as exc:
        bucket["crash"] = f"{type(exc).__name__}: {exc}"
        try:
            page.screenshot(path=str(SHOTS / f"{prefix}-crash.png"), full_page=True)
        except Exception:
            pass
    finally:
        # New context per viewport so cookies never mix; never hit /florist.
        try:
            context.close()
        except Exception:
            pass
    bucket["api"]["status_codes"] = bucket["api"]["status_codes"][:80]
    return bucket


def main() -> int:
    try:
        report["healthz"] = probe_healthz()
    except Exception as exc:
        report["healthz"] = {"error": f"{type(exc).__name__}: {exc}"}
        report["notes"].append("healthz probe failed.")
        report["first_blocker"] = {
            "tile": "healthz",
            "actual": str(report["healthz"]),
            "result": "blocked",
        }
        OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({"wrote": str(OUT), "healthz": report["healthz"]}, indent=2))
        return 0

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
        try:
            for name in ("desktop", "phone"):
                report["viewports"][name] = walk_viewport(browser, name)
        finally:
            try:
                browser.close()
            except Exception:
                pass

    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary = {
        "wrote": str(OUT),
        "healthz": report.get("healthz"),
        "florist_opened": report.get("florist_opened"),
        "first_blocker": report.get("first_blocker"),
        "notes": report.get("notes"),
        "viewports": {},
    }
    for name, bucket in report["viewports"].items():
        summary["viewports"][name] = {
            "results": [
                {"tile": s["tile"], "result": s["result"]} for s in bucket["steps"]
            ],
            "t02": bucket.get("t02"),
            "session_mint": bucket["api"].get("session_mint"),
            "csrf": bucket["api"].get("csrf_rejected"),
            "session_required": bucket["api"].get("session_required"),
            "total_mismatch": bucket["api"].get("total_mismatch"),
            "select_enabled": bucket["api"].get("select_enabled"),
            "auth_errors": bucket["api"].get("auth_errors"),
            "crash": bucket.get("crash"),
            "notes": bucket.get("notes"),
        }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
