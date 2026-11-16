"""Run the shared comparison using the same environment as the other notebooks.

Usage: python scripts/run_team_comparison.py [--data-dir /path/to/Data]
"""
import sys

from run_notebooks import main


if __name__ == "__main__":
    main(["08_team_model_comparison.ipynb", *sys.argv[1:]])
