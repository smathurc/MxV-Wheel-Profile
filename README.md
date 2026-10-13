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
more frequent hunting and lower critical speeds. We will begin by
examining standard wear measurements, then investigate whether
additional descriptions of profile shape help explain differences
in stability.

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

The project overview describes 29 unique trucks evaluated against seven
worn rail profiles, resulting in 203 stability assessments. These
assessments cover 14 cars with naturally worn wheel profiles and one
car with unworn wheel profiles.

The planned data sources include:

- Critical speeds from NUCARS hunting simulations
- Standard wheel profile wear measurements
- Equivalent conicity for wheel-rail combinations
- Measured two-dimensional wheel and rail profiles
- A feature schema describing the data columns

The data is provided in CSV or Excel files and requires linking
information across sources. We will document identifiers, units, and
relationships between datasets before combining them.

Wheels operate together within wheelsets and trucks. Our analysis will
account for that structure rather than assume each wheel or assessment
is an independent observation.

Project data is subject to the applicable NDA and IP agreement.
Restricted data is not included in this repository. Team members
should use the approved data storage and access process.

## Planned Approach

1. Inspect the datasets, confirm their structure, and document variables
   and units.
2. Check missing values, duplicates, unusual measurements, and the
   identifiers needed to join files.
3. Explore relationships between standard wear measurements, critical
   speed, and hunting behavior.
4. Develop and evaluate additional wheel profile shape descriptors.
5. Consider clustering and predictive modeling if the data and initial
   findings support those methods.
6. Communicate findings through visualizations and document the steps
   needed to reproduce the analysis.

Predictive modeling is a possible extension rather than a guaranteed
outcome. Descriptive analysis and clear visualizations will remain
useful if the available data does not support reliable prediction.

## Repository Structure

```text
.
├── README.md
├── INSTALL.md
├── .gitignore
├── requirements.txt
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
- `requirements.txt`: Python dependencies used by the project.
- `INSTALL.md`: Environment setup and reproduction instructions.

A license file and any required unsigned IP agreement will be added
after the applicable terms are confirmed.

## Getting Started

See [INSTALL.md](INSTALL.md) for setup instructions.

Follow the setup guide, then run [our demo](notebooks/demo.ipynb). We make example data in the notebook and use it for plots and logistic regression. The demo uses made-up data, so these results are only for checking that the code runs.

## Expected Deliverables

- Exploratory analysis of wheel profile measurements and hunting behavior
- Evaluation of standard and additional profile shape descriptors
- Visualizations and a summary of findings for MxV Rail
- Documented code that allows authorized users to reproduce the results
- Course milestone submissions and a final report

A stretch goal is a prototype interface for loading new data, rerunning
the analysis, and displaying results.

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

Use and distribution of project materials are governed by the
applicable MxV Rail agreements. The team will confirm the appropriate
license wording with the instructors and community partner before
adding a license file.

## Acknowledgments

We thank MxV Rail and the CMSE 495 instructional team for their guidance
and support throughout this project.
