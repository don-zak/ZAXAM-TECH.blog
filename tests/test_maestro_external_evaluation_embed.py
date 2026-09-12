from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAESTRO = ROOT / "maestro.html"
CNAME = ROOT / "CNAME"
CANONICAL_ZAXAM_ORIGIN = "https://zaxam.net"
EVALUATION_ORIGIN = "https://processual-maestro-external-evaluation.onrender.com"
EVALUATION_URL = f"{EVALUATION_ORIGIN}/console/evaluation.html"


class _IframeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.iframes: list[dict[str, str | None]] = []
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "iframe":
            self.iframes.append(values)
        if tag == "a":
            self.links.append(values)


class MaestroExternalEvaluationEmbedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = MAESTRO.read_text(encoding="utf-8")
        parser = _IframeParser()
        parser.feed(cls.html)
        cls.iframes = parser.iframes
        cls.links = parser.links

    def test_canonical_site_origin_matches_backend_frame_allowlist_contract(self) -> None:
        self.assertEqual(CNAME.read_text(encoding="utf-8").strip(), "zaxam.net")
        self.assertEqual(CANONICAL_ZAXAM_ORIGIN, "https://zaxam.net")

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
        self.assertIn("Evaluation-ready, not production-certified", self.html)

    def test_live_workspace_is_primary_and_demo_is_secondary(self) -> None:
        live_position = self.html.index("Recommended · Live evaluation")
        demo_position = self.html.index("No credentials · Deterministic")
        workspace_position = self.html.index('id="external-evaluation"')
        self.assertLess(live_position, demo_position)
        self.assertLess(demo_position, workspace_position)
        self.assertIn("Open workspace below", self.html)
        self.assertIn("Launch interactive demo", self.html)

    def test_customer_journey_and_quota_explanation_are_visible(self) -> None:
        for marker in (
            "1 · Connect",
            "2 · Prepare",
            "3 · Execute",
            "4 · Prove",
            "A fresh admitted execution consumes +1 quota.",
            "Status reads, durable replay and idempotency conflict consume zero additional units.",
            "Production execution and unsealed tasks or bindings remain blocked.",
        ):
            self.assertIn(marker, self.html)

    def test_workspace_has_safe_separate_tab_fallback(self) -> None:
        external_links = [
            link for link in self.links if link.get("href") == EVALUATION_URL
        ]
        self.assertEqual(len(external_links), 1)
        self.assertEqual(external_links[0].get("target"), "_blank")
        rel = set((external_links[0].get("rel") or "").split())
        self.assertIn("noopener", rel)
        self.assertIn("noreferrer", rel)

    def test_mobile_and_reduced_motion_ui_contracts_are_present(self) -> None:
        self.assertIn("@media(max-width:620px)", self.html)
        self.assertIn("@media(prefers-reduced-motion:reduce)", self.html)
        self.assertIn("height:clamp(760px,84vh,1040px)", self.html)

    def test_page_has_no_third_party_script_that_can_observe_parent_state(self) -> None:
        # The integration is an isolated iframe; the parent page intentionally has no script tag.
        self.assertNotIn("<script", self.html.lower())


if __name__ == "__main__":
    unittest.main()
