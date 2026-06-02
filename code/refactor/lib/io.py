"""I/O helpers."""

from pathlib import Path

import pandas as pd


def read_dta(path: Path) -> pd.DataFrame:
    return pd.read_stata(path)


def write_dta(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_stata(path, write_index=False, version=118)


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {description}: {path}\n"
            "Place raw files under data/raw/ or run with existing intermediates."
        )
