"""CBOE Crude Oil Volatility Index (OVX) — daily from FRED.

FRED series: `OVXCLS` (daily close).

API key resolved in order:
    1. FRED_API_KEY env var
    2. one-line file `fred_api_key.txt` at the repo root
    3. RuntimeError

Columns returned:
    date  — trading day
    ovx   — OVX close
"""

from __future__ import annotations

import os
from pathlib import Path

import polars as pl
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

_REPO_ROOT = Path(__file__).resolve().parent.parent
_KEY_FILE = _REPO_ROOT / "fred_api_key.txt"


def _resolve_fred_key() -> str:
    key = os.getenv("FRED_API_KEY")
    if key and key != "your_fred_api_key":
        return key.strip()
    if _KEY_FILE.exists():
        return _KEY_FILE.read_text().strip()
    raise RuntimeError(
        f"No FRED API key found. Set FRED_API_KEY or place key in {_KEY_FILE}."
    )


def load_ovx(start: str, end: str) -> pl.DataFrame:
    fred = Fred(api_key=_resolve_fred_key())
    series = fred.get_series("OVXCLS", observation_start=start, observation_end=end)
    pdf = series.rename("ovx").reset_index().rename(columns={"index": "date"})
    return pl.from_pandas(pdf).with_columns(pl.col("date").cast(pl.Date)).sort("date")
