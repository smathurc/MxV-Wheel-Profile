"""Resolve the shared input and output locations used by project notebooks.

Notebooks use the repository's data/ folder by default. Existing external-data
workflows may set HUNTING_DATA_DIR before launching Jupyter. Source inputs are
never created or overwritten by these helpers.
"""
import os
from pathlib import Path


def find_project_root(start=None):
    """Find the repository from its root, notebooks/, or a nested directory."""
    start = Path(start or Path.cwd()).resolve()
    for folder in (start, *start.parents):
        if ((folder / "requirements.txt").is_file()
                and (folder / "notebooks").is_dir()
                and (folder / "src").is_dir()):
            return folder
    raise FileNotFoundError("Start Jupyter inside the project repository; see INSTALL.md.")


def data_directory(root):
    """Use root/data unless an external-data location was explicitly set."""
    configured = Path(os.environ.get("HUNTING_DATA_DIR") or "data").expanduser()
    return configured if configured.is_absolute() else Path(root) / configured


def required_file(path):
    """Name a missing input and point to the shared installation directions."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Missing input {path}. Download the Teams Data contents; see INSTALL.md.")
    return path


def merged_file(data_folder):
    """Accept either supplied merged filename, without using stale outputs."""
    data_folder = Path(data_folder)
    for name in ("final_merged_data.csv", "final_merged_data(in).csv"):
        path = data_folder / name
        if path.is_file():
            return path
    return required_file(data_folder / "final_merged_data.csv")


def wheel_wear_file(data_folder):
    """Read the wheel-wear workbook from either approved archive layout."""
    data_folder = Path(data_folder)
    name = "2023-06-13 - Wheel wear results.xlsx"
    for folder in (data_folder, data_folder / "Profiles" / "Candidate wheel profiles"):
        path = folder / name
        if path.is_file():
            return path
    return required_file(data_folder / "Profiles" / "Candidate wheel profiles" / name)


def output_directory(root, name):
    """Create a generated-results directory without writing into data/."""
    folder = Path(root) / "outputs" / name
    folder.mkdir(parents=True, exist_ok=True)
    return folder
