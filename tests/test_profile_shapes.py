"""Synthetic profile checks; no partner data are needed."""

from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from profile_shapes import TREAD_GRID, read_tread, describe_tread, prepare_truck_shapes
from contact_hunting import paired_car_intervals


def write_profile(path, x=None, offset=0, declared_count=None):
    x = np.arange(55., 116.) if x is None else np.asarray(x)
    count = len(x) if declared_count is None else declared_count
    rows = [f"{value} {offset - 0.04 * value} 0 0" for value in x]
    path.write_text(f"ColumnDef=X,Y,A,C\nXYPoints={count}\n" + "\n".join(rows))


class ProfileTests(unittest.TestCase):
    def test_linear_slope_and_vertical_offset_invariance(self):
        height = -0.04 * TREAD_GRID
        for offset in (0, 100):
            slope, residual = describe_tread(height + offset)
            self.assertAlmostEqual(slope, -0.04)
            self.assertLess(residual, 1e-12)

    def test_bowed_tread_has_positive_departure_from_line(self):
        slope, residual = describe_tread(0.01 * (TREAD_GRID - 85) ** 2)
        self.assertAlmostEqual(slope, 0)
        self.assertGreater(residual, 0)

    def test_reader_centers_height_without_writing_source(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wheel.WHL"
            write_profile(path, offset=20)
            before = path.read_bytes()
            height = read_tread(path)
            np.testing.assert_allclose(height, -0.04 * (TREAD_GRID - 85), atol=1e-12)
            self.assertEqual(before, path.read_bytes())

    def test_reader_rejects_bad_counts_duplicate_x_and_missing_coverage(self):
        cases = [
            ({"declared_count": 2}, "count"),
            ({"x": [55, 60, 85, 85, 110, 115]}, "increasing"),
            ({"x": [70, 80, 90, 100]}, "cover"),
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wheel.WHL"
            for kwargs, error in cases:
                with self.subTest(kwargs=kwargs):
                    write_profile(path, **kwargs)
                    with self.assertRaisesRegex(ValueError, error):
                        read_tread(path)

    def test_truck_features_and_missing_wheel_check(self):
        trucks = pd.DataFrame({"Car": [1, 1], "Truck": [1, 1]})
        with tempfile.TemporaryDirectory() as folder:
            for axle in (1, 2):
                for side in ("L", "R"):
                    write_profile(Path(folder) / f"Car1_Axle{axle}{side}.WHL",
                                  offset=10 if side == "L" else 20)
            shapes, wheels, profiles = prepare_truck_shapes(folder, trucks)
            self.assertEqual(len(shapes), 1)
            self.assertEqual(len(wheels), 4)
            self.assertEqual(len(profiles), 4)
            self.assertAlmostEqual(shapes.mean_tread_slope.iloc[0], -0.04)
            self.assertLess(shapes.max_left_right_shape_difference.iloc[0], 1e-12)
            (Path(folder) / "Car1_Axle2R.WHL").unlink()
            with self.assertRaisesRegex(ValueError, "coverage"):
                prepare_truck_shapes(folder, trucks)

    def test_invalid_truck_identifier_rejected(self):
        with self.assertRaisesRegex(ValueError, "identifiers"):
            prepare_truck_shapes("unused", pd.DataFrame({"Car": [1], "Truck": [3]}))

    def test_custom_paired_comparison(self):
        predictions = pd.DataFrame({
            "Car": [1, 1, 2, 2], "Truck": 1, "Rail_Profile": [1, 2, 1, 2],
            "actual": [0, 1, 0, 1], "base": [1, 1, 1, 1], "shape": [0, 1, 0, 1],
        })
        _, changes = paired_car_intervals(
            predictions, n_bootstrap=20, comparisons=(("shape", "base", "Added shape"),)
        )
        self.assertEqual(changes.change_in_balanced_accuracy.iloc[0], 0.5)
        self.assertEqual(changes.cars_with_fewer_errors.iloc[0], 2)


if __name__ == "__main__":
    unittest.main()
