"""Historical macro figures (FX, gold, CPI) for manuscript Figures 1–2."""

from __future__ import annotations

import io
from pathlib import Path
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import MANUSCRIPT_BODY_FIGURES, RAW_DIR, REFACTOR_OUTPUT_FIGURES

RAW_FIGURES_DIR = RAW_DIR / "figures"
MONTHLY_MACRO_CSV = RAW_FIGURES_DIR / "monthly_macro.csv"

# FRED graph export (no API key); series chosen for 1930s coverage.
FRED_SERIES = {
    "sterling": "EXUSUK",  # U.S. dollars per U.K. pound
    "franc": "EXCHUS",  # U.S. dollars per French franc (monthly)
    "cpi": "CPIAUCSL",
}


def _fred_csv(series_id: str, start: str = "1930-01-01", end: str = "1936-12-31") -> pd.Series:
    url = (
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        f"&cosrd={start}&coerd={end}"
    )
    with urlopen(url, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    frame = pd.read_csv(io.StringIO(raw))
    frame.columns = ["date", series_id]
    frame["date"] = pd.to_datetime(frame["date"])
    s = frame.set_index("date")[series_id].astype(float)
    return s.replace(".", np.nan).dropna()


def fetch_monthly_macro(cache: Path = MONTHLY_MACRO_CSV) -> pd.DataFrame:
    """Download monthly macro series from FRED and cache locally."""
    cache.parent.mkdir(parents=True, exist_ok=True)
    cols = {}
    for name, sid in FRED_SERIES.items():
        cols[name] = _fred_csv(sid)
    out = pd.concat(cols, axis=1, sort=True)
    # Official U.S. gold price steps (USD/troy oz) for annotation lines.
    out["gold_official_us"] = np.nan
    out.loc[out.index >= "1934-01-31", "gold_official_us"] = 35.0
    out.loc[(out.index >= "1933-01-31") & (out.index < "1934-01-31"), "gold_official_us"] = 20.67
    out.to_csv(cache)
    return out


def _load_macro() -> pd.DataFrame:
    if MONTHLY_MACRO_CSV.is_file():
        frame = pd.read_csv(MONTHLY_MACRO_CSV, parse_dates=["date"]).set_index("date")
    else:
        frame = fetch_monthly_macro()
    return frame


def _norm_dec_1932(s: pd.Series) -> pd.Series:
    dec = s.loc["1932-12":"1932-12"]
    base = float(dec.iloc[-1]) if len(dec) else float(s.iloc[0])
    return s / base if base else s


def _vline_gold_order(ax) -> None:
    """April 5, 1933 — Executive Order 6102."""
    ax.axvline(pd.Timestamp("1933-04-05"), color="black", linewidth=1.0)


def plot_dollar_to_sterling(frame: pd.DataFrame, out_path: Path) -> Path:
    fx = _norm_dec_1932(frame["sterling"])
    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=150)
    ax.plot(fx.index, fx, color="C3", linestyle="--", linewidth=1.2, label="USD / sterling")
    if "gold_official_us" in frame.columns:
        g = frame["gold_official_us"].dropna()
        if not g.empty:
            ax.plot(g.index, _norm_dec_1932(g), color="C0", linewidth=1.2, label="Gold (US)")
    _vline_gold_order(ax)
    ax.set_xlim(pd.Timestamp("1930-12-31"), pd.Timestamp("1934-03-31"))
    ax.set_ylabel("Index (Dec. 1932 = 1)")
    ax.legend(loc="best", fontsize=8, frameon=False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_dollar_to_franc(frame: pd.DataFrame, out_path: Path) -> Path:
    fx = _norm_dec_1932(frame["franc"])
    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=150)
    ax.plot(fx.index, fx, color="C3", linestyle="--", linewidth=1.2, label="USD / franc")
    if "gold_official_us" in frame.columns:
        g = frame["gold_official_us"].dropna()
        if not g.empty:
            ax.plot(g.index, _norm_dec_1932(g), color="C0", linewidth=1.2, label="Gold (US)")
    _vline_gold_order(ax)
    ax.set_xlim(pd.Timestamp("1930-12-31"), pd.Timestamp("1934-03-31"))
    ax.set_ylabel("Index (Dec. 1932 = 1)")
    ax.legend(loc="best", fontsize=8, frameon=False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_inflation(frame: pd.DataFrame, out_path: Path) -> Path:
    cpi = _norm_dec_1932(frame["cpi"])
    fig, ax = plt.subplots(figsize=(5.5, 3.2), dpi=150)
    if "gold_official_us" in frame.columns:
        g = frame["gold_official_us"].dropna()
        if not g.empty:
            ax.plot(
                g.index,
                _norm_dec_1932(g),
                color="C0",
                linestyle=":",
                linewidth=1.2,
                label="Official gold price",
            )
    ax.plot(cpi.index, cpi, color="C3", linestyle="--", linewidth=1.2, label="CPI")
    _vline_gold_order(ax)
    ax.set_xlim(pd.Timestamp("1933-01-01"), pd.Timestamp("1934-12-31"))
    ax.set_ylabel("Index (Dec. 1932 = 1)")
    ax.legend(loc="best", fontsize=8, frameon=False)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def build_macro_figures(*, out_dir: Path | None = None) -> dict[str, Path]:
    frame = _load_macro()
    dest = Path(out_dir) if out_dir is not None else REFACTOR_OUTPUT_FIGURES
    paths = {
        "dollar_to_sterling": plot_dollar_to_sterling(frame, dest / "dollar_to_sterling.pdf"),
        "dollar_to_franc": plot_dollar_to_franc(frame, dest / "dollar_to_franc.pdf"),
        "inflation": plot_inflation(frame, dest / "inflation.pdf"),
    }
    MANUSCRIPT_BODY_FIGURES.mkdir(parents=True, exist_ok=True)
    for key, p in list(paths.items()):
        manuscript = MANUSCRIPT_BODY_FIGURES / p.name
        manuscript.write_bytes(p.read_bytes())
        paths[key] = manuscript
    return paths


def main() -> None:
    for name, path in build_macro_figures().items():
        print(f"Wrote {name}: {path}")


if __name__ == "__main__":
    main()
