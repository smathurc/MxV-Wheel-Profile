"""Check notebook selection for the command-line reproduction workflow."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_notebooks import select_notebooks


class NotebookRunnerTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        (self.root / "notebooks").mkdir()
        for name in ["02_analysis.ipynb", "01_overview.ipynb", "demo.ipynb"]:
            (self.root / "notebooks" / name).touch()

    def test_default_runs_every_notebook_in_filename_order(self):
        result = select_notebooks(self.root, [])
        self.assertEqual([p.name for p in result],
                         ["01_overview.ipynb", "02_analysis.ipynb", "demo.ipynb"])

    def test_named_selection_accepts_stems_and_runs_duplicates_once(self):
        result = select_notebooks(self.root, ["demo", "02_analysis.ipynb", "demo"])
        self.assertEqual([p.name for p in result], ["demo.ipynb", "02_analysis.ipynb"])

    def test_unknown_or_external_notebooks_fail_before_execution(self):
        for name in ["missing", "../demo.ipynb", "/tmp/demo.ipynb"]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unknown notebook"):
                select_notebooks(self.root, [name])


if __name__ == "__main__":
    unittest.main()
