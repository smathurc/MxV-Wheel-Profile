# Contact features and empty-car hunting

This experiment checks whether wheel-rail contact measurements add useful
information to equivalent conicity and rail profile. It uses nonlinear kernel
ridge classification with a Gaussian kernel. The model fits signed labels using
regularized least squares; its scores are not probabilities.

The notebook starts from the team's merged CSV and the contact-point difference
CSV. Keep approved inputs in the local `data` folder, or set `HUNTING_DATA_DIR`
in your environment. The contact experiment does not need profile files or MATLAB.

Each observation is one truck under one rail condition. Both wheelsets remain
traceable through the join. The four kernel models add features in stages:
rail identity; then mean conicity; then wheelset conicity difference; then the
three contact measurements. Contact features use the maximum across the two
wheelsets and `log1p` to reduce the influence of large values. The schema and
units still need partner review.

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
mean conicity alone. The last comparison prevents a gain over a weak intermediate
model from looking like an improvement over the simpler alternative.

The car-bootstrap ranges use 2,000 resamples with seed 42. Each draw samples
whole cars with replacement, keeping their truck and rail assessments together.
All models use the same draws. This describes variation in fixed out-of-fold
predictions; it excludes retraining and feature-selection uncertainty and is
not a formal significance test. Samples containing one target class are excluded
from balanced-accuracy calculations and the valid sample count is returned.

These are exploratory comparisons on a small set of cars. Feature ideas came
from inspection of these data and the partner's materials; nested tuning does
not undo that exploratory selection. This is not an external validation set or
a causal analysis. The public digest already studied related contact and
conicity descriptors, so this experiment should be presented as a benchmark
and follow-up question, rather than a discovery of a new mechanism.

The features are processed geometry summaries, not measured raw-profile shape
descriptors. The three contact summaries may be strongly correlated. This
experiment evaluates them as a group and does not rank them as independent
physical explanations. Nothing here supports prediction on new rail types or
real-world deployment.

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

Run the synthetic checks from this folder:

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
