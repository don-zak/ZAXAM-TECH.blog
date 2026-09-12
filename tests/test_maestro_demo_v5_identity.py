import unittest
from pathlib import Path

PAGE = Path("maestro-demo-v5.html")


class MaestroDemoV5IdentityTests(unittest.TestCase):
    def source(self) -> str:
        return PAGE.read_text(encoding="utf-8")

    def test_v5_wrapper_declares_v5_release_identity(self) -> None:
        source = self.source()

        self.assertIn("Maestro — Interactive Governance Demo v5", source)
        self.assertIn('data-maestro-demo-release="v5"', source)
        self.assertIn('title="Maestro interactive governance demo v5"', source)
        self.assertIn("Public showcase · v5", source)

    def test_v5_removes_startup_tunisia_from_rendered_demo(self) -> None:
        source = self.source()

        self.assertIn("normalizeV5Identity(doc)", source)
        self.assertIn(".replace(/Startup Tunisia\\s*/gi,'')", source)
        self.assertIn(".replace(/Public showcase\\s*·\\s*v4/gi,'Public showcase · v5')", source)
        self.assertIn(
            "Interactive Governance Demo<br>Agentic Operations & Governance Control Plane<br>Public showcase · v5",
            source,
        )

    def test_v5_hides_embedded_legacy_shell_until_identity_is_normalized(self) -> None:
        source = self.source()

        self.assertIn(
            "iframe{border:0;width:100%;height:100%;display:block;background:#050a12;visibility:hidden}",
            source,
        )
        self.assertIn("iframe.ready{visibility:visible}", source)
        self.assertLess(
            source.index("normalizeV5Identity(doc);"),
            source.index("frame.classList.add('ready');"),
        )

    def test_v5_cache_identity_no_longer_advertises_v4_release(self) -> None:
        source = self.source()

        self.assertIn('src="maestro-demo-v4.html?v=5-shell"', source)
        self.assertNotIn("?v=4-lifecycle-fix", source)
        self.assertNotIn("Public showcase · v4", source)


if __name__ == "__main__":
    unittest.main()
