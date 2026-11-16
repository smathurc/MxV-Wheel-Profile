"""Run project notebooks in fresh kernels with the active Python environment.

From the repository root, run all notebooks with:
    python scripts/run_notebooks.py
Or select one by filename:
    python scripts/run_notebooks.py 04_profile_shape_extension.ipynb
Executed copies and the execution summary stay under outputs/notebooks/.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time


def select_notebooks(root, names):
    """Select only repository notebooks, in the requested order."""
    available = {p.name: p for p in sorted((Path(root) / "notebooks").glob("*.ipynb"))}
    if not names:
        return list(available.values())
    selected = []
    for name in names:
        key = name if name.endswith(".ipynb") else name + ".ipynb"
        if key not in available:
            raise ValueError(f"Unknown notebook {name!r}. Available: {', '.join(available)}")
        if available[key] not in selected:
            selected.append(available[key])
    return selected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", help="Filenames, or omit to run all notebooks.")
    parser.add_argument("--data-dir", type=Path, help="Optional existing external Data folder.")
    parser.add_argument("--timeout", type=int, default=1200, help="Maximum seconds per cell.")
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    root = Path(__file__).resolve().parents[1]
    try:
        selected = select_notebooks(root, args.notebooks)
    except ValueError as error:
        parser.error(str(error))

    import nbformat
    from nbclient import NotebookClient
    from jupyter_client import KernelManager

    sys.path.insert(0, str(root / "src"))
    from project_paths import output_directory

    if args.data_dir:
        os.environ["HUNTING_DATA_DIR"] = str(args.data_dir.expanduser().resolve())
    destination = output_directory(root, "notebooks")
    records = []
    with tempfile.TemporaryDirectory(prefix="mxv-notebooks-") as runtime:
        for variable, name in (("IPYTHONDIR", "ipython"),
                               ("JUPYTER_RUNTIME_DIR", "jupyter"),
                               ("MPLCONFIGDIR", "matplotlib")):
            folder = Path(runtime) / name
            folder.mkdir()
            os.environ[variable] = str(folder)
        for source in selected:
            print(f"Running {source.name}", flush=True)
            notebook = nbformat.read(source, as_version=4)
            nbformat.validate(notebook)
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    cell.outputs = []
                    cell.execution_count = None
            manager = KernelManager(kernel_name="python3")
            manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher",
                                        "-f", "{connection_file}"]
            record = {"notebook": source.name, "status": "failed"}
            started = time.monotonic()
            try:
                NotebookClient(notebook, km=manager, timeout=args.timeout,
                               startup_timeout=180, allow_errors=False).execute(
                                   cwd=str(root), cleanup_kc=True)
                record["status"] = "passed"
            except Exception as error:
                record["error"] = str(error)
                raise
            finally:
                record["seconds"] = round(time.monotonic() - started, 2)
                record["executed_notebook"] = source.stem + "_executed.ipynb"
                nbformat.write(notebook, destination / record["executed_notebook"])
                records.append(record)
                summary = {"python": sys.version, "notebooks": records}
                (destination / "execution_summary.json").write_text(
                    json.dumps(summary, indent=2) + "\n")
            print(f"Passed {source.name} ({record['seconds']:.1f}s)", flush=True)
    print(f"Completed {len(records)} notebook(s). Executed copies: {destination}", flush=True)


if __name__ == "__main__":
    main()
