#!/usr/bin/env python3
"""
M15 Edge SSR & Performance Audit Runner

Measures Time-to-First-Byte (TTFB), Nginx pre-rendered HTML DOM structure presence,
and edge response latency. Distinguishes network TTFB from full browser LCP.
"""
import urllib.request, ssl, time, json, sys, os
from pathlib import Path

def audit_lcp(target_url=None):
    if not target_url:
        target_url = os.environ.get("AEA_AUDIT_URL", "https://aea.artof.link/")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"=== M15 EDGE SSR & PERFORMANCE AUDIT ===")
    print(f"Target Endpoint: {target_url}\n")

    t0 = time.time()
    try:
        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "AEA-Performance-Auditor/1.0", "Accept-Encoding": "gzip, deflate"}
        )
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        t_first_byte = (time.time() - t0) * 1000
        html = res.read().decode('utf-8', errors='ignore')
        t_total = (time.time() - t0) * 1000

        # Check for pre-rendered SSR markers in HTML payload
        t01_present = "tile-t01" in html or "conversation-container" in html or 'class="tile"' in html
        t02_present = "tile-t02" in html or "intent-summary" in html or "shared-understanding" in html

        print(f"  [1] Time to First Byte (TTFB):            {t_first_byte:.2f} ms")
        print(f"  [2] Total HTML Transfer Time:            {t_total:.2f} ms")
        print(f"  [3] Initial Payload Size:               {len(html)} bytes")
        print(f"  [4] Tile T-01 Pre-Rendered DOM Structure: {'PRESENT (PASS)' if t01_present else 'ABSENT (FAIL)'}")
        print(f"  [5] Tile T-02 Pre-Rendered DOM Structure: {'PRESENT (PASS)' if t02_present else 'ABSENT (FAIL)'}")

        # Honest Performance Evaluation
        # Note: Network TTFB represents the edge delivery floor; full Web Vitals LCP requires headless Chrome paint timing.
        grade = "EXCELLENT (< 100ms)" if t_first_byte < 100 else ("GOOD (< 200ms)" if t_first_byte < 200 else "NEEDS OPTIMIZATION")
        print(f"\n  [NETWORK TTFB FLOOR]: {t_first_byte:.2f} ms -> Grade: {grade}")
        print(f"  [NOTE]: Full LCP paint timing requires Chrome DevTools MCP browser trace.")

        return {
            "status": "PASS" if (t01_present and t02_present and t_first_byte < 250) else "WARN",
            "ttfb_ms": t_first_byte,
            "total_ms": t_total,
            "payload_bytes": len(html),
            "t01_ssr": t01_present,
            "t02_ssr": t02_present
        }

    except Exception as e:
        print(f"FAILED to query endpoint: {e}")
        return {"status": "FAIL", "error": str(e)}

if __name__ == "__main__":
    result = audit_lcp()
    if result["status"] == "FAIL":
        sys.exit(1)


def export_browser_lcp_trace_json(metrics: dict) -> Path:
    import json
    out_dir = Path('research/assessments')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'lcp_performance_trace.json'
    out_path.write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    return out_path
