# Installation and Setup

Use Python 3.12. After setup, every notebook reads the root `data/` folder
without path edits.

The full notebook workflow requires Windows x64, an Apple Silicon Mac
(M1 or newer, macOS 12+), or Linux x86_64 with glibc 2.28+ (such as Ubuntu 22.04+).
**Intel Macs are not supported by this setup** because the pinned
[TensorFlow release](https://pypi.org/project/tensorflow/2.21.0/) has no Intel
Mac build. No GPU is required.

## 1. Clone and install

Install [Python 3.12](https://www.python.org/downloads/) and
[Git](https://git-scm.com/downloads), then:

```bash
git clone https://github.com/smathurc/MxV-Wheel-Profile.git
cd MxV-Wheel-Profile
```

Create and activate an environment:

**macOS / Linux**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

On Windows, enable Python's PATH option during installation. If PowerShell
blocks activation, use Command Prompt with `.venv\Scripts\activate.bat`.
Activate the environment each time you open a terminal.

On macOS, XGBoost needs OpenMP: run `brew install libomp` if you use Homebrew,
or follow the [XGBoost installation guide](https://xgboost.readthedocs.io/en/stable/install.html).
On Windows, install the [Microsoft Visual C++ x64 Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
if it is not already installed. Linux needs the OpenMP runtime; on Ubuntu/Debian,
install it with `sudo apt install libgomp1` if it is missing.

Install all notebook dependencies:

```bash
python -m pip install -r requirements-all.txt -c constraints-comparison.txt
```

This installs the packages for every notebook, including XGBoost, SHAP and
TensorFlow. The constraints file specifies the package versions used in our
verified run.

## 2. Download the data

In the private **-MxV-Wheel-Profile** Teams channel, open
**Shared → Documents → Data**. Download the workbook, merged CSV and complete
`Profiles` folder. Extract them into the repository's `data/` folder:

```text
MxV-Wheel-Profile/
└── data/
    ├── Eq_Con_Fit_Results.xlsm
    ├── final_merged_data.csv
    └── Profiles/
        ├── Candidate wheel profiles/
        │   ├── 2023-06-13 - Wheel wear results.xlsx
        │   ├── Car1_Axle1.fit          # all 56 measured FIT files
        │   └── Car1_Axle1L.WHL        # all 112 measured WHL files
        ├── Rail profiles/             # all 11 BAN files and supplied companions
        └── WNTs/
            └── 2023-06-21 - Hunt_Disp_Max_CP_Difference.csv
```

Keep the original names and folder structure, without an extra `data/Data/`
layer. `final_merged_data(in).csv` is also accepted, and the wheel-wear workbook
may instead be directly under `data/`. Keep data files out of `notebooks/`.

Professors have approved access to the NDA data. Keep inputs and generated
results private. The synthetic demo needs no partner data.

## 3. Verify and run

Choose either Jupyter or the terminal. **Jupyter is the recommended option**
for following the demo and viewing the figures as you run each notebook.

### Jupyter Notebook (recommended)

From the repository root with the environment active, launch Jupyter:

```bash
python -m notebook
```

Open `notebooks/demo.ipynb` and choose **Restart Kernel and Run All Cells**.
The demo generates 560 rows for 20 invented cars and 280 truck/rail assessments,
then displays plots and model results. Its last cell prints:

```text
Demo completed successfully: synthetic data, two plots, grouped split, and one model ran.
```

Once the demo finishes without errors, open the project notebook you want
to run and use the same **Restart Kernel and Run All Cells** option. Each
notebook runs independently; the Teams download already includes the merged
CSV, so you do not need to run the merge notebook first.

### Terminal (alternative)

From the repository root with the environment active, run the synthetic tests
and demo:

```bash
python -m unittest discover -s tests -v
python scripts/run_notebooks.py demo.ipynb
```

All tests should pass. To run all notebooks in separate fresh kernels:

```bash
python scripts/run_notebooks.py
```

To run just the profile or shared comparison:

```bash
python scripts/run_notebooks.py 04_profile_shape_extension.ipynb
python scripts/run_team_comparison.py
```

Executed copies and `execution_summary.json` are saved under `outputs/notebooks/`.
The merge writes regenerated CSVs to `outputs/data/`; analyses read the supplied
CSV in `data/`. Source notebooks and downloaded inputs are unchanged.
Allow several minutes for the full run, including FIT training.

A successful terminal run finishes every selected notebook without errors. The
execution summary records each notebook's status and runtime.

## 4. Reproducing the figures

Notebooks 04 and 08 generate the profile and model comparisons for the report
and presentation. Run them using section 3. Their cells contain preprocessing,
analysis, plotting, titles, axis labels and export code; methods and limitations
are explained in the notebooks.

Notebook 04 uses the merged CSV, contact table and WHLs to calculate tread-shape
descriptors and compare predictions on held-out cars. It checks the source joins,
interpolates the tread window x=60–110 and centers profiles at x=85. Coordinate
units and interpretation remain provisional.

Notebook 08 also uses the BAN files and compares the prespecified models on
common truck/rail assessments. Both comparisons hold out complete cars and fit
scaling on training data. Acceleration and displacement remain separate outcomes;
the notebooks explain the model settings, bootstrap calculations and limitations.

| Figure | Notebook / cell* | Output stem under `outputs/` |
|---|---|---|
| Within-car shape and displacement-hunting differences, Truck 2 minus Truck 1 | 04 / 8 | `profile_shape/within_car_shape_comparison` |
| Balanced accuracy with and without shape, by endpoint | 04 / 9 | `profile_shape/profile_shape_performance` |
| Acceleration and displacement model comparison | 08 / 11 | `team_comparison/model_comparison` |
| Hunting fractions by rail condition | 08 / 11 | `team_comparison/rail_hunting` |

Each stem produces a 300 dpi `.png` and a vector `.pdf`. Notebook 04 also saves
`_plot_data.csv` for each stem. Notebook 08 saves `metrics.csv`, `rail_findings.csv`
and supporting predictions, comparisons and a run manifest in its output folder.

Other exploratory plots appear in their notebooks and executed copies; they
are not automatically saved as individual images. To inspect a completed run
without retraining, open its executed notebook and tables. Share completed runs
or intermediates through approved private Teams storage. Recompute after inputs
or code change. FIT training is unseeded, so its scores can vary between runs.

*Cells are numbered from 1, counting Markdown cells.*

## Troubleshooting

- **Missing input:** check the extracted data layout above; the error names the file.
- **Missing package:** activate `.venv`, repeat the install command and relaunch Jupyter.
- **Missing `libomp` on macOS:** install OpenMP using the link in section 1.

Existing external-data workflows can use `HUNTING_DATA_DIR` or the runner's
`--data-dir "/path/to/Data"` option. Neither is needed for the default layout.
See [docs/install_verification.md](docs/install_verification.md) for the verified
macOS run. The full workflow has not been tested on Windows/Linux.
