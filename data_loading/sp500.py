"""S&P 500 daily index — CRSP `crsp.dsi`, with yfinance gap-fill.

CRSP is academic-cadence (updated annually, usually with a ~6-month lag past
year-end). When the requested window extends past the latest CRSP date, the
post-cutoff portion is filled from yfinance `^GSPC` (see `yf_loaders.py`).

Columns:
    date, spindx, sprtrn, vwretd, ewretd, source
where `source` is "crsp" or "yfinance" and `vwretd`/`ewretd` are null on
yfinance rows.
"""

from __future__ import annotations

import warnings
from datetime import date, timedelta

import polars as pl

from data_loading.wrds_client import get_wrds_connection, query_wrds
from data_loading.yf_loaders import load_sp500_yf


def _load_sp500_crsp(start: str, end: str) -> pl.DataFrame:
    conn = get_wrds_connection()
    try:
        sql = f"""
            SELECT date, spindx, sprtrn, vwretd, ewretd
            FROM crsp.dsi
            WHERE date >= '{start}' AND date <= '{end}'
            ORDER BY date
        """
        df = query_wrds(conn, sql)
    finally:
        conn.close()
    return df.with_columns(pl.lit("crsp").alias("source")).select(
        ["date", "spindx", "sprtrn", "vwretd", "ewretd", "source"]
    )


def _crsp_dsi_max_date() -> date:
    conn = get_wrds_connection()
    try:
        df = query_wrds(conn, "SELECT MAX(date) AS max_date FROM crsp.dsi")
    finally:
        conn.close()
    return df["max_date"][0]


def load_sp500(start: str, end: str) -> pl.DataFrame:
    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)

    try:
        crsp_max = _crsp_dsi_max_date()
    except Exception as e:
        warnings.warn(
            f"Could not reach CRSP ({type(e).__name__}: {e}); falling back to pure yfinance.",
            stacklevel=2,
        )
        return load_sp500_yf(start, end)

    parts: list[pl.DataFrame] = []
    if start_d <= crsp_max:
        crsp_end = min(end_d, crsp_max).isoformat()
        parts.append(_load_sp500_crsp(start, crsp_end))
    if end_d > crsp_max:
        yf_start = max(start_d, crsp_max + timedelta(days=1)).isoformat()
        parts.append(load_sp500_yf(yf_start, end))

    if not parts:
        raise RuntimeError(f"No data window resolved for {start}..{end}.")
    return pl.concat(parts, how="diagonal_relaxed").sort("date")
