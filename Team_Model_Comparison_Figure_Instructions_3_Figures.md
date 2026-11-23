# Team Model Comparison Figures

Follow [INSTALL.md](INSTALL.md), then restart the kernel and run all cells in
[notebook 08](notebooks/08_team_model_comparison.ipynb). Cell 11 saves both
figures as PNG (300 dpi) and PDF under `outputs/team_comparison/`.

| File stem | What it shows |
|---|---|
| `model_comparison` | Balanced accuracy on held-out cars. The left panel uses acceleration to label hunting, and the right uses displacement. |
| `rail_hunting` | Observed hunting fractions across the seven rail profiles, with one bar per criterion on each rail. |

Balanced accuracy averages recall for hunting and no hunting. The dashed 0.5
line shows the score of an always-hunting predictor when both classes occur.
The same trucks appear under several rail conditions, so the rail chart
describes those observations and cannot isolate the effect of rail shape.

The run also saves `metrics.csv` and `rail_findings.csv` in the same folder.
