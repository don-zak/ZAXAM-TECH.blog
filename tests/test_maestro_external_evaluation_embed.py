from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAESTRO = ROOT / "maestro.html"
EVALUATION_ORIGIN = "https://processual-maestro-external-evaluation.onrender.com"
EVALUATION_URL = f"{EVALUATION_ORIGIN}/console/evaluation.html"


class _IframeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.iframes: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "iframe":
            self.iframes.append(dict(attrs))


class MaestroExternalEvaluationEmbedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = MAESTRO.read_text(encoding="utf-8")
        parser = _IframeParser()
        parser.feed(cls.html)
        cls.iframes = parser.iframes

    def test_exactly_one_governed_evaluation_iframe_is_present(self) -> None:
        self.assertEqual(len(self.iframes), 1)
        self.assertEqual(self.iframes[0].get("src"), EVALUATION_URL)
        self.assertEqual(
            self.iframes[0].get("title"),
            "Processual Maestro External Evaluation Workspace",
        )

    def test_embed_keeps_credential_on_evaluation_origin(self) -> None:
        iframe = self.iframes[0]
        self.assertEqual(iframe.get("referrerpolicy"), "no-referrer")
        self.assertEqual(iframe.get("sandbox"), "allow-scripts allow-same-origin")
        sandbox = set((iframe.get("sandbox") or "").split())
        self.assertNotIn("allow-forms", sandbox)
        self.assertNotIn("allow-top-navigation", sandbox)
        self.assertNotIn("allow-popups", sandbox)
        self.assertIn("ZAXAM-TECH does not proxy the API key", self.html)
        self.assertIn("does not store it", self.html)
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_evaluation_is_not_presented_as_production_or_mock_fallback(self) -> None:
        self.assertIn("production execution remains disabled", self.html)
        self.assertIn("fails closed rather than falling back to a mock execution path", self.html)
        self.assertIn("Authority issued → execution admitted → policy enforced → evidence produced.", self.html)

    def test_page_has_no_third_party_script_that_can_observe_parent_state(self) -> None:
        # The integration is an isolated iframe; the parent page intentionally has no script tag.
        self.assertNotIn("<script", self.html.lower())


if __name__ == "__main__":
    unittest.main()
