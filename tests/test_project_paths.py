"""Check notebook setup from a fresh clone without partner data.

Run from the repository root with python -m unittest discover -s tests -v.
"""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from project_paths import (
    data_directory, find_project_root, merged_file, output_directory,
    required_file, wheel_wear_file,
)


class ProjectPathsTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name).resolve()
        (self.root / "requirements.txt").touch()
        (self.root / "notebooks").mkdir()
        (self.root / "src").mkdir()
        (self.root / "data").mkdir()

    def test_root_is_found_from_root_or_notebooks(self):
        self.assertEqual(find_project_root(self.root), self.root)
        self.assertEqual(find_project_root(self.root / "notebooks"), self.root)

    def test_unrelated_directory_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as elsewhere:
            with self.assertRaisesRegex(FileNotFoundError, "repository"):
                find_project_root(elsewhere)

    def test_default_data_location_is_always_root_data(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(data_directory(self.root), self.root / "data")

    def test_external_and_relative_data_settings_remain_supported(self):
        with patch.dict(os.environ, {"HUNTING_DATA_DIR": "approved"}):
            self.assertEqual(data_directory(self.root), self.root / "approved")
        with patch.dict(os.environ, {"HUNTING_DATA_DIR": str(self.root / "external")}):
            self.assertEqual(data_directory(self.root), self.root / "external")

    def test_merged_filename_and_fallback_are_supported(self):
        data = self.root / "data"
        fallback = data / "final_merged_data(in).csv"
        fallback.touch()
        self.assertEqual(merged_file(data), fallback)
        preferred = data / "final_merged_data.csv"
        preferred.touch()
        self.assertEqual(merged_file(data), preferred)

    def test_old_generated_merge_does_not_override_downloaded_input(self):
        output = self.root / "outputs" / "data"
        output.mkdir(parents=True)
        (output / "final_merged_data.csv").touch()
        with self.assertRaisesRegex(FileNotFoundError, "Teams"):
            merged_file(self.root / "data")

    def test_wheel_wear_workbook_in_teams_profile_tree(self):
        folder = self.root / "data" / "Profiles" / "Candidate wheel profiles"
        folder.mkdir(parents=True)
        workbook = folder / "2023-06-13 - Wheel wear results.xlsx"
        workbook.touch()
        self.assertEqual(wheel_wear_file(self.root / "data"), workbook)

    def test_wheel_wear_workbook_directly_under_data_is_supported(self):
        workbook = self.root / "data" / "2023-06-13 - Wheel wear results.xlsx"
        workbook.touch()
        self.assertEqual(wheel_wear_file(self.root / "data"), workbook)

    def test_missing_file_names_the_input_and_install_guide(self):
        with self.assertRaisesRegex(FileNotFoundError, "missing.xlsx.*INSTALL.md"):
            required_file(self.root / "data" / "missing.xlsx")

    def test_output_folder_is_relative_to_project_without_changing_inputs(self):
        expected = self.root / "outputs" / "data"
        self.assertEqual(output_directory(self.root, "data"), expected)
        self.assertTrue(expected.is_dir())
        self.assertEqual(list((self.root / "data").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
