"""Prepare checked own-axle geometry for common truck feature aggregation."""

import numpy as np

import pandas as pd

from contact_hunting import (
    DISP_SPEED, RAIL_PROFILES, SPEED_LIMIT,
)

from profile_shapes import SHAPE_COLUMNS, describe_tread

TRUCK_KEY = ["Car", "Truck", "Rail_Profile"]

AXLE_KEY = ["Car", "Truck", "Axle", "Rail_Profile"]

WEAR_SOURCES = {
    "wear_flange_width": ["Flange Width_L", "Flange Width_R"],
    "wear_flange_height": ["Flange Height (Sh)_L", "Flange Height (Sh)_R"],
    "wear_abs_hollow": ["|Max Hollow Wear - AAR|_L", "|Max Hollow Wear - AAR|_R"],
    "wear_hollow_position": ["Max Hollow Wear Position - AAR_L", "Max Hollow Wear Position - AAR_R"],
}

def _checked_keys(frame):
    missing = set(AXLE_KEY).difference(frame.columns)
    if missing or frame.empty:
        raise ValueError("Axle assessments need nonempty complete identifiers.")
    ids = frame[AXLE_KEY].to_numpy(dtype=float)
    if not np.isfinite(ids).all() or (ids != np.floor(ids)).any():
        raise ValueError("Car, truck, axle and rail identifiers must be finite integers.")
    if (frame.Car <= 0).any() or not frame.Axle.isin([1, 2, 3, 4]).all():
        raise ValueError("Unsupported measured car or axle identifier.")
    if not np.array_equal(frame.Truck, np.where(frame.Axle <= 2, 1, 2)):
        raise ValueError("Truck identifiers disagree with their axle mapping.")
    if not frame.Rail_Profile.isin(RAIL_PROFILES).all():
        raise ValueError("Unsupported rail identifier.")
    if frame.duplicated(AXLE_KEY).any():
        raise ValueError("Duplicate axle/rail assessments.")
    for (_, truck, _), group in frame.groupby(TRUCK_KEY, sort=True):
        expected = {1, 2} if truck == 1 else {3, 4}
        if len(group) != 2 or set(group.Axle) != expected:
            raise ValueError("Each truck/rail assessment requires its two correct axles.")

def prepare_axles(merged, wheels, profiles):
    """Make own-axle features without reading or modifying source files.

    Wear is averaged over the two sides of the same axle. Source rail rows
    never change the weight assigned to a wheel. Shape definitions use the
    existing centered tread window, whose physical interpretation is provisional.
    """
    _checked_keys(merged)
    sources = [column for pair in WEAR_SOURCES.values() for column in pair]
    needed = ["Eq Con 3mm", DISP_SPEED, *sources]
    if not set(needed).issubset(merged):
        raise ValueError("Required axle conicity, displacement or wear columns are missing.")
    numeric = merged[needed].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError("Axle measurements must be finite.")
    if ((merged[DISP_SPEED] <= 0) | (merged[DISP_SPEED] > SPEED_LIMIT)).any():
        raise ValueError("Axle displacement speeds must be in (0, 80].")
    if (merged.groupby(["Car", "Axle"])[sources].nunique() != 1).any().any():
        raise ValueError("Axle wear measurements must be invariant across rail rows.")

    wheel_columns = {"Car", "Axle", "Side", "tread_slope", "tread_nonlinearity"}
    if not wheel_columns.issubset(wheels):
        raise ValueError("Required own-wheel descriptors are missing.")
    if wheels.duplicated(["Car", "Axle", "Side"]).any():
        raise ValueError("Duplicate wheel descriptors.")
    expected = {(int(car), int(axle), side)
                for car, axle in merged[["Car", "Axle"]].drop_duplicates().itertuples(index=False)
                for side in ("L", "R")}
    wheel_keys = set(wheels[["Car", "Axle", "Side"]].itertuples(index=False, name=None))
    if wheel_keys != expected or set(profiles) != expected:
        raise ValueError("Own-wheel and profile coverage must match the measured axles.")
    if not np.isfinite(wheels[["tread_slope", "tread_nonlinearity"]].to_numpy(float)).all():
        raise ValueError("Own-wheel descriptors must be finite.")
    wheel_index = wheels.set_index(["Car", "Axle", "Side"]).sort_index()
    shape_rows = []
    for car, axle in sorted({(c, a) for c, a, _ in expected}):
        for side in ("L", "R"):
            slope, nonlinear = describe_tread(profiles[(car, axle, side)])
            supplied = wheel_index.loc[(car, axle, side)]
            if not np.allclose([slope, nonlinear],
                               [supplied.tread_slope, supplied.tread_nonlinearity],
                               rtol=1e-10, atol=1e-12):
                raise ValueError("Wheel descriptors disagree with their own profile.")
        own = wheel_index.loc[(car, axle)]
        difference = np.asarray(profiles[(car, axle, "L")]) - profiles[(car, axle, "R")]
        shape_rows.append({
            "Car": car, "Axle": axle,
            SHAPE_COLUMNS[0]: own.tread_slope.mean(),
            SHAPE_COLUMNS[1]: own.tread_nonlinearity.mean(),
            # Keep the original name so feature bundles can match. Here there
            # is one axle, so no maximum across the truck's two axles is taken.
            SHAPE_COLUMNS[2]: float(np.sqrt(np.mean(difference ** 2))),
        })
    result = merged[AXLE_KEY + ["Eq Con 3mm", DISP_SPEED] + sources].copy()
    result["conicity_mean"] = result["Eq Con 3mm"]
    result["displacement_hunted"] = (result[DISP_SPEED] < SPEED_LIMIT).astype(int)
    for name, pair in WEAR_SOURCES.items():
        result[name] = result[pair].mean(axis=1)
    retained = AXLE_KEY + ["displacement_hunted", "conicity_mean", *WEAR_SOURCES]
    result = result[retained].merge(pd.DataFrame(shape_rows), on=["Car", "Axle"],
                                     how="left", validate="many_to_one")
    return result.sort_values(AXLE_KEY).reset_index(drop=True)
