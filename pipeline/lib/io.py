"""I/O helpers."""

import io
from pathlib import Path

import pandas as pd


def read_dta(path: Path) -> pd.DataFrame:
    return pd.read_stata(path)


def write_dta(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_stata(path, write_index=False, version=118)


def roundtrip_dta(df: pd.DataFrame) -> pd.DataFrame:
    """Round-trip a frame through the .dta format in memory.

    The A0-A3 stages used to be persisted as .dta and read back by the A4
    merge; the write/read cycle coerces dtypes (float32 storage, int
    promotion). Reproducing it in memory keeps the A4 build bit-identical to
    the verified on-disk chain without persisting intermediates.
    """
    buf = io.BytesIO()
    df.to_stata(buf, write_index=False, version=118)
    buf.seek(0)
    return pd.read_stata(buf)


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {description}: {path}\n"
            "Place raw source files under data/raw/."
        )
