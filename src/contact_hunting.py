"""Compare wheel-rail contact features using car-grouped validation."""

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd


TRUCK_KEY = ["Car", "Truck", "Rail_Profile"]
AXLE_KEY = ["Car", "Axle", "Rail_Profile"]
ACC_SPEED = "Empty Truck from Acc HS [mph]"
DISP_SPEED = "Empty Axle from Lat Disp HS [mph]"
SPEED_LIMIT = 80
RAIL_PROFILES = tuple(range(1, 8))
CONTACT_COLUMNS = {
    "log_contact_profile_difference":
        "Max CP profile difference over ±3mm from 0mm RRD [mm]",
    "log_contact_lateral_gradient":
        "Max CP lateral gradient over ±3mm from 0mm RRD [mm]",
    "log_contact_angle_difference":
        "Max CP contact angle difference over ±3mm from 0mm RRD [mm]",
}
FEATURE_SETS = {
    "Rail kernel": [],
    "Mean conicity + rail": ["conicity_mean"],
    "Conicity + rail": ["conicity_mean", "conicity_gap"],
    "Conicity + contact + rail": ["conicity_mean", "conicity_gap"]
        + list(CONTACT_COLUMNS),
}
# Keep retained features at the same distance scale when adding predictors.
KERNEL_DISTANCE_SCALE = 9.0
MODEL_COMPARISONS = (
    ("Mean conicity + rail", "Rail kernel", "Add mean conicity"),
    ("Conicity + rail", "Mean conicity + rail", "Add wheelset mismatch"),
    ("Conicity + contact + rail", "Conicity + rail", "Add contact features"),
    ("Conicity + contact + rail", "Mean conicity + rail", "Full model vs mean conicity"),
)
# Fixed grid shared by all feature comparisons.
PARAMETER_GRID = tuple(product((0.1, 1.0, 10.0), (0.25, 1.0)))


def load_tables(data_folder):
    """Read local inputs without changing or exporting them."""
    data_folder = Path(data_folder)
    merged_path = data_folder / "final_merged_data.csv"
    if not merged_path.exists():
        merged_path = data_folder / "final_merged_data(in).csv"
    contact_path = (
        data_folder / "Profiles" / "WNTs"
        / "2023-06-21 - Hunt_Disp_Max_CP_Difference.csv"
    )
    return (
        pd.read_csv(merged_path),
        pd.read_csv(contact_path, encoding="cp1252"),
    )


def prepare_trucks(merged, contact):
    """Make one checked observation per car, truck, and rail profile."""
    columns = list(dict.fromkeys(
        ["Filename"] + TRUCK_KEY + ["Axle", "Eq Con 3mm", ACC_SPEED, DISP_SPEED]
    ))
    missing = set(columns).difference(merged.columns)
    missing_contact = {"Filename", *CONTACT_COLUMNS.values()}.difference(contact.columns)
    if missing or missing_contact:
        raise ValueError(f"Required columns are missing: {sorted(missing | missing_contact)}")

    data = merged[columns].copy()
    geometry = contact[["Filename"] + list(CONTACT_COLUMNS.values())].copy()
    if data.isna().any().any() or geometry.isna().any().any():
        raise ValueError("The required source columns contain missing values.")
    if data.Filename.duplicated().any() or data.duplicated(AXLE_KEY).any():
        raise ValueError("The merged table contains repeated wheelset/rail rows.")
    if geometry.Filename.duplicated().any():
        raise ValueError("The contact table contains repeated filenames.")

    ids = data[["Car", "Truck", "Axle", "Rail_Profile"]].to_numpy(dtype=float)
    if not np.isfinite(ids).all() or (ids != np.floor(ids)).any():
        raise ValueError("Car, truck, axle, and rail identifiers must be whole numbers.")
    if not data.Car.gt(0).all() or not data.Axle.isin([1, 2, 3, 4]).all():
        raise ValueError("The measured-car table has unsupported car or axle identifiers.")
    expected_truck = np.where(data.Axle <= 2, 1, 2)
    if not np.array_equal(data.Truck, expected_truck):
        raise ValueError("Truck 1 must contain axles 1–2; truck 2 must contain axles 3–4.")
    if not data.Rail_Profile.isin(RAIL_PROFILES).all():
        raise ValueError("This experiment expects rail profiles 1–7.")

    # Check the parsed identifiers against the source filename before joining.
    parsed = data.Filename.str.extract(r"^Car(\d+)_Axle(\d+)_RProfile\s*(\d+)\.wnt$")
    if parsed.isna().any().any():
        raise ValueError("A merged filename does not follow the measured-profile format.")
    if not np.array_equal(parsed.astype(int).to_numpy(), data[AXLE_KEY].to_numpy()):
        raise ValueError("The identifiers do not match the source filenames.")

    data = data.merge(geometry, on="Filename", how="left", validate="one_to_one", indicator=True)
    if not data["_merge"].eq("both").all():
        raise ValueError("Some measured profiles have no matching contact measurements.")
    data = data.drop(columns="_merge")
    numeric = ["Eq Con 3mm", ACC_SPEED, DISP_SPEED] + list(CONTACT_COLUMNS.values())
    if not np.isfinite(data[numeric].to_numpy(dtype=float)).all():
        raise ValueError("Required measurements must be finite numbers.")
    if (data[[ACC_SPEED, DISP_SPEED]] <= 0).any().any():
        raise ValueError("Hunting speeds must be positive.")
    if (data[[ACC_SPEED, DISP_SPEED]] > SPEED_LIMIT).any().any():
        raise ValueError("A speed exceeds the documented 80 mph test limit; check its meaning.")
    if (data[list(CONTACT_COLUMNS.values())] < 0).any().any():
        raise ValueError("Contact-difference magnitudes cannot be negative.")

    groups = data.groupby(TRUCK_KEY, sort=True)
    if not groups.size().eq(2).all() or not groups.Axle.nunique().eq(2).all():
        raise ValueError("Each truck/rail assessment must contain two different wheelsets.")
    if not groups[ACC_SPEED].nunique().eq(1).all():
        raise ValueError("The repeated truck-acceleration results disagree.")

    trucks = groups.agg(
        acceleration_speed=(ACC_SPEED, "first"),
        displacement_speed=(DISP_SPEED, "min"),
        conicity_mean=("Eq Con 3mm", "mean"),
        conicity_min=("Eq Con 3mm", "min"),
        conicity_max=("Eq Con 3mm", "max"),
    )
    trucks["conicity_gap"] = trucks.conicity_max - trucks.conicity_min
    for feature, source in CONTACT_COLUMNS.items():
        trucks[feature] = np.log1p(groups[source].max())
    trucks["acceleration_hunted"] = (trucks.acceleration_speed < SPEED_LIMIT).astype(int)
    # Either wheelset meeting the displacement criterion flags the truck.
    trucks["displacement_hunted"] = (trucks.displacement_speed < SPEED_LIMIT).astype(int)
    for source, calculated in (
        ("Min Empty Truck from Acc HS [mph]", "acceleration_speed"),
        ("Min Empty Axle from Lat Disp HS [mph]", "displacement_speed"),
    ):
        if source in merged.columns:
            supplied = merged.groupby(TRUCK_KEY, sort=True)[source]
            if not supplied.nunique(dropna=False).eq(1).all():
                raise ValueError("The supplied truck-speed summaries disagree within a truck.")
            if not np.allclose(supplied.first().to_numpy(), trucks[calculated].to_numpy()):
                raise ValueError("Calculated truck speeds disagree with the supplied summaries.")
    return trucks.reset_index()


def classification_metrics(actual, predicted):
    """Return metrics for a binary target containing both classes."""
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    if actual.ndim != 1 or predicted.ndim != 1 or actual.shape != predicted.shape:
        raise ValueError("Actual and predicted labels must be equal-length 1D arrays.")
    if set(np.unique(actual)) != {0, 1} or not np.isin(predicted, [0, 1]).all():
        raise ValueError("Metrics require both target classes and binary predictions.")
    true_positive = int(((actual == 1) & (predicted == 1)).sum())
    true_negative = int(((actual == 0) & (predicted == 0)).sum())
    false_positive = int(((actual == 0) & (predicted == 1)).sum())
    false_negative = int(((actual == 1) & (predicted == 0)).sum())
    recall = true_positive / (true_positive + false_negative)
    specificity = true_negative / (true_negative + false_positive)
    precision = true_positive / max(true_positive + false_positive, 1)
    return {
        "accuracy": float(np.mean(actual == predicted)),
        "balanced_accuracy": (recall + specificity) / 2,
        "recall": recall,
        "specificity": specificity,
        "precision": precision,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_positive": true_positive,
    }


def kernel_scores(train_features, test_features, train_rails, test_rails,
                  train_target, alpha, gamma):
    """Fit centered-target kernel ridge and return signed decision scores.

    Standardization uses the training rows only. Rail identity is one-hot
    encoded. Gaussian distances use the same fixed divisor for each feature
    set, so adding columns does not rescale the retained feature distances.
    These scores are not calibrated probabilities.
    """
    if alpha <= 0 or gamma <= 0:
        raise ValueError("alpha and gamma must be positive.")
    mean = train_features.mean(axis=0)
    scale = train_features.std(axis=0)
    scale = np.where(scale == 0, 1, scale)
    train_categories = (np.asarray(train_rails)[:, None] == RAIL_PROFILES).astype(float)
    test_categories = (np.asarray(test_rails)[:, None] == RAIL_PROFILES).astype(float)
    train = np.column_stack(((train_features - mean) / scale, train_categories))
    test = np.column_stack(((test_features - mean) / scale, test_categories))

    def gaussian_kernel(left, right):
        distances = (left * left).sum(axis=1)[:, None] + (right * right).sum(axis=1)
        distances = np.maximum(distances - 2 * left @ right.T, 0)
        return np.exp(-gamma * distances / KERNEL_DISTANCE_SCALE)

    signed_target = 2 * np.asarray(train_target) - 1
    target_mean = signed_target.mean()
    weights = np.linalg.solve(
        gaussian_kernel(train, train) + alpha * np.eye(len(train)),
        signed_target - target_mean,
    )
    return gaussian_kernel(test, train) @ weights + target_mean


def evaluate_models(trucks, target, feature_sets=None):
    """Leave each car out once; choose kernel settings inside training cars.

    Returns aggregate metrics, assessment predictions, and selected settings.
    The latter two tables contain partner-derived information and stay local.
    """
    if feature_sets is None:
        feature_sets = FEATURE_SETS
    if target not in ("acceleration_hunted", "displacement_hunted"):
        raise ValueError("Choose an acceleration or displacement hunting target.")
    car_ids = trucks.Car.to_numpy()
    cars = np.unique(car_ids)
    if len(cars) < 4:
        raise ValueError("At least four cars are needed for the grouped inner/outer splits.")
    actual = trucks[target].to_numpy()
    if set(np.unique(actual)) != {0, 1}:
        raise ValueError("The target must contain both hunting classes.")
    rails = trucks.Rail_Profile.to_numpy()
    features = {name: trucks[columns].to_numpy() for name, columns in feature_sets.items()}
    if any(not np.isfinite(values).all() for values in features.values()):
        raise ValueError("Model features must be finite numbers.")
    reserved = set(TRUCK_KEY + ["actual", "Always hunting", "Rail only"])
    if reserved.intersection(feature_sets):
        raise ValueError("Feature-set names must not overwrite identifiers or baselines.")
    predictions = {name: np.zeros(len(trucks), dtype=int)
                   for name in ["Always hunting", "Rail only", *feature_sets]}
    selected = []

    def predict(name, train, test, alpha, gamma):
        return (kernel_scores(
            features[name][train], features[name][test], rails[train], rails[test],
            actual[train], alpha, gamma,
        ) >= 0).astype(int)

    for held_car in cars:
        train = np.flatnonzero(car_ids != held_car)
        test = np.flatnonzero(car_ids == held_car)
        if set(np.unique(actual[train])) != {0, 1}:
            raise ValueError("A training fold has only one target class.")
        predictions["Always hunting"][test] = 1
        for rail in RAIL_PROFILES:
            reference = train[rails[train] == rail]
            if len(reference) == 0:
                raise ValueError("A training fold is missing a rail condition.")
            predictions["Rail only"][test[rails[test] == rail]] = int(actual[reference].mean() >= 0.5)

        inner_car_folds = np.array_split(cars[cars != held_car], 3)
        for name in feature_sets:
            candidates = []
            for alpha, gamma in PARAMETER_GRID:
                inner_predictions = np.zeros(len(trucks), dtype=int)
                for validation_cars in inner_car_folds:
                    validation = train[np.isin(car_ids[train], validation_cars)]
                    fit = train[~np.isin(car_ids[train], validation_cars)]
                    inner_predictions[validation] = predict(name, fit, validation, alpha, gamma)
                score = classification_metrics(actual[train], inner_predictions[train])["balanced_accuracy"]
                candidates.append((score, alpha, gamma))
            # On tied scores, prefer stronger regularization and a broader kernel.
            _, alpha, gamma = max(candidates, key=lambda value: (value[0], value[1], -value[2]))
            predictions[name][test] = predict(name, train, test, alpha, gamma)
            selected.append({"held_car": held_car, "model": name, "alpha": alpha, "gamma": gamma})

    metrics = pd.DataFrame([
        {"target": target, "model": name, **classification_metrics(actual, predicted)}
        for name, predicted in predictions.items()
    ])
    assessments = trucks[TRUCK_KEY].copy()
    assessments["actual"] = actual
    for name, predicted in predictions.items():
        assessments[name] = predicted
    return metrics, assessments, pd.DataFrame(selected)


def paired_car_intervals(assessments, n_bootstrap=2000, seed=42, comparisons=None):
    """Describe score variation by resampling complete held-out car blocks.

    The same draws are used for all models. These percentile intervals use
    fixed out-of-fold predictions; they do not include model retraining,
    exploratory feature selection, or parameter-selection uncertainty.
    """
    if comparisons is None:
        comparisons = MODEL_COMPARISONS
    if n_bootstrap < 1:
        raise ValueError("n_bootstrap must be positive.")
    compared_models = [name for added, base, _ in comparisons for name in (added, base)]
    required = set(TRUCK_KEY + ["actual"] + compared_models)
    if not required.issubset(assessments.columns):
        raise ValueError("Assessment predictions are missing required columns.")
    if assessments.duplicated(TRUCK_KEY).any():
        raise ValueError("Assessment predictions contain duplicated keys.")
    model_names = [column for column in assessments
                   if column not in TRUCK_KEY + ["actual"]]
    actual = assessments.actual.to_numpy()
    for name in model_names:
        classification_metrics(actual, assessments[name].to_numpy())

    cars = np.sort(assessments.Car.unique())
    if len(cars) < 2:
        raise ValueError("At least two cars are needed for car resampling.")
    counts = np.zeros((len(cars), len(model_names), 4), dtype=int)
    for car_index, car in enumerate(cars):
        group = assessments.loc[assessments.Car == car]
        observed = group.actual.to_numpy()
        for model_index, name in enumerate(model_names):
            predicted = group[name].to_numpy()
            counts[car_index, model_index] = [
                ((observed == 0) & (predicted == 0)).sum(),
                ((observed == 0) & (predicted == 1)).sum(),
                ((observed == 1) & (predicted == 0)).sum(),
                ((observed == 1) & (predicted == 1)).sum(),
            ]

    generator = np.random.default_rng(seed)
    draws = generator.integers(0, len(cars), size=(n_bootstrap, len(cars)))
    sampled = counts[draws].sum(axis=1)
    negative_count = sampled[:, :, 0] + sampled[:, :, 1]
    positive_count = sampled[:, :, 2] + sampled[:, :, 3]
    valid = ((negative_count > 0) & (positive_count > 0)).all(axis=1)
    sampled = sampled[valid]
    if len(sampled) == 0:
        raise ValueError("No bootstrap samples contain both classes.")
    scores = 0.5 * (
        sampled[:, :, 0] / negative_count[valid]
        + sampled[:, :, 3] / positive_count[valid]
    )
    score_rows = []
    for index, name in enumerate(model_names):
        lower, upper = np.quantile(scores[:, index], [0.025, 0.975])
        point = classification_metrics(actual, assessments[name].to_numpy())["balanced_accuracy"]
        score_rows.append({"model": name, "balanced_accuracy": point,
                           "lower_95": lower, "upper_95": upper,
                           "valid_draws": len(sampled)})

    comparison_rows = []
    for added, base, label in comparisons:
        added_index = model_names.index(added)
        base_index = model_names.index(base)
        differences = scores[:, added_index] - scores[:, base_index]
        lower, upper = np.quantile(differences, [0.025, 0.975])
        point = (
            score_rows[added_index]["balanced_accuracy"]
            - score_rows[base_index]["balanced_accuracy"]
        )
        per_car_difference = (
            (assessments[added] == assessments.actual).astype(int)
            - (assessments[base] == assessments.actual).astype(int)
        ).groupby(assessments.Car).mean()
        comparison_rows.append({
            "comparison": label, "change_in_balanced_accuracy": point,
            "lower_95": lower, "upper_95": upper,
            "cars_with_fewer_errors": int((per_car_difference > 0).sum()),
            "cars_with_more_errors": int((per_car_difference < 0).sum()),
            "cars_tied": int((per_car_difference == 0).sum()),
        })
    return pd.DataFrame(score_rows), pd.DataFrame(comparison_rows)
