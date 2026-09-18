# Analysis Notebooks

This folder will contain Jupyter notebooks for exploring the MxV Rail
wheel profile data and hunting simulation results.

Our initial analysis will focus on understanding the datasets,
checking data quality, and exploring relationships between wheel
wear measurements and critical speed.

## Naming Notebooks

Use numbered, descriptive filenames to make the analysis order clear.
For example:

- 01_data_overview.ipynb
- 02_data_quality_and_joins.ipynb
- 03_wear_measurements_and_hunting.ipynb

These are suggested filenames; the notebooks have not been created yet.

## Documenting the Analysis

Each notebook should explain:

- Its purpose and research question
- Required datasets and relevant variables
- Data preparation steps and assumptions
- Findings, limitations, and follow-up questions

Keep track of measurement units and whether observations represent
individual wheels, wheelsets, trucks, or wheel-rail assessments.

## Before Committing

- Use relative paths instead of paths specific to your computer.
- Keep restricted datasets in the local data/ folder.
- Remove unnecessary outputs and any confidential information.
- Check that the notebook runs in order once its required data and
  dependencies are available.

Move reusable functions into src/ as the analysis develops.
