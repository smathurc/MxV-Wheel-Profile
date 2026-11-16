"""Checked, common truck observations for the team's model comparison.

Each assessment has equal weight. Side means and absolute differences are
computed within the same axle, then averaged over that truck's two axles.
Thus side means are also equal-weight means of its four wheels; differences
are mean within-axle differences, not differences of truck-level means.
Source units, reconstructed tread coordinates and rail geometry remain
provisional pending confirmation of the original exports.
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd

from axle_models import WEAR_SOURCES, prepare_axles
from contact_hunting import ACC_SPEED, DISP_SPEED, CONTACT_COLUMNS, TRUCK_KEY, prepare_trucks
from profile_shapes import SHAPE_COLUMNS, prepare_truck_shapes


# Numeric lists from notebooks/06_nguyenaa_randomforest_and_modeling.ipynb.
# The expanded RF shares wear-summary definitions with Dom, with a different full list.
RF_ORIGINAL_COLUMNS = [
    "Eq Con 3mm", "Flange Width (Sd)_L", "Flange Width (Sd)_R",
    "Flange Height (Sh)_L", "Flange Height (Sh)_R", "Max Hollow Wear_L",
    "Max Hollow Wear_R", "Max Hollow Wear Position_L", "Max Hollow Wear Position_R",
    "Flange Radius_L", "Flange Radius_R",
]
RF_ENGINEERED_COLUMNS = RF_ORIGINAL_COLUMNS + [
    "Hollow_Wear_Avg", "Hollow_Wear_Diff", "qR_Avg", "qR_Diff",
    "Flange_Width_Avg", "Flange_Width_Diff", "Flange_Angle_Avg", "Flange_Angle_Diff",
    "Flange Width (Sd)_Avg", "Flange Height (Sh)_Avg", "Max Hollow Wear_Avg",
    "Flange Radius_Avg", "Min Flange Root Radius_Avg",
]
# Dom's wheel_features declaration, retaining its average/difference order.
DOM_MEASUREMENTS = [
    "Flange Width", "Flange Width (Sd)", "Flange Height (Sh)", "qR",
    "Max Hollow Wear - AAR", "Max Flange Angle", "Flange Radius", "Min Flange Root Radius",
]
DOM_COLUMNS = [m + "_Avg" for m in DOM_MEASUREMENTS] + [m + "_Diff" for m in DOM_MEASUREMENTS]
RAIL_COLUMNS = ["rail_crown_mean", "rail_crown_range", "rail_width_1mm_mean"]
FEATURE_SETS = {
    "conicity": ["conicity_mean"],
    "wear": ["conicity_mean", *WEAR_SOURCES],
    "wear_shape": ["conicity_mean", *WEAR_SOURCES, *SHAPE_COLUMNS],
    "conicity_shape": ["conicity_mean", *SHAPE_COLUMNS],
    "wear_contact": ["conicity_mean", *WEAR_SOURCES, *CONTACT_COLUMNS],
    "wear_rail": ["conicity_mean", *WEAR_SOURCES, *RAIL_COLUMNS],
    "rf_original": RF_ORIGINAL_COLUMNS,
    "rf_engineered": RF_ENGINEERED_COLUMNS,
    "dom": DOM_COLUMNS,
    "core": ["conicity_mean", *DOM_COLUMNS],
}


def prepare_rail_summary(rail_folder):
    """Reproduce notebook 03's crown/width descriptors using coordinates only.

Fit Y=aX²+bX+c at points strictly within 20 coordinate units of the sampled
top; radius=-1/(2a). Width is sampled X range strictly above top Y minus 1.
For split rails use mean radius, radius range, and mean width across sides.
The supplied archive must contain eleven BAN files covering profiles 1–7.
"""
    paths = sorted(Path(rail_folder).glob("*.BAN"))
    if len(paths) != 11:
        raise ValueError("Rail geometry requires the archive's 11 BAN files.")
    rows = []
    names = set()
    for path in paths:
        match = re.fullmatch(r"RProfile ([1-7])([LR]?)\.BAN", path.name)
        if match is None or (int(match[1]), match[2]) in names:
            raise ValueError("Unsupported or duplicate rail-profile filename.")
        rail, side = int(match[1]), match[2]
        names.add((rail, side))
        headers, coordinates = {}, []
        for line in path.read_text(encoding="cp1252").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                headers[key.strip()] = value.strip()
            elif line.strip():
                try:
                    coordinates.append([float(v) for v in line.split()])
                except ValueError as error:
                    raise ValueError("Unexpected rail coordinate text.") from error
        columns = headers.get("ColumnDef", "").split(",")
        if columns not in (["X", "Y", "A"], ["X", "Y", "A", "C"]):
            raise ValueError("Unsupported BAN coordinate header.")
        points = np.asarray(coordinates, dtype=float)
        if (points.ndim != 2 or points.shape[1] != len(columns)
                or len(points) != int(headers.get("XYPoints", -1))
                or not np.isfinite(points).all()):
            raise ValueError("Rail coordinates must match the header and be finite.")
        x, y = points[:, 0], points[:, 1]
        top = int(np.argmax(y))
        window = np.abs(x - x[top]) < 20
        if np.unique(x[window]).size < 3:
            raise ValueError("Rail crown fit needs three distinct X positions.")
        a = np.polyfit(x[window], y[window], 2)[0]
        if not np.isfinite(a) or a >= 0:
            raise ValueError("Rail crown fit must have finite negative curvature.")
        within = x[y > y[top] - 1]
        rows.append({"Rail_Profile": rail, "crown": -1 / (2 * a),
                     "width": float(np.ptp(within))})
    expected = {(r, s) for r in range(1, 8) for s in (("L", "R") if r <= 4 else ("",))}
    if names != expected:
        raise ValueError("BAN coverage must match the seven documented rail profiles.")
    grouped = pd.DataFrame(rows).groupby("Rail_Profile", sort=True)
    result = grouped.agg(rail_crown_mean=("crown", "mean"),
                         rail_width_1mm_mean=("width", "mean"))
    result["rail_crown_range"] = grouped.crown.max() - grouped.crown.min()
    return result.reset_index()[["Rail_Profile", *RAIL_COLUMNS]]


def _checked_source_labels(merged):
    for column, speed in (("Empty_Truck_Hunted", ACC_SPEED),
                          ("Empty_Axle_Hunted", DISP_SPEED)):
        if column not in merged:
            continue
        labels = merged[column].astype(str).str.strip().str.lower().map(
            {"true": 1, "false": 0, "1": 1, "0": 0})
        if labels.isna().any() or not np.array_equal(labels.to_numpy(),
                                                    (merged[speed] < 80).astype(int).to_numpy()):
            raise ValueError(f"Source {column} labels disagree with their speed threshold.")


def prepare_feature_tables(merged, contact, profile_folder, rail_summary):
    """Build complete source-aligned tables without dropping any assessments.

The contact helper checks keys, axle mapping and outcome agreement. Require
all four axles on all seven rail profiles for every car. RF numeric columns
are the exact published definitions; Dom's sixteen columns are its eight
physical wheel measurements' axle means and absolute side differences.
Rail identity is excluded from numeric bundles and encoded by the evaluator.
"""
    trucks = prepare_trucks(merged, contact)
    if merged.empty:
        raise ValueError("The measured-car table is empty.")
    expected = {(int(c), a, r) for c in merged.Car.unique()
                for a in range(1, 5) for r in range(1, 8)}
    actual = set(merged[["Car", "Axle", "Rail_Profile"]].itertuples(index=False, name=None))
    if actual != expected:
        raise ValueError("Every measured car requires four axles on all seven rail profiles.")
    _checked_source_labels(merged)
    shapes, wheels, profiles = prepare_truck_shapes(profile_folder, trucks)
    axles = prepare_axles(merged, wheels, profiles)
    source_columns = set(RF_ORIGINAL_COLUMNS)
    for measurement in [*DOM_MEASUREMENTS, "Max Hollow Wear"]:
        source_columns.update([measurement + "_L", measurement + "_R"])
    missing = source_columns.difference(merged.columns)
    if missing:
        raise ValueError(f"Required team measurement columns are missing: {sorted(missing)}")
    ordered_sources = sorted(source_columns)
    try:
        numeric = merged[ordered_sources].to_numpy(dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError("Team source measurements must be numeric.") from error
    if not np.isfinite(numeric).all():
        raise ValueError("Team source measurements must be finite.")
    wheel_sources = [c for c in ordered_sources if c != "Eq Con 3mm"]
    if not merged.groupby(["Car", "Axle"])[wheel_sources].nunique().eq(1).all().all():
        raise ValueError("Wheel geometry must be invariant across repeated rail rows.")
    features = merged[TRUCK_KEY + ordered_sources].copy()
    for measurement in [*DOM_MEASUREMENTS, "Max Hollow Wear"]:
        left, right = features[measurement + "_L"], features[measurement + "_R"]
        features[measurement + "_Avg"] = (left + right) / 2
        features[measurement + "_Diff"] = (left - right).abs()
    for alias, source in {"Hollow_Wear": "Max Hollow Wear - AAR", "Flange_Width": "Flange Width",
                          "Flange_Angle": "Max Flange Angle"}.items():
        for suffix in ("Avg", "Diff"):
            features[f"{alias}_{suffix}"] = features[f"{source}_{suffix}"]
    retained = list(dict.fromkeys(RF_ENGINEERED_COLUMNS + DOM_COLUMNS))
    numeric_trucks = features.groupby(TRUCK_KEY, sort=True)[retained].mean().reset_index()
    wear = axles.groupby(TRUCK_KEY, sort=True)[list(WEAR_SOURCES)].mean().reset_index()
    for table, on, validate in ((numeric_trucks, TRUCK_KEY, "one_to_one"),
                                (wear, TRUCK_KEY, "one_to_one"),
                                (shapes, ["Car", "Truck"], "many_to_one")):
        trucks = trucks.merge(table, on=on, how="left", validate=validate)
    required_rail = {"Rail_Profile", *RAIL_COLUMNS}
    if (not required_rail.issubset(rail_summary) or rail_summary.Rail_Profile.duplicated().any()
            or set(rail_summary.Rail_Profile) != set(range(1, 8))):
        raise ValueError("Rail summary must contain one row for each of profiles 1–7.")
    trucks = trucks.merge(rail_summary[["Rail_Profile", *RAIL_COLUMNS]], on="Rail_Profile",
                          how="left", validate="many_to_one")
    all_features = list(dict.fromkeys(c for cols in FEATURE_SETS.values() for c in cols))
    if len(trucks) != len(expected) // 2 or not np.isfinite(trucks[all_features].to_numpy(float)).all():
        raise ValueError("Common feature joins lost coverage or introduced nonfinite measurements.")
    trucks = trucks.sort_values(TRUCK_KEY).reset_index(drop=True)
    return dict(trucks=trucks, axles=axles, wheels=wheels, profiles=profiles,
                rail_summary=rail_summary.copy(), merged=merged.copy(),
                feature_sets={name: list(cols) for name, cols in FEATURE_SETS.items()})


def load_benchmark_data(data_dir):
    """Read the approved local inputs and prepare the shared feature tables."""
    data_dir = Path(data_dir).expanduser().resolve()
    merged_path = data_dir / "final_merged_data.csv"
    if not merged_path.exists():
        merged_path = data_dir / "final_merged_data(in).csv"
    contact_path = data_dir / "Profiles/WNTs/2023-06-21 - Hunt_Disp_Max_CP_Difference.csv"
    profile_folder = data_dir / "Profiles/Candidate wheel profiles"
    rail_folder = data_dir / "Profiles/Rail profiles"
    return prepare_feature_tables(pd.read_csv(merged_path),
                                  pd.read_csv(contact_path, encoding="cp1252"),
                                  profile_folder, prepare_rail_summary(rail_folder))
