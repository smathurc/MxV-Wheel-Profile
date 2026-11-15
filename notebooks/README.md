# Notebooks

Start with `demo.ipynb` to check the installation. It generates its own example data and runs without partner files. Follow `INSTALL.md` at the repository root.

The other notebooks use approved project data:

- `00_capstone_data_merge_work_and_info`: combines wheel wear and simulation results.
- `01_data_overview.ipynb`: inspects the workbook and profile files.
- `02_empty_car_validation.ipynb`: checks the merged rows and compares left/right hollow wear.
- `03_contact_hunting_model.ipynb`: tests wheelset mismatch and contact measurements
- `03_rail_profiles.ipynb`: reads the seven rail profiles, measures how rounded the rail head is, and compares that with conicity and hunting.
- `04_profile_shape_extension.ipynb`: tests tread-shape measurements add information
- `05_Fit_File_Analysis.ipynb`: reads the fit files and analyzes them.
- `06_nguyenaa_randomforest_and_modeling`: creates a RF classifier to analyze selected features.
- `07_verbana3_EDA_and_modeling.ipynb`: creates exploratory plots and logistic regression models.
- `08_team_model_comparison.ipynb`: Comparisons of wheel-wear and profile-shape findings.
- `demo.ipynb`: runs a short demo of the project inputs and model.

Input paths for these notebooks are listed in `INSTALL.md`.
