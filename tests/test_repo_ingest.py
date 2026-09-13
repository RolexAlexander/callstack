"""Zero-cost verification that codebase ingestion works generically --
against a synthetic local directory, no network, no real repo needed.
This is the test that actually backs the "works on any codebase" claim.
"""

import tempfile
import unittest
from pathlib import Path

from support_agent.repo_ingest import ingest_codebase


class TestIngestCodebase(unittest.TestCase):
    def test_reads_readme_and_source_files_from_local_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Widget Service\nProcesses widgets via a queue.")
            (root / "app.py").write_text("def process_widget(): pass  # rate limited to 50/min")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "ignored.py").write_text("should not appear")

            context = ingest_codebase(str(root))

        self.assertIn("Widget Service", context)
        self.assertIn("rate limited to 50/min", context)
        self.assertNotIn("should not appear", context)

    def test_missing_path_returns_honest_empty_message_not_crash(self):
        context = ingest_codebase("/no/such/path/exists")
        self.assertIn("no readable", context.lower())

    def test_respects_size_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for i in range(20):
                (root / f"file_{i}.py").write_text("x = 1\n" * 5000)
            context = ingest_codebase(str(root))
        # MAX_CONTEXT_CHARS is 60_000; allow slack for the last chunk that
        # pushed it over before the loop's own check caught it.
        self.assertLess(len(context), 70_000)


if __name__ == "__main__":
    unittest.main()
