"""Tablet-only Path B rewalk after !224 is on the live image.

URL: https://aea.artof.link/  (ACM TLS — do not ignore certificate errors)
Confirm Conversation left of Intent Summary at 768 and 900.
Brief T-01…T-03. Payment / T-07 skipped. Do not open /florist.
If tablet is still one column T-01 above T-02, score product fail (image is current).
"""
from __future__ import annotations

import json
import ssl
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://aea.artof.link/"
ORIGIN = "https://aea.artof.link"
OUT = Path(__file__).with_name("2026-08-17-mother-birthday-tablet-rewalk.json")
SHOTS = Path(__file__).with_name("_walk_shots_tablet_rewalk")
SHOTS.mkdir(exist_ok=True)

LAYOUT_JS = """() => {
  const conv = document.querySelector('#conversation');
  const und = document.querySelector('#understanding');
  const main = document.querySelector('main.workspace');
  if (!conv || !und || !main) return { missing: true };
  const cr = conv.getBoundingClientRect();
  const ur = und.getBoundingClientRect();
  const cs = getComputedStyle(main);
  const vh = window.innerHeight;
  const sameRow = Math.abs(cr.top - ur.top) < 80;
  const sameCol = Math.abs(cr.left - ur.left) < 80;
  const t01LeftOfT02 = cr.left < ur.left - 8 && sameRow;
  const t01AboveT02 = cr.top < ur.top - 8 && sameCol;
  const cols = (cs.gridTemplateColumns || '').trim().split(/\\s+/).filter(Boolean);
  const inFirst = (r) => r.top < vh && r.bottom > 0;
  return {
    viewport: { w: window.innerWidth, h: window.innerHeight },
    conversation: {
      top: Math.round(cr.top),
      left: Math.round(cr.left),
      width: Math.round(cr.width),
      height: Math.round(cr.height),
      bottom: Math.round(cr.bottom),
    },
    understanding: {
      top: Math.round(ur.top),
      left: Math.round(ur.left),
      width: Math.round(ur.width),
      height: Math.round(ur.height),
      bottom: Math.round(ur.bottom),
    },
    gridTemplateColumns: cs.gridTemplateColumns,
    gridTemplateAreas: cs.gridTemplateAreas,
    conversationOrder: getComputedStyle(conv).order,
    understandingOrder: getComputedStyle(und).order,
    t01LeftOfT02,
    t01AboveT02,
    columnTokenCount: cols.length,
    conversationInFirstViewport: inFirst(cr),
    understandingInFirstViewport: inFirst(ur),
    bothInFirstViewport: inFirst(cr) && inFirst(ur),
  };
}"""

report: dict = {
    "url": URL,
    "scenario": "mother-birthday",
    "payment_included": False,
    "origin": ORIGIN,
    "assignment": (
        "Tablet-only rewalk after !224 deployed; T-01 left of T-02 at 768/900; "
        "product fail if still stacked"
    ),
    "origin_main": "c9c5c0b",
    "mr": "!224",
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
    "workspace": {},
    "notes": [],
    "first_blocker": None,
    "deployed_224": None,
    "cursor_ide_browser": "no tab available; Playwright fallback",
}


def step(tile: str, expected: str, actual: str, result: str) -> None:
    report["steps"].append(
        {"tile": tile, "expected": expected, "actual": actual, "result": result}
    )
    if result == "fail" and report["first_blocker"] is None:
        report["first_blocker"] = {"tile": tile, "actual": actual, "result": result}


def sanitize_post(rec: dict) -> dict:
    keep = {
        "path": rec.get("path"),
        "status": rec.get("status"),
        "method": rec.get("method"),
        "error": rec.get("error"),
        "code": rec.get("code"),
    }
    if rec.get("rec_count") is not None:
        keep["rec_count"] = rec["rec_count"]
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
    info["looks_like_224"] = bool(
        info["has_siblings_comment"]
        and info["has_tablet_two_col_areas"]
        and not info["has_order_minus_1"]
    )
    return info


def main() -> int:
    try:
        report["live_css"] = fetch_live_css()
        report["deployed_224"] = bool(report["live_css"].get("looks_like_224"))
        if report["deployed_224"]:
            report["notes"].append(
                "Live /assets/styles.css matches !224 (sibling two-col tablet, no order:-1)."
            )
        else:
            report["notes"].append(
                "Live CSS markers do not match !224; PM said image is current — "
                "layout still scored as product, not deploy lag."
            )
    except Exception as css_exc:
        report["notes"].append(
            f"live CSS fetch failed: {type(css_exc).__name__}: {css_exc}"
        )

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
            viewport={"width": 768, "height": 1024},
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
                    hasCardNumber: !!document.querySelector(
                      'input[autocomplete="cc-number"], input[name="card"], input[name="pan"]'
                    ),
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

        def measure(label: str) -> dict:
            geo = page.evaluate(LAYOUT_JS)
            report["tablet_layout"][label] = geo
            return geo

        def score_tablet(geo: dict) -> tuple[str, str]:
            left = bool(geo.get("t01LeftOfT02"))
            stacked = bool(geo.get("t01AboveT02"))
            both = bool(geo.get("bothInFirstViewport"))
            if left and both:
                return (
                    "pass",
                    "Conversation sits left of Intent Summary in the first viewport.",
                )
            if left and not both:
                return (
                    "fail",
                    "T-01 is left of T-02 but Intent Summary is not in the first viewport.",
                )
            if stacked:
                return (
                    "fail",
                    "Tablet is one column with Conversation stacked above Intent Summary. "
                    "Image is current (!224 CSS live) — product fail, not deploy lag.",
                )
            return (
                "fail",
                "Tablet layout is neither two-column left-of nor a clean one-column stack.",
            )

        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            try:
                page.wait_for_selector("#message-form", timeout=25000)
            except Exception as boot_exc:
                page.screenshot(path=str(SHOTS / "00-boot-fail.png"), full_page=True)
                mint = report["api"].get("session_mint")
                actual = (
                    f"Workspace did not show #message-form. "
                    f"title={page.title()!r} url={page.url!r} "
                    f"session_mint={mint} boot_exc={type(boot_exc).__name__}: {boot_exc}"
                )
                step(
                    "Boot / session mint",
                    "Customer workspace boots; session mint succeeds so composer is usable",
                    actual,
                    "fail",
                )
                report["notes"].append("Stop: session/boot blocked.")
                raise SystemExit(0)

            page.wait_for_timeout(2500)
            mint = report["api"].get("session_mint")
            report["boot"] = dump()
            page.evaluate("window.scrollTo(0, 0)")
            geo_768 = measure("768x1024-landing")
            page.screenshot(path=str(SHOTS / "01-tablet-768-first-viewport.png"))
            page.screenshot(path=str(SHOTS / "01-tablet-768-full.png"), full_page=True)
            result_768, note_768 = score_tablet(geo_768)
            step(
                "Tablet 768 T-01 left of T-02",
                "At 768px, Conversation is left of Intent Summary in the first viewport, not stacked above",
                f"{note_768} geo={geo_768} live_css={report.get('live_css')}",
                result_768,
            )

            page.set_viewport_size({"width": 900, "height": 1024})
            page.wait_for_timeout(400)
            page.evaluate("window.scrollTo(0, 0)")
            geo_900 = measure("900x1024-landing")
            page.screenshot(path=str(SHOTS / "02-tablet-900-first-viewport.png"))
            page.screenshot(path=str(SHOTS / "02-tablet-900-full.png"), full_page=True)
            result_900, note_900 = score_tablet(geo_900)
            step(
                "Tablet 900 T-01 left of T-02",
                "At 900px, Conversation is left of Intent Summary in the first viewport, not stacked above",
                f"{note_900} geo={geo_900}",
                result_900,
            )

            page.set_viewport_size({"width": 768, "height": 1024})
            page.wait_for_timeout(300)

            chips = page.locator("#suggestions button").all_text_contents()
            assistant = page.locator("#messages").inner_text()
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
            page.screenshot(path=str(SHOTS / "03-partial-thought-768.png"))
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
            page.evaluate("window.scrollTo(0, 0)")
            geo_after = measure("768x1024-after-intent")
            page.screenshot(path=str(SHOTS / "04-intent-768-first-viewport.png"))
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
            after_result, after_note = score_tablet(geo_after)
            step(
                "Tablet 768 T-01 left of T-02 after intent",
                "Two-column tablet layout still holds after Shared Understanding fills",
                f"{after_note} geo={geo_after}",
                after_result,
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

            snap = dump()
            badges = snap.get("availabilityBadges") or []
            select_enabled = int(snap.get("selectEnabledCount") or 0)
            report["api"]["select_enabled"] = select_enabled > 0
            report["api"]["availability_badges"] = badges
            page.screenshot(path=str(SHOTS / "05-recommendations-768.png"), full_page=True)
            empty_copy = ""
            if page.locator("#recommendation-empty, #recommendations").count():
                empty_copy = page.locator(
                    "#recommendation-empty, #recommendations"
                ).inner_text()
            cards = snap.get("cards") or []
            rec_ok = select_enabled > 0 or any(
                (b.get("badge") or "") == "Available" for b in badges
            )
            step(
                "T-03 Curated Recommendations",
                "Validated options matching birthday / Mum / budget; available options selectable",
                f"Cards ({len(cards)}): {cards}. badges={badges}. "
                f"select_enabled={select_enabled}. empty={empty_copy[:240]!r}.",
                "pass" if rec_ok else "fail",
            )

            step(
                "T-04…T-06 Customize / delivery / summary",
                "Optional on this tablet-only rewalk",
                "Skipped. Full mother-birthday through T-06 not required.",
                "blocked",
            )
            step(
                "T-07 Checkout",
                "Stop before payment unless asked",
                "Payment skipped.",
                "blocked",
            )
            step(
                "T-08 Tracking",
                "Tracking after confirmed order",
                "Skipped with payment.",
                "blocked",
            )

            report["workspace"] = dump()
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
                "deployed_224": report.get("deployed_224"),
                "tablet_layout": report.get("tablet_layout"),
                "first_blocker": report.get("first_blocker"),
                "notes": report.get("notes"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
