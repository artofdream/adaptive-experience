"""Path B rewalk after merged !224 (tablet T-01 left of T-02; mobile T-01 above T-02).

URL: https://aea.artof.link/  (ACM TLS — do not ignore certificate errors)
Mother-birthday T-01…T-06. Payment / T-07 Place Order skipped.
Do not open /florist.
If tablet layout matches the pre-!224 CSS, record not-yet-deployed (not a product fail).
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
OUT = Path(__file__).with_name("2026-08-17-mother-birthday-tablet-t01-t02.json")
SHOTS = Path(__file__).with_name("_walk_shots_tablet_224")
SHOTS.mkdir(exist_ok=True)

TODAY = date.today()
DELIVERY_DATE = (TODAY + timedelta(days=7)).isoformat()

LAYOUT_JS = """() => {
  const conv = document.querySelector('#conversation');
  const und = document.querySelector('#understanding');
  const main = document.querySelector('main.workspace');
  if (!conv || !und || !main) return { missing: true };
  const cr = conv.getBoundingClientRect();
  const ur = und.getBoundingClientRect();
  const cs = getComputedStyle(main);
  const sameRow = Math.abs(cr.top - ur.top) < 80;
  const sameCol = Math.abs(cr.left - ur.left) < 80;
  const t01LeftOfT02 = cr.left < ur.left - 8 && sameRow;
  const t01AboveT02 = cr.top < ur.top - 8 && sameCol;
  const cols = (cs.gridTemplateColumns || '').trim().split(/\\s+/).filter(Boolean);
  return {
    viewport: { w: window.innerWidth, h: window.innerHeight },
    conversation: {
      top: Math.round(cr.top),
      left: Math.round(cr.left),
      width: Math.round(cr.width),
      height: Math.round(cr.height),
    },
    understanding: {
      top: Math.round(ur.top),
      left: Math.round(ur.left),
      width: Math.round(ur.width),
      height: Math.round(ur.height),
    },
    gridTemplateColumns: cs.gridTemplateColumns,
    gridTemplateAreas: cs.gridTemplateAreas,
    conversationOrder: getComputedStyle(conv).order,
    understandingOrder: getComputedStyle(und).order,
    t01LeftOfT02,
    t01AboveT02,
    columnTokenCount: cols.length,
  };
}"""

report: dict = {
    "url": URL,
    "scenario": "mother-birthday",
    "payment_included": False,
    "origin": ORIGIN,
    "assignment": "Path B rewalk after !224 tablet T-01 left of T-02; mobile T-01 above T-02",
    "origin_main": "c9c5c0b",
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
    "live_css": {},
    "tablet_layout": {},
    "mobile_layout": {},
    "workspace": {},
    "notes": [],
    "first_blocker": None,
    "deployed_224": None,
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


def fetch_live_css() -> dict:
    ctx = ssl.create_default_context()
    css = urllib.request.urlopen(
        f"{ORIGIN}/assets/styles.css", context=ctx, timeout=20
    ).read().decode("utf-8", errors="replace")
    info = {
        "bytes": len(css),
        "has_siblings_comment": "workspace siblings" in css,
        "has_order_minus_1": "order: -1" in css or "order:-1" in css,
        "has_tablet_two_col_areas": '"conversation understanding"' in css
        and "main main" in css,
        "has_mobile_stack_areas": '"conversation"' in css
        and '"understanding"' in css,
        "tablet_rule_excerpt": "",
    }
    start = css.find("@media (max-width: 60rem)")
    if start >= 0:
        info["tablet_rule_excerpt"] = css[start : start + 420]
    # Deployed iff the sibling-grid tablet rule is present (origin/main 1a9fd24 / !224).
    info["looks_like_224"] = bool(
        info["has_siblings_comment"] and info["has_tablet_two_col_areas"]
    )
    return info


def main() -> int:
    try:
        report["live_css"] = fetch_live_css()
        report["deployed_224"] = bool(report["live_css"].get("looks_like_224"))
        if not report["deployed_224"]:
            report["notes"].append(
                "Live /assets/styles.css still has pre-!224 tablet rule "
                "(.understanding { order: -1 } + one column). origin/main c9c5c0b "
                "is not on this Path B image yet."
            )
    except Exception as css_exc:
        report["notes"].append(f"live CSS fetch failed: {type(css_exc).__name__}: {css_exc}")

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
            unknown = any("Unknown" in (b.get("badge") or "") for b in badges)
            if card_count == 0:
                t03 = "fail"
                report["notes"].append("T-03 empty: no ranked cards after intent.")
            elif not available or select_enabled == 0:
                t03 = "fail"
            else:
                t03 = "pass"
            step(
                "T-03 Curated Recommendations",
                "Validated options matching birthday / Mum / budget; available options selectable",
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
                    "Date + named window; confirm saved destination reference",
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
                    "ASO Help",
                    "Help available without leaving the workspace; labeled as not a person",
                    f"Help dialog: {help_copy[:280]!r}. Answer: {answer!r}.",
                    "pass" if not_a_person else "fail",
                )
                if page.locator("[data-close-help]").count():
                    page.click("[data-close-help]")
                    page.wait_for_timeout(300)
            else:
                step(
                    "ASO Help",
                    "Help available without leaving the workspace; labeled as not a person",
                    "Desktop ? FAB not found after walk.",
                    "fail",
                )

            # --- !224 layout: tablet 768 then 900; mobile 390 ---
            def measure(width: int, height: int, shot_name: str) -> dict:
                page.set_viewport_size({"width": width, "height": height})
                page.wait_for_timeout(500)
                geo = page.evaluate(LAYOUT_JS)
                page.screenshot(path=str(SHOTS / shot_name), full_page=True)
                return geo

            tablet_768 = measure(768, 1024, "09-tablet-768.png")
            tablet_900 = measure(900, 1024, "10-tablet-900.png")
            mobile_390 = measure(390, 844, "11-mobile-390.png")
            report["tablet_layout"] = {"768x1024": tablet_768, "900x1024": tablet_900}
            report["mobile_layout"] = {"390x844": mobile_390}

            deployed = bool(report.get("deployed_224"))
            tablet_left = bool(tablet_768.get("t01LeftOfT02")) and bool(
                tablet_900.get("t01LeftOfT02")
            )
            tablet_still_stacked = bool(tablet_768.get("t01AboveT02"))
            if deployed and tablet_left:
                tablet_result = "pass"
                tablet_note = "Live CSS matches !224; T-01 sits left of T-02 at tablet widths."
            elif not deployed and tablet_still_stacked:
                tablet_result = "blocked"
                tablet_note = (
                    "Tablet layout unchanged from pre-!224 (T-01 stacked above T-02, "
                    "one workspace column). Live CSS still has `.understanding { order: -1 }` "
                    "and `grid-template-columns: 1fr` at 60rem. origin/main c9c5c0b is "
                    "not-yet-deployed on Path B — not scored as a product fail."
                )
                report["notes"].append("Tablet !224 not-yet-deployed (not a product fail).")
            elif deployed and not tablet_left:
                tablet_result = "fail"
                tablet_note = (
                    "Live CSS looks like !224 but T-01 is not left of T-02 at tablet width."
                )
            else:
                tablet_result = "fail"
                tablet_note = (
                    "Tablet layout does not match !224 and CSS markers are inconclusive."
                )
            step(
                "Tablet T-01 left of T-02 (!224)",
                "At 641–960px, Conversation (T-01) stays left of Intent Summary (T-02); tiles span below",
                f"{tablet_note} 768={tablet_768} 900={tablet_900} live_css={report.get('live_css')}",
                tablet_result,
            )

            mobile_above = bool(mobile_390.get("t01AboveT02"))
            step(
                "Mobile T-01 above T-02 (!224)",
                "Through 640px, one-column reading order: T-01 Conversation above T-02 Intent Summary",
                f"t01AboveT02={mobile_above}. geo={mobile_390}",
                "pass" if mobile_above else "fail",
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
                "deployed_224": report.get("deployed_224"),
                "tablet_layout": report.get("tablet_layout"),
                "mobile_layout": report.get("mobile_layout"),
                "live_css": {
                    k: report.get("live_css", {}).get(k)
                    for k in (
                        "bytes",
                        "looks_like_224",
                        "has_siblings_comment",
                        "has_order_minus_1",
                        "has_tablet_two_col_areas",
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
