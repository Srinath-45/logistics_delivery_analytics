"""
Functions for loading the logistics delivery dataset.
"""

from pathlib import Path

import pandas as pd


def check_file_exists(file_path):
    """Check whether the specified data file exists."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}")

    return True


def load_data(file_path):
    """Load a CSV file into a Pandas DataFrame."""
    check_file_exists(file_path)

    data = pd.read_csv(file_path)

    if data.empty:
        raise ValueError("The data file is empty.")

    return data