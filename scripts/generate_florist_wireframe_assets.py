#!/usr/bin/env python3
"""Generate grayscale Lily's Florist wireframe SVGs and reusable assets."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIREFRAMES = ROOT / "implementations" / "florist" / "wireframes"

# Low-fidelity grayscale tokens (UX guide)
G = {
    "bg": "#FFFFFF",
    "bg-muted": "#F5F5F5",
    "bg-soft": "#EEEEEE",
    "border": "#CFCFCF",
    "border-strong": "#9A9A9A",
    "text": "#222222",
    "text-sec": "#666666",
    "text-muted": "#888888",
    "fill": "#D9D9D9",
    "fill-dark": "#4A4A4A",
    "ok": "#6B6B6B",
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def icon_svg(name: str, paths: str, size: int = 24) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" role="img" aria-label="{name}">
  {paths}
</svg>'''


ICONS = {
    "icon-ai-concierge.svg": icon_svg(
        "AI Floral Concierge",
        f'''<rect x="5" y="7" width="14" height="12" rx="3" stroke="{G['text']}" stroke-width="1.5"/>
  <circle cx="9.5" cy="12" r="1.2" fill="{G['text']}"/>
  <circle cx="14.5" cy="12" r="1.2" fill="{G['text']}"/>
  <path d="M9 15.5h6" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M12 3v3M8 4.5l1.5 2M16 4.5l-1.5 2" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round"/>''',
    ),
    "icon-bouquet.svg": icon_svg(
        "Bouquet",
        f'''<path d="M12 14c-3-4-6-5-6-8a3 3 0 0 1 6 0 3 3 0 0 1 6 0c0 3-3 4-6 8Z" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M12 14v7M10 21h4" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round"/>''',
    ),
    "icon-truck.svg": icon_svg(
        "Delivery truck",
        f'''<path d="M3 7h11v9H3V7Z" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M14 10h4l3 3v3h-7v-6Z" stroke="{G['text']}" stroke-width="1.5"/>
  <circle cx="7" cy="18" r="1.5" stroke="{G['text']}" stroke-width="1.5"/>
  <circle cx="17" cy="18" r="1.5" stroke="{G['text']}" stroke-width="1.5"/>''',
    ),
    "icon-location.svg": icon_svg(
        "Location pin",
        f'''<path d="M12 21s-6-5.2-6-10a6 6 0 1 1 12 0c0 4.8-6 10-6 10Z" stroke="{G['text']}" stroke-width="1.5"/>
  <circle cx="12" cy="11" r="2" stroke="{G['text']}" stroke-width="1.5"/>''',
    ),
    "icon-credit-card.svg": icon_svg(
        "Credit card",
        f'''<rect x="2.5" y="5.5" width="19" height="13" rx="2" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M2.5 10h19" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M6 15h4" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round"/>''',
    ),
    "icon-lock.svg": icon_svg(
        "Lock",
        f'''<rect x="5" y="11" width="14" height="9" rx="2" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M8 11V8a4 4 0 0 1 8 0v3" stroke="{G['text']}" stroke-width="1.5"/>
  <circle cx="12" cy="15.5" r="1" fill="{G['text']}"/>''',
    ),
    "icon-checkmark.svg": icon_svg(
        "Checkmark",
        f'''<circle cx="12" cy="12" r="8.5" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M8 12.5l2.5 2.5L16 9.5" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>''',
    ),
    "icon-clock.svg": icon_svg(
        "Clock",
        f'''<circle cx="12" cy="12" r="8.5" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M12 7.5V12l3 2" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round"/>''',
    ),
    "icon-send.svg": icon_svg(
        "Send",
        f'''<path d="M4 12l16-7-7 16-2.5-6.5L4 12Z" stroke="{G['text']}" stroke-width="1.5" stroke-linejoin="round"/>''',
    ),
    "icon-help.svg": icon_svg(
        "Help / ASO",
        f'''<circle cx="12" cy="12" r="8.5" stroke="{G['text']}" stroke-width="1.5"/>
  <path d="M9.5 9.5a2.5 2.5 0 1 1 3.8 2.1c-.7.5-1.3 1-1.3 2" stroke="{G['text']}" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="12" cy="16.5" r="0.9" fill="{G['text']}"/>''',
    ),
}


def chrome_header() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="56" viewBox="0 0 1200 56" role="img" aria-label="Header bar">
  <rect width="1200" height="56" fill="{G['bg']}" stroke="{G['border']}"/>
  <text x="24" y="34" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" fill="{G['text']}">Lily's Florist</text>
  <text x="1040" y="34" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{G['text-sec']}">Orders</text>
  <text x="1120" y="34" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{G['text-sec']}">Help</text>
</svg>'''


def chrome_chat_bubbles() -> tuple[str, str]:
    user = f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="64" viewBox="0 0 280 64" role="img" aria-label="User chat bubble">
  <rect x="40" y="4" width="236" height="56" rx="12" fill="{G['fill-dark']}"/>
  <text x="56" y="28" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['bg']}">User message</text>
  <text x="56" y="46" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['fill']}">Preference / intent text</text>
</svg>'''
    assistant = f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="72" viewBox="0 0 280 72" role="img" aria-label="Assistant chat bubble">
  <circle cx="18" cy="24" r="12" fill="{G['fill']}" stroke="{G['border-strong']}"/>
  <rect x="40" y="4" width="236" height="64" rx="12" fill="{G['bg-muted']}" stroke="{G['border']}"/>
  <text x="56" y="28" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">AI Floral Concierge</text>
  <text x="56" y="46" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">Assistant response</text>
</svg>'''
    return user, assistant


def chrome_input() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="48" viewBox="0 0 360 48" role="img" aria-label="Chat input">
  <rect x="1" y="1" width="358" height="46" rx="23" fill="{G['bg']}" stroke="{G['border-strong']}"/>
  <text x="20" y="29" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{G['text-muted']}">Type your message...</text>
  <circle cx="332" cy="24" r="14" fill="{G['fill-dark']}"/>
  <path d="M326 24l10-5-4 10-1.5-4L326 24Z" fill="{G['bg']}"/>
</svg>'''


def chrome_badge() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="88" height="24" viewBox="0 0 88 24" role="img" aria-label="Available badge">
  <rect width="88" height="24" rx="12" fill="{G['bg-soft']}" stroke="{G['border-strong']}"/>
  <circle cx="12" cy="12" r="4" fill="{G['ok']}"/>
  <text x="22" y="16" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Available</text>
</svg>'''


def chrome_button() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="140" height="40" viewBox="0 0 140 40" role="img" aria-label="Primary button">
  <rect width="140" height="40" rx="8" fill="{G['fill-dark']}"/>
  <text x="70" y="25" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['bg']}">Primary action</text>
</svg>'''


def tile_frame() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="320" height="220" viewBox="0 0 320 220" role="img" aria-label="Tile frame">
  <rect width="320" height="220" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="0" y="0" width="320" height="36" rx="12" fill="{G['bg-muted']}"/>
  <rect x="0" y="24" width="320" height="12" fill="{G['bg-muted']}"/>
  <text x="16" y="24" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="{G['text']}">T-0X Tile title</text>
  <rect x="16" y="56" width="288" height="12" rx="2" fill="{G['fill']}"/>
  <rect x="16" y="80" width="220" height="12" rx="2" fill="{G['bg-soft']}"/>
  <rect x="16" y="104" width="256" height="12" rx="2" fill="{G['bg-soft']}"/>
  <rect x="16" y="160" width="120" height="36" rx="8" fill="{G['fill-dark']}"/>
</svg>'''


def product_card() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="260" viewBox="0 0 200 260" role="img" aria-label="Product card">
  <rect width="200" height="260" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="12" y="12" width="176" height="120" rx="8" fill="{G['fill']}"/>
  <text x="12" y="156" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">Product name</text>
  <text x="12" y="178" font-family="Arial, Helvetica, sans-serif" font-size="13" fill="{G['text']}">$0.00</text>
  <rect x="12" y="190" width="88" height="22" rx="11" fill="{G['bg-soft']}" stroke="{G['border-strong']}"/>
  <text x="28" y="205" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Available</text>
  <rect x="12" y="222" width="176" height="28" rx="6" fill="{G['fill-dark']}"/>
  <text x="100" y="240" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['bg']}">Select</text>
</svg>'''


def order_summary() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="280" height="180" viewBox="0 0 280 180" role="img" aria-label="Order summary">
  <rect width="280" height="180" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
  <text x="16" y="28" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">Order Summary</text>
  <text x="16" y="60" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Arrangement</text>
  <text x="230" y="60" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$125.00</text>
  <text x="16" y="84" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Delivery</text>
  <text x="230" y="84" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$12.00</text>
  <text x="16" y="108" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Tax</text>
  <text x="230" y="108" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$0.50</text>
  <line x1="16" y1="124" x2="264" y2="124" stroke="{G['border']}"/>
  <text x="16" y="150" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" fill="{G['text']}">Total</text>
  <text x="230" y="150" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" fill="{G['text']}">$137.50</text>
</svg>'''


def tracking_timeline() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="200" viewBox="0 0 240 200" role="img" aria-label="Tracking timeline">
  <rect width="240" height="200" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
  <text x="16" y="28" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">Order Tracking</text>
  <line x1="28" y1="52" x2="28" y2="168" stroke="{G['border-strong']}" stroke-width="2"/>
  <circle cx="28" cy="56" r="7" fill="{G['fill-dark']}"/>
  <text x="48" y="60" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Order Received</text>
  <circle cx="28" cy="96" r="7" fill="{G['ok']}" stroke="{G['text']}" stroke-width="2"/>
  <text x="48" y="100" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Preparing Bouquet</text>
  <circle cx="28" cy="136" r="7" fill="{G['bg']}" stroke="{G['border-strong']}" stroke-width="2"/>
  <text x="48" y="140" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-muted']}">Out for Delivery</text>
  <circle cx="28" cy="176" r="7" fill="{G['bg']}" stroke="{G['border-strong']}" stroke-width="2"/>
  <text x="48" y="180" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-muted']}">Delivered</text>
</svg>'''


def adaptive_workspace() -> str:
    """Main MVP wireframe: Header + T-01 + T-02 + Adaptive Workspace tiles + ASO."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900" role="img" aria-label="Adaptive Workspace MVP wireframe">
  <rect width="1440" height="900" fill="{G['bg-muted']}"/>

  <!-- Header -->
  <g id="Header">
    <rect x="0" y="0" width="1440" height="64" fill="{G['bg']}" stroke="{G['border']}"/>
    <text x="32" y="40" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="{G['text']}">Lily's Florist</text>
    <text x="1240" y="40" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="{G['text-sec']}">Orders</text>
    <text x="1330" y="40" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="{G['text-sec']}">Help</text>
  </g>

  <!-- Left: Conversation T-01 -->
  <g id="T-01-Conversation">
    <rect x="24" y="88" width="420" height="788" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
    <text x="44" y="120" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" fill="{G['text']}">T-01 Conversation and Intent</text>
    <text x="44" y="142" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Persistent AI Floral Concierge</text>

    <rect x="44" y="164" width="380" height="100" rx="8" fill="{G['bg-soft']}"/>
    <text x="60" y="192" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">Welcome to Lily's Florist</text>
    <text x="60" y="214" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">AI-assisted flower purchase</text>
    <rect x="300" y="180" width="100" height="64" rx="6" fill="{G['fill']}"/>

    <circle cx="60" cy="310" r="14" fill="{G['fill']}" stroke="{G['border-strong']}"/>
    <rect x="84" y="292" width="300" height="52" rx="10" fill="{G['bg-muted']}" stroke="{G['border']}"/>
    <text x="100" y="314" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Hello! What occasion are you shopping for today?</text>
    <text x="100" y="332" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-muted']}">AI disclosure visible</text>

    <rect x="120" y="368" width="300" height="52" rx="10" fill="{G['fill-dark']}"/>
    <text x="136" y="390" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['bg']}">I need 10 pink flowers for a baby shower.</text>
    <text x="136" y="408" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['fill']}">Budget is $400.</text>

    <circle cx="60" cy="464" r="14" fill="{G['fill']}" stroke="{G['border-strong']}"/>
    <rect x="84" y="446" width="300" height="44" rx="10" fill="{G['bg-muted']}" stroke="{G['border']}"/>
    <text x="100" y="472" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Great — I've understood your needs...</text>

    <rect x="44" y="800" width="320" height="44" rx="22" fill="{G['bg']}" stroke="{G['border-strong']}"/>
    <text x="64" y="827" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-muted']}">Type your message...</text>
    <circle cx="388" cy="822" r="16" fill="{G['fill-dark']}"/>
  </g>

  <!-- Right column stack -->
  <g id="T-02-Shared-Understanding">
    <rect x="460" y="88" width="956" height="140" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
    <text x="480" y="120" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" fill="{G['text']}">T-02 Intent Summary (Shared Understanding)</text>
    <text x="480" y="148" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Occasion: Baby shower</text>
    <text x="700" y="148" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Qty / colour: 10 pink</text>
    <text x="920" y="148" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Budget: $400</text>
    <rect x="480" y="168" width="120" height="32" rx="6" fill="{G['bg']}" stroke="{G['border-strong']}"/>
    <text x="510" y="188" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Correct</text>
  </g>

  <g id="Adaptive-Workspace">
    <text x="480" y="260" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" fill="{G['text']}">Adaptive Workspace (T-03 … T-08)</text>

    <!-- T-03 -->
    <g id="T-03">
      <rect x="460" y="276" width="468" height="280" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="480" y="304" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">T-03 Curated Recommendations</text>
      <rect x="480" y="324" width="190" height="200" rx="8" fill="{G['bg']}" stroke="{G['border']}"/>
      <rect x="492" y="336" width="166" height="90" rx="6" fill="{G['fill']}"/>
      <text x="492" y="448" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="{G['text']}">Pink Flower Vase</text>
      <text x="492" y="468" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$125.00</text>
      <rect x="492" y="480" width="166" height="28" rx="6" fill="{G['fill-dark']}"/>
      <text x="575" y="498" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['bg']}">Select</text>
      <rect x="690" y="324" width="190" height="200" rx="8" fill="{G['bg']}" stroke="{G['border']}"/>
      <rect x="702" y="336" width="166" height="90" rx="6" fill="{G['fill']}"/>
      <text x="702" y="448" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="{G['text']}">Lilac Bouquet</text>
      <text x="702" y="468" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$95.00</text>
      <rect x="702" y="480" width="166" height="28" rx="6" fill="{G['fill-dark']}"/>
      <text x="785" y="498" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['bg']}">Select</text>
    </g>

    <!-- T-04 -->
    <g id="T-04">
      <rect x="948" y="276" width="468" height="280" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="968" y="304" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">T-04 Product Selection and Customization</text>
      <rect x="968" y="324" width="180" height="120" rx="6" fill="{G['fill']}"/>
      <text x="980" y="456" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700" fill="{G['text']}">Pink Flower Vase</text>
      <text x="1168" y="344" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Arrangement</text>
      <rect x="1168" y="352" width="220" height="28" rx="4" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="1176" y="370" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Pink Flower Vase</text>
      <text x="1168" y="404" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Size</text>
      <rect x="1168" y="412" width="220" height="28" rx="4" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="1176" y="430" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Standard</text>
      <text x="1168" y="464" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Card message</text>
      <rect x="1168" y="472" width="220" height="48" rx="4" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="1176" y="492" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">Happy baby shower!</text>
      <rect x="968" y="500" width="100" height="32" rx="6" fill="{G['fill-dark']}"/>
      <text x="1018" y="520" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['bg']}">Update</text>
    </g>

    <!-- T-05 -->
    <g id="T-05">
      <rect x="460" y="572" width="308" height="304" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="480" y="600" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">T-05 Delivery and Recipient</text>
      <circle cx="492" cy="640" r="8" fill="{G['fill-dark']}"/>
      <text x="512" y="644" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">10:00–12:00 · Available</text>
      <circle cx="492" cy="676" r="8" fill="{G['bg']}" stroke="{G['border-strong']}"/>
      <text x="512" y="680" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">12:00–14:00 · Available</text>
      <circle cx="492" cy="712" r="8" fill="{G['bg']}" stroke="{G['border-strong']}"/>
      <text x="512" y="716" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">14:00–16:00 · Available</text>
      <text x="480" y="760" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Deliver to: 123 Flower St</text>
      <text x="480" y="784" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Recipient: Sarah Johnson</text>
      <rect x="480" y="808" width="260" height="36" rx="8" fill="{G['fill-dark']}"/>
      <text x="610" y="830" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['bg']}">Confirm Delivery</text>
    </g>

    <!-- T-06 / T-07 -->
    <g id="T-06-T-07">
      <rect x="784" y="572" width="308" height="304" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="804" y="600" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">T-06 Order Summary</text>
      <text x="804" y="636" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Arrangement</text>
      <text x="1040" y="636" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$125.00</text>
      <text x="804" y="660" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Delivery</text>
      <text x="1040" y="660" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$12.00</text>
      <text x="804" y="684" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Tax</text>
      <text x="1040" y="684" text-anchor="end" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">$0.50</text>
      <line x1="804" y1="700" x2="1056" y2="700" stroke="{G['border']}"/>
      <text x="804" y="728" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">Total $137.50</text>
      <text x="804" y="764" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">T-07 Checkout</text>
      <text x="804" y="788" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-sec']}">Card ···· 4242</text>
      <rect x="804" y="808" width="260" height="36" rx="8" fill="{G['fill-dark']}"/>
      <text x="934" y="830" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['bg']}">Place Order</text>
    </g>

    <!-- T-08 -->
    <g id="T-08">
      <rect x="1108" y="572" width="308" height="304" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
      <text x="1128" y="600" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">T-08 Order Tracking</text>
      <rect x="1128" y="616" width="268" height="28" rx="6" fill="{G['bg-soft']}" stroke="{G['border']}"/>
      <text x="1140" y="635" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Order Confirmed</text>
      <line x1="1144" y1="668" x2="1144" y2="800" stroke="{G['border-strong']}" stroke-width="2"/>
      <circle cx="1144" cy="672" r="6" fill="{G['fill-dark']}"/>
      <text x="1160" y="676" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Order Received</text>
      <circle cx="1144" cy="716" r="6" fill="{G['ok']}" stroke="{G['text']}"/>
      <text x="1160" y="720" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Preparing Bouquet</text>
      <circle cx="1144" cy="760" r="6" fill="{G['bg']}" stroke="{G['border-strong']}"/>
      <text x="1160" y="764" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-muted']}">Out for Delivery</text>
      <circle cx="1144" cy="804" r="6" fill="{G['bg']}" stroke="{G['border-strong']}"/>
      <text x="1160" y="808" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text-muted']}">Delivered</text>
      <text x="1128" y="848" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-muted']}">Updates every minute</text>
    </g>
  </g>

  <!-- ASO overlay affordance -->
  <g id="ASO">
    <circle cx="1388" cy="840" r="28" fill="{G['fill-dark']}"/>
    <text x="1388" y="846" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" fill="{G['bg']}">?</text>
    <text x="1280" y="888" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">ASO FAQ overlay</text>
  </g>
</svg>'''


def journey_step(num: int, title: str, action: str, body: str, w: int = 280, h: int = 420) -> str:
    title_xml = escape(title)
    action_xml = escape(action)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Step {num}: {title_xml}">
  <rect width="{w}" height="{h}" rx="12" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="0" y="0" width="{w}" height="56" rx="12" fill="{G['bg-muted']}"/>
  <rect x="0" y="44" width="{w}" height="12" fill="{G['bg-muted']}"/>
  <text x="16" y="24" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-muted']}">Step {num}</text>
  <text x="16" y="44" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">{title_xml}</text>
  <text x="16" y="80" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">{action_xml}</text>
  {body}
  <rect x="12" y="{h - 48}" width="{w - 24}" height="28" rx="6" fill="{G['fill-dark']}"/>
  <text x="{w // 2}" y="{h - 29}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['bg']}">Continue</text>
</svg>'''


def journey_bodies() -> dict[str, str]:
    return {
        "01-open-conversation.svg": journey_step(
            1,
            "Open Lily's Florist",
            "Customer opens adaptive workspace",
            f'''<rect x="16" y="100" width="248" height="72" rx="8" fill="{G['bg-soft']}"/>
  <text x="28" y="128" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Welcome banner</text>
  <circle cx="36" cy="210" r="10" fill="{G['fill']}"/>
  <rect x="56" y="194" width="200" height="40" rx="8" fill="{G['bg-muted']}" stroke="{G['border']}"/>
  <text x="68" y="218" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Occasion prompt</text>
  <rect x="16" y="320" width="200" height="32" rx="16" fill="{G['bg']}" stroke="{G['border-strong']}"/>''',
        ),
        "02-share-preferences.svg": journey_step(
            2,
            "Share preferences",
            "Occasion, budget, preferences",
            f'''<rect x="56" y="110" width="200" height="48" rx="10" fill="{G['fill-dark']}"/>
  <text x="68" y="138" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['bg']}">User: baby shower / $400</text>
  <circle cx="36" cy="200" r="10" fill="{G['fill']}"/>
  <rect x="56" y="184" width="200" height="40" rx="8" fill="{G['bg-muted']}" stroke="{G['border']}"/>
  <text x="68" y="208" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">AI acknowledges intent</text>''',
        ),
        "03-recommendations.svg": journey_step(
            3,
            "View recommendations",
            "Validated curated options",
            f'''<rect x="16" y="110" width="112" height="160" rx="8" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="28" y="122" width="88" height="60" rx="4" fill="{G['fill']}"/>
  <text x="28" y="204" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="{G['text']}">$125</text>
  <rect x="152" y="110" width="112" height="160" rx="8" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="164" y="122" width="88" height="60" rx="4" fill="{G['fill']}"/>
  <text x="164" y="204" font-family="Arial, Helvetica, sans-serif" font-size="10" fill="{G['text']}">$95</text>''',
        ),
        "04-customize.svg": journey_step(
            4,
            "Customize bouquet",
            "Basic options + delivery details",
            f'''<rect x="16" y="110" width="100" height="70" rx="6" fill="{G['fill']}"/>
  <rect x="132" y="110" width="132" height="24" rx="4" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="132" y="146" width="132" height="24" rx="4" fill="{G['bg']}" stroke="{G['border']}"/>
  <rect x="132" y="182" width="132" height="24" rx="4" fill="{G['bg']}" stroke="{G['border']}"/>
  <text x="16" y="230" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">Date / time slot fields</text>''',
        ),
        "05-delivery.svg": journey_step(
            5,
            "Select delivery",
            "Validated delivery slot",
            f'''<circle cx="28" cy="120" r="7" fill="{G['fill-dark']}"/>
  <text x="48" y="124" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Slot A · Available</text>
  <circle cx="28" cy="156" r="7" fill="{G['bg']}" stroke="{G['border-strong']}"/>
  <text x="48" y="160" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Slot B · Available</text>
  <text x="16" y="210" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">123 Flower St · Recipient</text>''',
        ),
        "06-checkout.svg": journey_step(
            6,
            "Confirm & pay",
            "Summary + secure payment",
            f'''<text x="16" y="120" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Arrangement $125.00</text>
  <text x="16" y="144" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="{G['text']}">Delivery $12.00</text>
  <text x="16" y="176" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{G['text']}">Total $137.50</text>
  <text x="16" y="220" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-sec']}">Card ···· 4242</text>''',
        ),
        "07-tracking.svg": journey_step(
            7,
            "Track order",
            "Authoritative status timeline",
            f'''<rect x="16" y="110" width="248" height="28" rx="6" fill="{G['bg-soft']}"/>
  <text x="28" y="128" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Order Confirmed</text>
  <line x1="32" y1="160" x2="32" y2="280" stroke="{G['border-strong']}"/>
  <circle cx="32" cy="164" r="5" fill="{G['fill-dark']}"/>
  <text x="48" y="168" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Received</text>
  <circle cx="32" cy="208" r="5" fill="{G['ok']}"/>
  <text x="48" y="212" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text']}">Preparing</text>
  <circle cx="32" cy="252" r="5" fill="{G['bg']}" stroke="{G['border-strong']}"/>
  <text x="48" y="256" font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{G['text-muted']}">Out for Delivery</text>''',
        ),
    }


def main() -> None:
    for name, svg in ICONS.items():
        write(ASSETS / "icons" / name, svg)

    write(ASSETS / "chrome" / "header-bar.svg", chrome_header())
    user, assistant = chrome_chat_bubbles()
    write(ASSETS / "chrome" / "chat-bubble-user.svg", user)
    write(ASSETS / "chrome" / "chat-bubble-assistant.svg", assistant)
    write(ASSETS / "chrome" / "chat-input.svg", chrome_input())
    write(ASSETS / "chrome" / "status-badge-available.svg", chrome_badge())
    write(ASSETS / "chrome" / "button-primary.svg", chrome_button())

    write(ASSETS / "tiles" / "tile-frame.svg", tile_frame())
    write(ASSETS / "tiles" / "product-card.svg", product_card())
    write(ASSETS / "tiles" / "order-summary.svg", order_summary())
    write(ASSETS / "tiles" / "tracking-timeline.svg", tracking_timeline())

    write(WIREFRAMES / "adaptive-workspace-mvp.svg", adaptive_workspace())
    for name, svg in journey_bodies().items():
        write(WIREFRAMES / "journey-steps" / name, svg)

    print("Generated assets under", ASSETS)
    print("Generated wireframes under", WIREFRAMES)


if __name__ == "__main__":
    main()
