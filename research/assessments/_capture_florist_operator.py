"""Isolated Playwright capture of /florist. Never opens the shop."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent / "_florist_ux_shots"
PROFILE = Path(__file__).resolve().parent / "_florist_profile"
URL = "https://aea.artof.link/florist"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    PROFILE.mkdir(exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=True,
            channel="msedge",
            viewport={"width": 1440, "height": 1100},
            ignore_https_errors=True,
        )
        page = context.new_page()
        page.goto(URL, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "01-florist-full.png"), full_page=True)
        inbox = page.locator("#inbox")
        if inbox.count():
            inbox.screenshot(path=str(OUT / "02-inbox.png"))
        session = page.locator("#session")
        if session.count():
            session.screenshot(path=str(OUT / "03-session.png"))
        mode = page.locator("#operator-mode").inner_text() if page.locator("#operator-mode").count() else ""
        title = page.title()
        Path(OUT / "meta.txt").write_text(
            f"url={page.url}\ntitle={title}\nmode={mode}\n", encoding="utf-8"
        )
        context.close()


if __name__ == "__main__":
    main()
