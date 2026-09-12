from pathlib import Path
import unittest


PAGE = Path("external-evaluation.html")


class ExternalEvaluationLaunchHandoffTests(unittest.TestCase):
    def source(self) -> str:
        return PAGE.read_text(encoding="utf-8")

    def test_launch_token_arrives_in_fragment_not_query(self):
        source = self.source()
        self.assertIn("#evaluation-launch=", source)
        self.assertIn("window.location.hash", source)
        self.assertNotIn("window.location.search + 'evaluation-launch'", source)

    def test_zaxam_does_not_persist_launch_or_api_credentials(self):
        source = self.source()
        self.assertNotIn("localStorage.", source)
        self.assertNotIn("sessionStorage.", source)
        self.assertIn("never written to localStorage/sessionStorage/cookies", source)
        self.assertIn("API key still required", source)

    def test_fragment_is_cleaned_before_iframe_launch(self):
        source = self.source()
        clean = "history.replaceState(null, '', window.location.pathname + window.location.search);"
        assign = "frame.src = WORKSPACE + '?launch=' + encodeURIComponent(ticket);"
        self.assertIn(clean, source)
        self.assertIn(assign, source)
        self.assertLess(source.index(clean), source.index(assign))

    def test_workspace_remains_on_dedicated_origin_and_sandboxed(self):
        source = self.source()
        self.assertIn(
            "https://processual-maestro-external-evaluation.onrender.com/console/evaluation.html",
            source,
        )
        self.assertIn("referrerPolicy = 'no-referrer'", source)
        self.assertIn("allow-scripts allow-same-origin", source)
        self.assertIn("Production disabled", source)


if __name__ == "__main__":
    unittest.main()
