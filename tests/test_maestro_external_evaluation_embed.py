from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAESTRO = ROOT / "maestro.html"
CNAME = ROOT / "CNAME"
CANONICAL_ZAXAM_ORIGIN = "https://zaxam.net"
LAUNCH_WRAPPER = "external-evaluation.html"


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

    def test_exactly_one_controlled_entry_iframe_is_present(self) -> None:
        self.assertEqual(len(self.iframes), 1)
        self.assertEqual(self.iframes[0].get("src"), LAUNCH_WRAPPER)
        self.assertEqual(
            self.iframes[0].get("title"),
            "Processual Maestro External Evaluation controlled entry",
        )

    def test_overview_never_embeds_or_links_directly_to_render_workspace(self) -> None:
        render_workspace = (
            "https://processual-maestro-external-evaluation.onrender.com/console/evaluation.html"
        )
        self.assertNotIn(f'src="{render_workspace}"', self.html)
        self.assertNotIn(f'href="{render_workspace}"', self.html)
        wrapper_links = [link for link in self.links if link.get("href") == LAUNCH_WRAPPER]
        self.assertEqual(len(wrapper_links), 1)

    def test_controlled_entry_keeps_browser_boundary_fail_closed(self) -> None:
        iframe = self.iframes[0]
        self.assertEqual(iframe.get("referrerpolicy"), "no-referrer")
        self.assertEqual(iframe.get("sandbox"), "allow-scripts allow-same-origin")
        sandbox = set((iframe.get("sandbox") or "").split())
        self.assertNotIn("allow-forms", sandbox)
        self.assertNotIn("allow-top-navigation", sandbox)
        self.assertNotIn("allow-popups", sandbox)
        self.assertIn("does not store the launch ticket or Evaluation API key", self.html)
        self.assertIn("Direct Render navigation is not an authorized workspace path", self.html)
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_evaluation_is_not_presented_as_production_or_mock_fallback(self) -> None:
        self.assertIn("Production execution remains disabled", self.html)
        self.assertIn("Evaluation-ready, not production-certified", self.html)
        self.assertIn("Workspace entry is fail-closed", self.html)

    def test_live_workspace_is_primary_and_demo_is_secondary(self) -> None:
        live_position = self.html.index("Recommended · Live evaluation")
        demo_position = self.html.index("No credentials · Deterministic")
        workspace_position = self.html.index('id="external-evaluation"')
        self.assertLess(live_position, demo_position)
        self.assertLess(demo_position, workspace_position)
        self.assertIn("Open controlled entry", self.html)
        self.assertIn("Launch interactive demo", self.html)

    def test_customer_journey_and_quota_explanation_are_visible(self) -> None:
        for marker in (
            "1 · Launch",
            "2 · Connect",
            "3 · Execute",
            "4 · Prove",
            "A fresh admitted execution consumes +1 quota.",
            "Status reads, durable replay and idempotency conflict consume zero additional units.",
            "Direct workspace entry without launch authority",
        ):
            self.assertIn(marker, self.html)

    def test_mobile_and_reduced_motion_ui_contracts_are_present(self) -> None:
        self.assertIn("@media(max-width:620px)", self.html)
        self.assertIn("@media(prefers-reduced-motion:reduce)", self.html)
        self.assertIn("height:clamp(760px,84vh,1040px)", self.html)

    def test_page_has_no_script_that_can_observe_launch_or_key_state(self) -> None:
        # The overview embeds only the local launch wrapper and intentionally has no script.
        self.assertNotIn("<script", self.html.lower())


if __name__ == "__main__":
    unittest.main()
