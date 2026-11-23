# Contact features and empty-car hunting

We test whether contact measurements improve predictions over equivalent
conicity and rail profile. We use kernel ridge classification with a Gaussian
kernel. The model fits signed labels with regularized least squares and
returns decision scores.

The notebook starts from the team's merged CSV and the contact-point difference
CSV. Keep approved inputs in the local `data` folder, or set `HUNTING_DATA_DIR`
in your environment. The contact experiment does not need profile files or MATLAB.

Each row represents one truck on one rail profile. The join retains the
identifiers for both wheelsets. We start with rail profile and add mean
conicity, the difference in wheelset conicity, and the three contact
measurements in stages. For each contact measurement, we take the larger
wheelset value and apply `log1p`. MxV Rail still needs to confirm the fields
and units.

Two outcome definitions are evaluated separately:

- Truck acceleration: the shared empty-truck acceleration speed is below 80 mph.
- Axle displacement: at least one of the truck's two empty-axle displacement
  speeds is below 80 mph. This is a sensitivity endpoint. The calculated speed
  matches the supplied truck-speed summary; the partner should still confirm
  the preferred criterion for the research question.

The 80 mph value represents no hunting recorded within the tested speed range.
It is not treated as an observed onset speed for regression. TD24-022 discusses
decreasing-speed simulations and treats displacement as the more direct hunting
criterion. These target definitions should be agreed with the partner before
choosing a final model.

Every outer fold holds out one complete car. Three grouped inner folds select
regularization and kernel width from a small fixed grid. Numeric scaling uses
training rows only; rail categories are fixed at profiles 1–7. There is no
imputation or global feature selection. Gaussian distances have a fixed divisor
of nine for all four models, so retained features keep the same distance weight.
Each feature set gets its own tuning within the same grouped folds. These are
predictive comparisons between complete pipelines, not causal feature effects.

Use balanced accuracy alongside hunting recall and the confusion counts. The
fixed always-hunting baseline has 50% balanced accuracy when both classes occur.
The rail-only baseline estimates the majority outcome separately for each rail
using training cars. Avoid relying on accuracy alone.

The notebook reports four paired comparisons: adding mean conicity, adding
wheelset mismatch, adding contact features, and comparing the full model with
the mean-conicity model. That last comparison uses mean conicity and rail
profile as the baseline for the full model.

The car-bootstrap ranges use 2,000 resamples with seed 42. Each draw samples
whole cars with replacement, keeping their truck and rail assessments together.
All models use the same draws. This describes variation in fixed out-of-fold
predictions; it excludes retraining and feature-selection uncertainty and is
not a formal significance test. Samples containing one target class are excluded
from balanced-accuracy calculations and the valid sample count is returned.

We chose features after looking at these cars and the partner's materials.
The same cars appear in the grouped validation, so treat the scores as
exploratory. TD24-022 studied related contact and conicity descriptors. Our
comparison gives MxV Rail a benchmark to test on additional cars.

We test the three processed contact summaries as a group. They may be
correlated, so the comparison cannot separate their physical effects.
We used the same seven rail profiles throughout.

## Running the notebook

Use the Python environment described in the team's `INSTALL.md`. This code
needs only NumPy and pandas; the interactive notebook also needs Jupyter.
Open `notebooks/03_contact_hunting_model.ipynb` and run its cells in order.
The notebook reads the source files and calculates features in memory. It does
not write source data or result files.

`notebooks/04_profile_shape_extension.ipynb` adds one separate comparison. It
also reads the measured `Car*_Axle*[LR].WHL` exports from
`Profiles/Candidate wheel profiles`. These files supply coordinate-based tread
descriptors: mean slope, mean RMS departure from a line, and the larger
left/right RMS difference across the two wheelsets. The comparison adds all
three to mean conicity and rail identity using the same validation procedure.

The shared x window is 60–110, sampled at one-unit spacing and vertically
centered at x=85. The reader checks coverage and monotonicity before interpolation.
It does not repair or overwrite source profiles. Units, alignment, and export
reconstruction need confirmation; these descriptors should not be interpreted
as physical curvature or equivalent conicity. Individual feature effects are
not estimated. The additional notebook also checks the gain after omitting
each car's fixed predictions from scoring; this is not a retraining experiment.

Run the synthetic checks from the repository root:

```sh
python -m unittest discover -s tests -v
```

## Before sharing code

Keep partner inputs and generated results local. The notebook is distributed
with empty outputs and no partner measurements or saved results in its prose.
After running it, clear all outputs and save before sharing; also check for
rendered tables, widget state, or attachments. The synthetic checks verify
that the shared notebook has no saved code outputs or widget state.

Assessment predictions and model choices contain partner-derived information.
Keep any local exports and source documents out of a GitHub commit.

## References

- Ulrich Spangenberg, MxV Rail, TD24-022, *Wheel-Rail Interaction Affecting Hunting
  Stability*, October 2024. The supplied digest informs target interpretation.
- [Kernel ridge method](https://scikit-learn.org/stable/modules/kernel_ridge.html)
- [Grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
