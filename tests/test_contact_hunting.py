"""Synthetic checks for the join, model calculation, and grouped evaluation."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import contact_hunting as model


def example_tables():
    rows = []
    contact_rows = []
    for car in range(1, 5):
        for rail in range(1, 8):
            for axle in (1, 2):
                filename = f"Car{car}_Axle{axle}_RProfile {rail}.wnt"
                rows.append({
                    "Filename": filename, "Car": car, "Truck": 1,
                    "Axle": axle, "Rail_Profile": rail,
                    "Eq Con 3mm": car + rail / 100 + axle / 1000,
                    model.ACC_SPEED: 60 if (car + rail) % 3 else 80,
                    model.DISP_SPEED: 55 if axle == 2 else 80,
                })
                contact_rows.append({
                    "Filename": filename,
                    **{column: car + rail + axle for column in model.CONTACT_COLUMNS.values()},
                })
    return pd.DataFrame(rows), pd.DataFrame(contact_rows)


class PreparationTests(unittest.TestCase):
    def test_two_wheelsets_become_one_truck_assessment(self):
        source, contact = example_tables()
        result = model.prepare_trucks(source, contact)
        self.assertEqual(len(result), 28)
        self.assertFalse(result.duplicated(model.TRUCK_KEY).any())
        self.assertTrue(result.displacement_hunted.eq(1).all())
        self.assertTrue(np.allclose(result.conicity_gap, 0.001))

    def test_unmatched_contact_row_fails_instead_of_dropping_assessment(self):
        source, contact = example_tables()
        with self.assertRaisesRegex(ValueError, "no matching"):
            model.prepare_trucks(source, contact.iloc[1:])

    def test_repeated_truck_outcomes_must_agree(self):
        source, contact = example_tables()
        source.loc[0, model.ACC_SPEED] = 80
        with self.assertRaisesRegex(ValueError, "disagree"):
            model.prepare_trucks(source, contact)

    def test_wrong_axle_to_truck_mapping_fails(self):
        source, contact = example_tables()
        source.loc[0, "Truck"] = 2
        with self.assertRaisesRegex(ValueError, "axles"):
            model.prepare_trucks(source, contact)

    def test_filename_and_identifier_mismatch_fails(self):
        source, contact = example_tables()
        source.loc[0, "Car"] = 9
        with self.assertRaisesRegex(ValueError, "source filenames"):
            model.prepare_trucks(source, contact)

    def test_negative_sentinel_is_rejected(self):
        source, contact = example_tables()
        contact.loc[0, next(iter(model.CONTACT_COLUMNS.values()))] = -1000
        with self.assertRaisesRegex(ValueError, "negative"):
            model.prepare_trucks(source, contact)

    def test_calculated_displacement_speed_must_match_supplied_truck_summary(self):
        source, contact = example_tables()
        source["Min Empty Axle from Lat Disp HS [mph]"] = 80
        with self.assertRaisesRegex(ValueError, "Calculated truck speeds disagree"):
            model.prepare_trucks(source, contact)

    def test_unexpected_outcome_column_cannot_become_a_feature(self):
        source, contact = example_tables()
        contact["Future hunting outcome"] = 60
        result = model.prepare_trucks(source, contact)
        self.assertNotIn("Future hunting outcome", result.columns)
        predictors = {column for columns in model.FEATURE_SETS.values() for column in columns}
        self.assertTrue(predictors.isdisjoint({model.ACC_SPEED, model.DISP_SPEED,
                                             "acceleration_hunted", "displacement_hunted"}))


class ModelTests(unittest.TestCase):
    def test_kernel_scores_match_two_sample_closed_form(self):
        features = np.array([[0.0], [1.0]])
        scores = model.kernel_scores(features, features, [1, 1], [1, 1], [0, 1], 0.1, 1.0)
        off_diagonal = np.exp(-4 / 9)
        expected = (1 - off_diagonal) / (1.1 - off_diagonal)
        np.testing.assert_allclose(scores, [-expected, expected])

    def test_test_rows_do_not_change_scaling(self):
        train = np.array([[0.0], [1.0], [2.0]])
        single = model.kernel_scores(train, np.array([[0.5]]), [1, 1, 1], [1], [0, 0, 1], 1, 1)
        batch = model.kernel_scores(train, np.array([[0.5], [100000.0]]),
                                    [1, 1, 1], [1, 1], [0, 0, 1], 1, 1)
        np.testing.assert_allclose(single[0], batch[0])

    def test_adding_a_constant_feature_does_not_rescale_existing_distances(self):
        train = np.array([[0.0], [1.0], [2.0]])
        test = np.array([[0.5], [1.5]])
        original = model.kernel_scores(train, test, [1, 1, 2], [1, 2], [0, 0, 1], 1, 1)
        extended = model.kernel_scores(
            np.column_stack((train, np.ones(3))),
            np.column_stack((test, np.ones(2))),
            [1, 1, 2], [1, 2], [0, 0, 1], 1, 1,
        )
        np.testing.assert_allclose(original, extended)

    def test_balanced_accuracy_and_confusion_counts(self):
        result = model.classification_metrics([0, 0, 1, 1], [0, 1, 1, 1])
        self.assertEqual(result["balanced_accuracy"], 0.75)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["false_negative"], 0)

    def test_metrics_reject_broadcastable_label_shapes(self):
        with self.assertRaisesRegex(ValueError, "equal-length 1D"):
            model.classification_metrics([0, 1], [[0], [1]])
        with self.assertRaisesRegex(ValueError, "equal-length 1D"):
            model.classification_metrics([0, 1], [0])

    def test_every_prediction_holds_out_whole_cars(self):
        source, contact = example_tables()
        trucks = model.prepare_trucks(source, contact)
        original = model.kernel_scores
        checked_calls = []

        def checked_scores(train, test, *args):
            # The synthetic first feature encodes car in its whole-number part.
            if train.shape[1] > 0:
                train_cars = set(np.floor(train[:, 0]).astype(int))
                test_cars = set(np.floor(test[:, 0]).astype(int))
                self.assertTrue(train_cars.isdisjoint(test_cars))
            checked_calls.append(True)
            return original(train, test, *args)

        with patch.object(model, "kernel_scores", side_effect=checked_scores):
            with patch.object(model, "PARAMETER_GRID", ((1.0, 1.0),)):
                metrics, predictions, settings = model.evaluate_models(trucks, "acceleration_hunted")
        self.assertTrue(checked_calls)
        self.assertEqual(len(predictions), len(trucks))
        self.assertEqual(set(settings.held_car), set(trucks.Car))
        self.assertEqual(len(metrics), 6)

    def test_paired_bootstrap_preserves_identical_models_and_complete_cars(self):
        assessments = pd.DataFrame({
            "Car": np.repeat(np.arange(1, 5), 2),
            "Truck": 1,
            "Rail_Profile": np.tile([1, 2], 4),
            "actual": np.tile([0, 1], 4),
        })
        for name in model.FEATURE_SETS:
            assessments[name] = assessments.actual
        assessments["Conicity + contact + rail"] = 1 - assessments.actual
        scores, changes = model.paired_car_intervals(assessments, n_bootstrap=50, seed=7)
        contact = changes.set_index("comparison").loc["Add contact features"]
        self.assertEqual(contact.change_in_balanced_accuracy, -1)
        self.assertEqual(contact.lower_95, -1)
        self.assertEqual(contact.upper_95, -1)
        self.assertEqual(contact.cars_with_more_errors, 4)
        unchanged = changes.set_index("comparison").loc["Add wheelset mismatch"]
        self.assertEqual(unchanged.lower_95, 0)
        self.assertEqual(unchanged.upper_95, 0)
        scores_again, changes_again = model.paired_car_intervals(
            assessments, n_bootstrap=50, seed=7
        )
        pd.testing.assert_frame_equal(changes, changes_again)
        self.assertTrue(scores.valid_draws.eq(50).all())

    def test_shared_notebook_has_no_saved_outputs_or_widget_state(self):
        for name in ("03_contact_hunting_model.ipynb", "04_profile_shape_extension.ipynb"):
            path = ROOT / "notebooks" / name
            notebook = json.loads(path.read_text())
            self.assertNotIn("widgets", notebook["metadata"])
            for cell in notebook["cells"]:
                self.assertFalse(cell.get("attachments"))
                if cell["cell_type"] == "code":
                    self.assertEqual(cell["outputs"], [])
                    self.assertIsNone(cell["execution_count"])


if __name__ == "__main__":
    unittest.main()
