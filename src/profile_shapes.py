"""A small set of descriptors from exported wheel-profile coordinates."""

from pathlib import Path
import re

import numpy as np
import pandas as pd


TREAD_GRID = np.arange(60.0, 111.0, 1.0)
SHAPE_COLUMNS = [
    "mean_tread_slope",
    "mean_tread_nonlinearity",
    "max_left_right_shape_difference",
]
SHAPE_MODELS = {
    "Mean conicity + rail": ["conicity_mean"],
    "Mean conicity + shape + rail": ["conicity_mean"] + SHAPE_COLUMNS,
}
SHAPE_COMPARISONS = (
    ("Mean conicity + shape + rail", "Mean conicity + rail", "Add profile shape"),
)


def read_tread(path):
    """Read a shared tread window without changing the file or its coordinates.

    Both sides in these exports use positive x from the flange toward the tread.
    Units and the FIT reconstruction still require source confirmation. The
    interpolation window avoids duplicate x positions near the flange root.
    """
    headers = {}
    rows = []
    for line in Path(path).read_text(encoding="cp1252").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            headers[key] = value.strip()
        elif line.strip():
            try:
                row = [float(value) for value in line.split()]
            except ValueError as error:
                raise ValueError("Unexpected text in the profile coordinate block.") from error
            if len(row) != 4:
                raise ValueError("This reader expects four WHL coordinate columns.")
            rows.append(row)
    if headers.get("ColumnDef") != "X,Y,A,C":
        raise ValueError("The profile has an unsupported column definition.")
    coordinates = np.asarray(rows, dtype=float)
    if len(coordinates) != int(headers.get("XYPoints", -1)):
        raise ValueError("The profile point count does not match its header.")
    if coordinates.ndim != 2 or coordinates.shape[1] != 4:
        raise ValueError("The profile has no valid coordinate block.")
    if not np.isfinite(coordinates).all():
        raise ValueError("Profile coordinates must be finite.")

    # Use neighboring points to bracket both interpolation endpoints.
    band = coordinates[(coordinates[:, 0] >= 55) & (coordinates[:, 0] <= 115), :2]
    if len(band) < 3 or not np.all(np.diff(band[:, 0]) > 0):
        raise ValueError("The tread window needs strictly increasing x coordinates.")
    if band[0, 0] > TREAD_GRID[0] or band[-1, 0] < TREAD_GRID[-1]:
        raise ValueError("The profile does not cover the full tread window.")
    height = np.interp(TREAD_GRID, band[:, 0], band[:, 1])
    # Centering removes export height offsets from the comparison, in memory.
    return height - np.interp(85.0, band[:, 0], band[:, 1])


def describe_tread(height):
    """Return signed linear slope and RMS departure from that fitted line."""
    height = np.asarray(height, dtype=float)
    if height.shape != TREAD_GRID.shape or not np.isfinite(height).all():
        raise ValueError("A tread must have one finite height per grid position.")
    centered_x = TREAD_GRID - TREAD_GRID.mean()
    design = np.column_stack((centered_x, np.ones(len(centered_x))))
    slope, intercept = np.linalg.lstsq(design, height, rcond=None)[0]
    residual = height - (slope * centered_x + intercept)
    return float(slope), float(np.sqrt(np.mean(residual ** 2)))


def prepare_truck_shapes(profile_folder, truck_assessments):
    """Calculate truck descriptors from four wheel profiles."""
    expected_trucks = truck_assessments[["Car", "Truck"]].drop_duplicates()
    if expected_trucks.empty or not expected_trucks.Truck.isin([1, 2]).all():
        raise ValueError("Measured trucks must use identifiers 1 or 2.")
    cars = expected_trucks.Car.to_numpy(dtype=float)
    if not np.isfinite(cars).all() or (cars <= 0).any() or (cars != np.floor(cars)).any():
        raise ValueError("Car identifiers must be positive whole numbers.")
    profiles = {}
    wheel_rows = []
    pattern = re.compile(r"^Car(\d+)_Axle([1-4])([LR])\.WHL$")
    for path in sorted(Path(profile_folder).glob("*.WHL")):
        match = pattern.fullmatch(path.name)
        if match is None:
            raise ValueError("A wheel-profile filename has an unsupported format.")
        car, axle = int(match[1]), int(match[2])
        side = match[3]
        key = (car, axle, side)
        if key in profiles:
            raise ValueError("More than one profile was found for a wheel.")
        profiles[key] = read_tread(path)
        slope, nonlinearity = describe_tread(profiles[key])
        wheel_rows.append({
            "Car": car, "Axle": axle, "Side": side,
            "tread_slope": slope, "tread_nonlinearity": nonlinearity,
        })

    expected_wheels = {
        (int(row.Car), axle, side)
        for row in expected_trucks.itertuples(index=False)
        for axle in ((1, 2) if row.Truck == 1 else (3, 4))
        for side in ("L", "R")
    }
    if set(profiles) != expected_wheels:
        raise ValueError("Wheel-profile coverage does not match the measured trucks.")

    wheels = pd.DataFrame(wheel_rows)
    wheels["Truck"] = np.where(wheels.Axle <= 2, 1, 2)
    shapes = wheels.groupby(["Car", "Truck"], as_index=False).agg(
        mean_tread_slope=("tread_slope", "mean"),
        mean_tread_nonlinearity=("tread_nonlinearity", "mean"),
    )
    differences = {}
    for row in expected_trucks.itertuples(index=False):
        axles = (1, 2) if row.Truck == 1 else (3, 4)
        differences[(row.Car, row.Truck)] = max(
            np.sqrt(np.mean((profiles[(row.Car, axle, "L")]
                             - profiles[(row.Car, axle, "R")]) ** 2))
            for axle in axles
        )
    shapes["max_left_right_shape_difference"] = [
        differences[(row.Car, row.Truck)] for row in shapes.itertuples(index=False)
    ]
    return shapes, wheels, profiles
