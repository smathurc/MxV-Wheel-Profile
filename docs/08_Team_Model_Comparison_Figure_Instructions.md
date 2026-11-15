# Figure Reproduction — Team Model Comparison

**Source notebook:** `notebooks/08_team_model_comparison.ipynb`  
**Installation and setup:** See `INSTALL.md` for the required environment and project setup.  
**Use:** Figures are presented in the project presentation and/or final report.

The notebook loads the assessment data through `load_benchmark_data()` in `src/team_data.py`. It evaluates models with leave-one-car-out validation, computes held-out performance metrics, and summarizes hunting outcomes by rail profile. The three charts below are created in the **“Rail patterns and performance figures”** section. The acceleration and displacement model comparisons are two panels of one saved image.

## Figure 1 — Acceleration Hunting: Model Comparison

**Output:** Left panel of `outputs/team_comparison/model_comparison.png` (also saved as `.pdf`).

This horizontal bar chart compares the **held-out balanced accuracy** of the evaluated models for acceleration-based hunting. Each bar represents one model, and the horizontal axis runs from 0 to 1. The dashed line at **0.5** provides a reference level. Balanced accuracy averages the model's recall for hunting and non-hunting observations.

**How it was generated:** The notebook creates held-out predictions by leaving out an entire car for each evaluation fold. It calculates `balanced_accuracy` for each model and outcome in the `metrics` table. The plotting code selects rows with `target == "acceleration_hunted"`, uses `plot.barh()` to draw the bars, and adds the dashed reference line using `axvline()`.

## Figure 2 — Displacement Hunting: Model Comparison

**Output:** Right panel of `outputs/team_comparison/model_comparison.png` (also saved as `.pdf`).

This horizontal bar chart compares the same models using **displacement-based hunting** as the outcome. The axis, accuracy measure, and **0.5** reference line match Figure 1, making the two outcome types easy to compare.

**How it was generated:** The notebook calculates displacement-based held-out balanced accuracy in the same `metrics` table. The plotting code selects rows with `target == "displacement_hunted"` and draws a second horizontal bar chart using `plot.barh()`. Both model comparison panels are arranged side by side with `plt.subplots(1, 2)` and saved together using `fig.savefig()`.

## Figure 3 — Hunting Rates by Rail Condition

**Output:** `outputs/team_comparison/rail_hunting.png` (also saved as `.pdf`).

This grouped bar chart shows the **fraction of truck assessments classified as hunting** for each of the seven rail profiles. Each rail profile has two bars: one for acceleration-based hunting and one for displacement-based hunting. The vertical axis ranges from 0 to 1.

**How it was generated:** The notebook groups the assessment table by `Rail_Profile` and calculates the mean of the binary `acceleration_hunted` and `displacement_hunted` columns. Those means are the observed hunting fractions. The two columns are displayed using `plot.bar()`, and the figure is saved using `fig.savefig()`.

**Interpretation:** Differences among rail profiles describe the observations in this dataset. Because the same trucks are evaluated under multiple rail conditions, the chart does not establish that a rail profile independently causes hunting.

## Reproducing the Figures

Follow **`INSTALL.md`** for installation and project setup, then run `notebooks/08_team_model_comparison.ipynb` from a fresh kernel. The notebook reads project data from `data/` or the directory specified by `HUNTING_DATA_DIR`, calculates the results, and saves the figures in `outputs/team_comparison/`.

The run also saves supporting tables, including `metrics.csv` and `rail_findings.csv`, in the same output directory. The plots are generated at **300 dpi** for PNG output and are also saved as PDF files.
