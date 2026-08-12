from html.parser import HTMLParser
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1] / "gateway"


class UiParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.labels = set()
        self.aria = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append(tag)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "label" and values.get("for"):
            self.labels.add(values["for"])
        self.aria.extend(key for key in values if key.startswith("aria-"))


class BrowserUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "ui" / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "ui" / "assets" / "styles.css").read_text(encoding="utf-8")
        cls.script = (ROOT / "ui" / "assets" / "app.js").read_text(encoding="utf-8")
        cls.parser = UiParser()
        cls.parser.feed(cls.html)

    def test_interface_has_one_clear_conversation_entry_point(self):
        self.assertEqual(1, self.html.count('id="message-form"'))
        self.assertIn('placeholder="For example:', self.html)
        self.assertIn("You can change every detail later", self.html)
        self.assertIn("Nothing is final until you review", self.html)

    def test_semantic_landmarks_labels_and_live_feedback_are_present(self):
        for tag in ("header", "main", "section", "aside", "form", "label", "dialog"):
            self.assertIn(tag, self.parser.tags)
        self.assertIn("message", self.parser.labels)
        self.assertIn("aria-live", self.parser.aria)
        self.assertIn('href="#conversation"', self.html)

    def test_keyboard_focus_and_help_return_are_explicit(self):
        self.assertIn(":focus-visible", self.css)
        self.assertIn("helpButton.focus()", self.script)
        self.assertIn('aria-expanded="false"', self.html)

    def test_gateway_serves_ui_without_weakening_api_perimeter(self):
        nginx = (ROOT / "nginx.conf").read_text(encoding="utf-8")
        self.assertIn("location = / {", nginx)
        self.assertIn("location /api/ {", nginx)
        self.assertIn('proxy_set_header X-Internal-Identity "";', nginx)

    def test_layout_has_explicit_desktop_tablet_and_mobile_contracts(self):
        self.assertIn("grid-template-columns: minmax(0, 1.7fr)", self.css)
        self.assertIn("@media (max-width: 60rem)", self.css)
        self.assertIn("@media (max-width: 40rem)", self.css)
        self.assertIn("grid-template-columns: 1fr", self.css)

    def test_mobile_controls_and_content_resist_clipping(self):
        self.assertIn("min-height: 44px", self.css)
        self.assertIn("overflow-wrap: anywhere", self.css)
        self.assertIn("width: 100%", self.css)
        self.assertIn('name="viewport"', self.html)

    def test_platform_preferences_remain_usable(self):
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn("forced-colors: active", self.css)


if __name__ == "__main__":
    unittest.main()
