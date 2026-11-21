# Notebooks

Follow [INSTALL.md](../INSTALL.md), then open `demo.ipynb` in Jupyter and restart
and run all cells. The demo generates its own data. Every partner-data notebook
uses the same root `data/` folder and can run independently.

- `00_capstone_data_merge_work_and_info.ipynb`: rebuild the merged table from
  the wear and simulation workbooks; write regenerated CSVs to `outputs/data/`.
- `01_data_overview.ipynb`: inspect workbook coverage and profile files.
- `02_empty_car_validation.ipynb`: check truck/rail groups and hollow-wear differences.
- `03_contact_hunting_model.ipynb`: compare conicity and contact summaries using
  car-held-out kernel ridge.
- `03_rail_profiles.ipynb`: describe rail geometry, conicity and hunting patterns.
- `04_profile_shape_extension.ipynb`: test the added tread-shape descriptors.
- `05_Fit_File_Analysis.ipynb`: prepare FIT sequences and run the wheel-split LSTM trial.
- `06_nguyenaa_randomforest_and_modeling.ipynb`: compare original and expanded
  RF inputs, including wear summaries shared with Dom; group folds by truck.
- `07_verbana3_EDA_and_modeling.ipynb`: EDA, logistic regression, XGBoost and
  model explanations; group predictive splits by car.
- `08_team_model_comparison.ipynb`: compare shared model families and feature
  questions on common truck/rail observations with complete cars held out.

Personal-notebook scores use different feature lists, row units and splits.
Use notebook 08 for the common comparison. Figure exports and their source cells
are listed in [INSTALL.md](../INSTALL.md#4-reproducing-the-figures).
