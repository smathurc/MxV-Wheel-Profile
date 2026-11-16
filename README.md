# Identifying Wheel Profile Characteristics Associated with Hunting

**Michigan State University | CMSE 495 Capstone | Fall 2026**  
**Community Partner: MxV Rail**

## Project Overview

We are a team of Computational Data Science seniors at Michigan State
University working with MxV Rail to study how worn wheel profiles relate
to rail vehicle stability.

Hunting refers to unstable motion of a rail vehicle on straight track.
The speed at which a vehicle becomes unstable is called its critical
speed. As wheels and rails wear, their shapes change, which can reduce
the critical speed. If that speed falls below the vehicle's operating
speed, hunting can occur during normal operation.

Our goal is to identify wheel profile characteristics associated with
more frequent hunting and lower critical speeds. We compare standard wear
measurements, contact summaries and tread-shape descriptors, using descriptive
plots and grouped predictive checks.

## Research Questions

- How do standard measurements, such as flange thickness, flange height,
  hollow wear, and hollow wear position, relate to hunting behavior?
- Can additional features, such as profile gradient and curvature,
  describe relevant differences in wheel shape?
- Does similarity between wheel profiles on the same axle or within
  the same truck relate to stability?
- Can profiles with similar hunting behavior be grouped together?
- Which characteristics appear most useful for distinguishing profiles
  with different levels of hunting?

## Data

The source workbook contains 203 truck/rail assessments, including an unworn
reference. Our measured-car merge excludes that reference and contains 392
axle/rail rows: 14 cars, 28 trucks and 196 truck/rail assessments under seven
rail conditions.

The data sources include:

- Critical speeds from NUCARS hunting simulations
- Standard wheel profile wear measurements
- Equivalent conicity for wheel-rail combinations
- Measured two-dimensional wheel and rail profiles

CSV/Excel results are joined to the supplied wheel and rail files by their
car, axle/truck and rail identifiers. The notebooks document the joins and
flag unresolved units or source conventions.

Wheels operate together within wheelsets and trucks, and the same vehicles
are assessed under several rails. The shared comparison holds out complete
cars. Personal notebooks identify their own observation and split units.

Project data is subject to the applicable NDA and IP agreement.
Restricted data is not included in this repository. Team members
should use the approved data storage and access process.

## Approach

1. Inspect the datasets, confirm their structure, and document variables
   and units.
2. Check missing values, duplicates, unusual measurements, and the
   identifiers needed to join files.
3. Explore relationships between standard wear measurements, critical
   speed, and hunting behavior.
4. Develop and evaluate additional wheel profile shape descriptors.
5. Compare predictive models and feature sets with the grouping appropriate
   to each experiment.
6. Communicate findings through visualizations and document the steps
   needed to reproduce the analysis.

The current notebooks include logistic regression, random forest, XGBoost,
kernel-ridge comparisons and a FIT/LSTM prototype. We interpret their scores
within the small sample and each validation design; they are not evidence
of a causal wheel characteristic or a deployment-ready predictor.

## Repository Structure

```text
.
├── README.md
├── INSTALL.md
├── .gitignore
├── requirements.txt
├── requirements-all.txt
├── scripts/
├── src/
├── notebooks/
├── docs/
├── example_data/
└── tests/
```

- `src/`: Reusable code for data processing, feature extraction,
  analysis, and visualization.
- `notebooks/`: Exploratory analyses with explanations of methods
  and findings.
- `docs/`: Data documentation, assumptions, decisions, and project reports.
- `example_data/`: Approved sample or synthetic data for demonstrating
  the workflow.
- `tests/`: Tests for data processing and analysis code.
- `requirements.txt`: Base dependencies; `requirements-all.txt` adds the full
  modeling environment.
- `scripts/`: Optional execution of selected or all notebooks in fresh kernels.
- `INSTALL.md`: Environment setup and reproduction instructions.

See [LICENSE](LICENSE) for the software license.

## Getting Started

See [INSTALL.md](INSTALL.md) for setup instructions.

Follow the setup guide, then run [our demo](notebooks/demo.ipynb). We make example data in the notebook and use it for plots and logistic regression. The demo uses made-up data, so these results are only for checking that the code runs.

## Reproducing the analysis

Follow [INSTALL.md](INSTALL.md) to install the full environment and place the
approved Teams download under `data/`. Then run any notebook from a fresh
kernel, or run all notebooks with `python scripts/run_notebooks.py`.
See [the figure instructions](INSTALL.md#4-reproducing-the-figures) for workflows and outputs.
No notebook path edits are needed.

## Expected Deliverables

- Exploratory analysis of wheel profile measurements and hunting behavior
- Evaluation of standard and additional profile shape descriptors
- Visualizations and a summary of findings for MxV Rail
- Documented code that allows authorized users to reproduce the results
- Course milestone submissions and a final report

## Team

- Jamie Le
- Sanskaar Mathur
- Dominic Verbanac
- Aaron Nguyen
- Brandon Grimes

## Community Partner

**MxV Rail**

- Primary contact: Ulrich Spangenberg
- Advisory team: Corey Pasta

## Team Workflow

We will use issues to track tasks, questions, and decisions. Substantial
changes will be submitted through branches and reviewed through pull
requests or merge requests.

Each team member will contribute throughout the semester. Before
committing, we will review changes, clear unnecessary notebook outputs,
and check that no restricted information is included.

## License and Data Restrictions

See [LICENSE](LICENSE) for software licensing. Partner data remains subject to the applicable MxV Rail agreements.

## Acknowledgments

We thank MxV Rail and the CMSE 495 instructional team for their guidance
and support throughout this project.
