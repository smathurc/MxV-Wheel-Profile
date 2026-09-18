# Installation and Setup

This guide explains how to set up a local copy of our MxV Rail
capstone project.

The repository is currently being prepared for exploratory data
analysis. We will update these instructions as we add code and
confirm the environment needed to run it.

## Prerequisites

Before starting, make sure you have:

- Git installed
- Python installed
- Access to the team's repository
- Authorized access to the project data

We will record the tested Python version once our initial analysis
environment is established.

## 1. Clone the Repository

Open the repository in your browser and copy its HTTPS clone URL
from the Code menu.

In your terminal, run the following command, replacing
YOUR_REPOSITORY_URL with the copied URL:

```bash
git clone YOUR_REPOSITORY_URL
```

Enter the downloaded repository folder, replacing
YOUR_REPOSITORY_FOLDER with its name:

```bash
cd YOUR_REPOSITORY_FOLDER
```

## 2. Create a Virtual Environment

From the repository folder, run:

```bash
python -m venv .venv
```

If your computer uses python3 instead of python, run:

```bash
python3 -m venv .venv
```

Activate the environment using the command for your operating system.

### macOS or Linux

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Activate this environment each time you start a new terminal session
to work on the project.

## 3. Install Dependencies

With the environment activated, run:

```bash
python -m pip install -r requirements.txt
```

The requirements.txt file currently serves as a placeholder.
We will add the packages and tested versions used by our analysis
as code is introduced.

## 4. Set Up Project Data

Obtain the datasets through the team's approved access process.

Create a folder named data in the repository's top-level directory:

```bash
mkdir data
```

Store local project datasets in this folder. The .gitignore file
excludes data/ from version control.

Do not upload restricted datasets, signed agreements, credentials,
or other confidential materials.

We will document the expected input filenames and folder structure
when the initial data workflow is established.

## 5. Run the Analysis

An executable analysis workflow has not yet been added.

As the project develops, this section will include:

- Required input files
- The order for running notebooks or scripts
- Exact commands where applicable
- Expected outputs
- Assumptions needed to interpret the results

Exploratory notebooks will be stored in notebooks/, and reusable
Python code will be stored in src/.

## Testing

No automated tests have been added yet. We will document how to
run them when tests are introduced.

## Reproducibility

As we develop the analysis, we will record dependency versions,
use relative file paths, and document data preparation steps.
Where applicable, we will also record random seeds.
