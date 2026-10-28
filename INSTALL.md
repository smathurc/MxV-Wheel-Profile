# Installation and Setup

This guide shows how to install the packages and run our demo. The demo makes its own example data, so you do not need access to the partner data.
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

```bash
python -m pip install -r requirements.txt
python -m notebook
```

In the browser, open `notebooks/demo.ipynb`. Choose **Kernel → Restart Kernel and Run All Cells**. Wait for all cells to finish.

The notebook uses pandas and NumPy for data handling, Matplotlib for figures, and scikit-learn for modeling. Jupyter Notebook and ipykernel provide the notebook interface. openpyxl supports the original Excel analysis; nbclient and nbformat support execution verification.

## 4. Verify success

The first cell reports **560 synthetic rows, 20 invented cars, and 280 truck/rail assessments**. You should see hunting-rate and wear plots, a classification report, and a confusion matrix. The last cell prints:

```text
Demo completed successfully: synthetic data, two plots, grouped split, and one model ran.
```

Check that all cells finish without errors. The model scores use made-up data, so they do not show how well the model works on real equipment.

## Example data

You do not need to download example data. `demo.ipynb` makes it using random seed 42 each time you restart and run all cells. We do not read partner files or save a dataset in this demo.

## Authorized partner analysis

To run the original notebooks, get the project data through our approved team access process. Keep the data and notebook outputs that show it out of GitHub.

- `01_data_overview.ipynb`: expects `data/Eq_Con_Fit_Results.xlsm` and `data/Profiles/`, relative to the repository root.
- `02_empty_car_validation.ipynb`: expects `data/final_merged_data.csv` (or its documented fallback filename).
- `CAPSTONE DATA MERGE WORK AND INFO.ipynb`: currently uses `Data/` relative to its working directory and produces `Data/final_merged_data.csv`.
- `verbana3_EDA_and_modeling.ipynb`: currently reads `final_merged_data.csv` from its working directory.
- `03_rail_profiles.ipynb`: expects `data/Profiles/Rail profiles/` and `data/final_merged_data.csv`, relative to the repository root.

The original notebooks use the data paths listed above. For the installation check, run `demo.ipynb`. Our `.gitignore` excludes the `data/` folder at the repository root.
