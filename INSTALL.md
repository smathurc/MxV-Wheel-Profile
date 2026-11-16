# Installation and Setup

Use this guide to run the synthetic baseline. It generates a sample input table, makes two plots, and trains and tests one logistic regression model. You do not need partner data for the baseline. Section 5 shows how to run our shared team comparison, which uses the approved partner data.
Use Python 3.12. We tested the demo in a fresh environment on macOS with Python 3.12.3. See `docs/install_verification.md` for the results and tested package versions.

## 1. Install prerequisites and get the repository

Install [Python 3.12](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) for your operating system. On Windows, enable the Python installer option to add Python to PATH. Repository access is required if the repository is private.

```bash
git clone https://github.com/smathurc/MxV-Wheel-Profile.git
cd MxV-Wheel-Profile
```

## 2. Create and activate an isolated environment

Run these commands from the repository root.

macOS / Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt and `.venv\Scripts\activate.bat` instead. Activate the environment each time you open a new terminal. If Conda base is active, run `conda deactivate` before activating this environment.

## 3. Install dependencies and launch the demo

If you already have the project and its environment, open a terminal in the project folder and activate that environment. Run the install command below if the dependencies are missing or if `requirements.txt` has changed. Then launch Jupyter.

```bash
python -m pip install -r requirements.txt
python -m notebook
```

In the browser, open `notebooks/demo.ipynb`. Choose **Kernel → Restart Kernel and Run All Cells**. Wait for all cells to finish. If you see `ModuleNotFoundError`, check that Jupyter was started from the environment where you ran the install command. Stop the old Jupyter session and relaunch it from the active project environment.

The notebook uses pandas and NumPy for data handling, Matplotlib for figures, and scikit-learn for modeling. Jupyter Notebook and ipykernel provide the notebook interface. openpyxl supports the original Excel analysis; nbclient and nbformat support execution verification.

## 4. Verify success

The first cell reports **560 synthetic rows, 20 invented cars, and 280 truck/rail assessments**. You should see hunting-rate and wear plots, a classification report, and a confusion matrix. The last cell prints:

```text
Demo completed successfully: synthetic data, two plots, grouped split, and one model ran.
```

Check that all cells finish without errors. The model scores use made-up data, so they do not show how well the model works on real equipment.

## 5. Run the shared team comparison

`notebooks/08_team_model_comparison.ipynb` compares our models on the same truck assessments and held-out cars. It needs the partner data and the helper files in `src/`.

In the private course Teams channel, open **Shared → Documents → Data**. Download the workbook, the merged CSV, and the `Profiles` folder. Put them in the `data/` folder at the repository root and keep the folder layout:

```text
data/
├── Eq_Con_Fit_Results.xlsm
├── final_merged_data.csv
└── Profiles/
    ├── Candidate wheel profiles/
    ├── Rail profiles/
    └── WNTs/
```

With the project environment active, install the comparison dependencies, run the tests, and launch Jupyter from the repository root:

```bash
python -m pip install -r requirements-comparison.txt -c constraints-comparison.txt
python -m unittest discover -s tests -v
python -m notebook
```

`requirements-comparison.txt` adds XGBoost to `requirements.txt`. `constraints-comparison.txt` pins the main package versions we tested. TensorFlow is not needed for this notebook.

Open `notebooks/08_team_model_comparison.ipynb` and choose **Kernel → Restart Kernel and Run All Cells**. You can also run the same notebook from the terminal. It saves an executed copy to `outputs/08_team_model_comparison_executed.ipynb`.

```bash
python scripts/run_team_comparison.py
```

If your data is in another folder, change the `inputs` line in the notebook's first code cell, or pass the folder to the script:

```bash
python scripts/run_team_comparison.py --data-dir "path/to/Data"
```

On macOS, if importing XGBoost reports a missing `libomp`, follow the [XGBoost installation guide](https://xgboost.readthedocs.io/en/stable/install.html) to install the OpenMP runtime.

## 6. Verify the comparison

All tests should pass. The notebook should finish without errors and save these files under `outputs/team_comparison/`:

- `metrics.csv`, `paired_comparisons.csv`, `per_car_errors.csv`, `rail_findings.csv`, and `consolidated_findings.csv`
- `held_out_predictions.csv` and `kernel_settings.csv`
- `model_comparison.png`/`.pdf` and `rail_hunting.png`/`.pdf`
- `run_manifest.json`, which records the package versions and input file hashes

We ran the comparison in a fresh kernel on macOS with Python 3.12.3 on November 15, 2026. We have not verified it on Windows yet. These files contain partner results, so keep them out of GitHub. Our `.gitignore` excludes the `outputs/` folder.

## Example data

You do not need to download example data. `demo.ipynb` makes it using random seed 42 each time you restart and run all cells. We do not read partner files or save a dataset in this demo.

## Other project notebooks

The team keeps the source-file merge and the other modeling experiments in separate notebooks. The baseline starts with the merged-table format. It can be run by itself for a walkthrough or an installation check.

To run the partner-data notebooks, get the project data through our approved team access process. Keep the data and notebook outputs that show it out of GitHub.

- `01_data_overview.ipynb`: expects `data/Eq_Con_Fit_Results.xlsm` and `data/Profiles/`, relative to the repository root.
- `02_empty_car_validation.ipynb`: expects `data/final_merged_data.csv` (or its documented fallback filename).
- `00_capstone_data_merge_work_and_info.ipynb`: currently uses `Data/` relative to its working directory and produces `Data/final_merged_data.csv`.
- `03_contact_hunting_model.ipynb` and `04_profile_shape_extension.ipynb`: read the `data/` folder, or the folder set in `HUNTING_DATA_DIR`.
- `03_rail_profiles.ipynb`: expects `data/Profiles/Rail profiles/` and `data/final_merged_data.csv`, relative to the repository root.
- `05_Fit_File_Analysis.ipynb`: currently reads `Eq_Con_Fit_Results.xlsm` and the profile files from its working directory.
- `06_nguyenaa_randomforest_and_modeling.ipynb` and `07_verbana3_EDA_and_modeling.ipynb`: currently read `final_merged_data.csv` from their working directory.
- `08_team_model_comparison.ipynb`: see section 5.

Check the inputs and dependencies in the notebook you plan to run. Our `.gitignore` excludes the `data/` folder at the repository root.
