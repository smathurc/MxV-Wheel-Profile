"""Synthetic checks for the common team comparison tables."""

from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contact_hunting import ACC_SPEED, DISP_SPEED, CONTACT_COLUMNS
from team_data import (
    DOM_MEASUREMENTS, FEATURE_SETS, RAIL_COLUMNS, RF_ORIGINAL_COLUMNS,
    prepare_feature_tables, prepare_rail_summary, sha256_file,
)


def fixture(folder):
    """Give each axle distinct geometry so incorrect averaging is visible."""
    rows, contact = [], []
    source_bases = set(DOM_MEASUREMENTS) | {
        "Max Hollow Wear", "Max Hollow Wear Position", "|Max Hollow Wear - AAR|",
        "Max Hollow Wear Position - AAR",
    }
    for axle in range(1, 5):
        for side in "LR":
            x = np.arange(55., 116.)
            height = -0.01 * axle * x + (side == "R") * .001 * (x - 85) ** 2
            path = Path(folder) / f"Car1_Axle{axle}{side}.WHL"
            path.write_text("ColumnDef=X,Y,A,C\nXYPoints=61\n" +
                            "\n".join(f"{a} {b} 0 0" for a, b in zip(x, height)))
        for rail in range(1, 8):
            name = f"Car1_Axle{axle}_RProfile{rail}.wnt"
            row = dict(Filename=name, Car=1, Axle=axle,
                       Truck=1 if axle <= 2 else 2, Rail_Profile=rail,
                       **{"Eq Con 3mm": axle / 10, ACC_SPEED: 70 if axle <= 2 else 80,
                          DISP_SPEED: 65 if axle == 1 else 80})
            for base in source_bases:
                row[base + "_L"] = axle * 10.
                row[base + "_R"] = axle * 10. + axle
            row["Empty_Truck_Hunted"] = axle <= 2
            row["Empty_Axle_Hunted"] = axle == 1
            rows.append(row)
            contact.append(dict(Filename=name, **{c: axle for c in CONTACT_COLUMNS.values()}))
    rails = pd.DataFrame({"Rail_Profile": range(1, 8),
                          **{c: np.ones(7) for c in RAIL_COLUMNS}})
    return pd.DataFrame(rows), pd.DataFrame(contact), rails


class TeamDataTests(unittest.TestCase):
    def test_correct_axles_side_transforms_labels_and_feature_bundles(self):
        with tempfile.TemporaryDirectory() as folder:
            merged, contact, rails = fixture(folder)
            before = merged.copy(deep=True)
            result = prepare_feature_tables(merged.sample(frac=1, random_state=4), contact,
                                            folder, rails)
            trucks = result["trucks"]
            self.assertEqual(len(trucks), 14)
            self.assertEqual(len(result["axles"]), 28)
            self.assertEqual(len(result["wheels"]), 8)
            self.assertEqual(len(result["profiles"]), 8)
            self.assertEqual(trucks.Truck.tolist(), [1] * 7 + [2] * 7)
            self.assertAlmostEqual(trucks.loc[0, "wear_flange_width"], 15.75)
            self.assertAlmostEqual(trucks.loc[7, "wear_flange_width"], 36.75)
            self.assertAlmostEqual(trucks.loc[0, "Flange Width_Avg"], 15.75)
            self.assertAlmostEqual(trucks.loc[0, "Flange Width_Diff"], 1.5)
            self.assertAlmostEqual(trucks.loc[0, "Flange Width (Sd)_L"], 15)
            self.assertEqual(trucks.acceleration_hunted.tolist(), [1] * 7 + [0] * 7)
            self.assertEqual(trucks.displacement_hunted.tolist(), [1] * 7 + [0] * 7)
            self.assertEqual(len(FEATURE_SETS["rf_original"]), 11)
            self.assertEqual(len(FEATURE_SETS["rf_engineered"]), 24)
            self.assertEqual(len(FEATURE_SETS["dom"]), 16)
            self.assertEqual(len(FEATURE_SETS["core"]), 17)
            for columns in FEATURE_SETS.values():
                self.assertTrue(np.isfinite(trucks[columns].to_numpy(float)).all())
                self.assertFalse(set(columns) & {"Car", "Truck", "Rail_Profile", ACC_SPEED, DISP_SPEED})
            pd.testing.assert_frame_equal(merged, before)

    def test_rejects_duplicates_mapping_labels_and_missing_coverage(self):
        with tempfile.TemporaryDirectory() as folder:
            merged, contact, rails = fixture(folder)
            cases = []
            cases.append(pd.concat([merged, merged.iloc[[0]]]))
            bad = merged.copy(); bad.loc[0, "Truck"] = 2; cases.append(bad)
            bad = merged.copy(); bad.loc[0, "Empty_Truck_Hunted"] = False; cases.append(bad)
            cases.append(merged.loc[merged.Rail_Profile != 7])
            bad = merged.copy(); bad.loc[0, RF_ORIGINAL_COLUMNS[1]] = np.inf; cases.append(bad)
            for bad in cases:
                with self.subTest(case=len(bad)):
                    with self.assertRaises(ValueError):
                        prepare_feature_tables(bad, contact, folder, rails)
            with self.assertRaises(ValueError):
                prepare_feature_tables(merged, contact.iloc[1:], folder, rails)

    def test_rail_geometry_is_coordinate_only_and_sources_are_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = []
            for rail in range(1, 8):
                for side in ("L", "R") if rail <= 4 else ("",):
                    x = np.arange(-30., 31.)
                    y = -x ** 2 / (2 * (100 + rail))
                    path = Path(folder) / f"RProfile {rail}{side}.BAN"
                    path.write_text("ColumnDef=X,Y,A\nXYPoints=61\n\n" +
                                    "\n".join(f"{a} {b} 0" for a, b in zip(x, y)),
                                    encoding="cp1252")
                    paths.append(path)
            hashes = {p: sha256_file(p) for p in paths}
            summary = prepare_rail_summary(folder)
            self.assertEqual(summary.Rail_Profile.tolist(), list(range(1, 8)))
            np.testing.assert_allclose(summary.rail_crown_mean, np.arange(101., 108.))
            np.testing.assert_allclose(summary.rail_crown_range, 0, atol=1e-12)
            self.assertEqual(hashes, {p: sha256_file(p) for p in paths})
            paths[0].unlink()
            with self.assertRaisesRegex(ValueError, "11"):
                prepare_rail_summary(folder)


if __name__ == "__main__":
    unittest.main()
