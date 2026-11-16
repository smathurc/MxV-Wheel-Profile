# Installation verification

## Full notebook workflow — November 16, 2026

Tested on macOS arm64 with Python 3.12.3. A new environment installed
`requirements-all.txt` with `constraints-comparison.txt`. All 39 synthetic tests
passed. `python scripts/run_notebooks.py` completed all 11 notebooks in separate
fresh kernels using the supplied Teams data under root `data/`, with no path
edits or notebook-local input copies. The earlier audit also checked that input
hashes were unchanged.

The run regenerated the merged CSV, profile-shape exports and shared comparison
outputs. Executed copies and the execution summary remain private under
`outputs/notebooks/`. The model definitions, splits and feature calculations
were unchanged. FIT training remains nondeterministic as documented.

The final review rerun passed all 11 notebooks and all 39 tests. Notebook/source
validation passed, as did the installed dependency check. The prose and plot-label
review preserved model constructors, settings and split/prediction calls.

| Platform | Verification |
|---|---|
| Apple Silicon Mac, Python 3.12 | Full install, 39 tests and all 11 notebooks passed |
| Windows x64, Python 3.12 | All 13 pinned packages have compatible wheels; full workflow not run |
| Linux x86_64, Python 3.12 | All 13 pinned packages have compatible wheels; full workflow not run |
| Intel Mac | Full environment unsupported: pinned TensorFlow has no Intel Mac build |

Wheel availability was checked against PyPI on November 16, 2026. It does not
verify notebook execution on Windows/Linux. Earlier demo-only checks are
preserved below.

## Local execution

Passed October 13, 2026 on macOS using Python 3.12.3. Installed requirements.txt into a fresh temporary virtual environment. All demo cells ran from /tmp with no project data present. The final success message appeared. Notebook structure validation passed.

Tested package versions:
- pandas: 2.3.3
- numpy: 2.5.4
- matplotlib: 3.11.2
- scikit-learn: 1.9.1
- openpyxl: 3.1.5
- notebook: 7.6.3
- ipykernel: 6.31.0
- nbclient: 0.11.0
- nbformat: 5.11.1

## Second-computer test

- Tester: Brandon Grimes
- Date: 10/13/26
- Operating system: Windows 10
- Python version: 3.13.9
- Followed INSTALL.md from a fresh clone: True
- All cells completed and final success message appeared: True
- Corrections needed: None
