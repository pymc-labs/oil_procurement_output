"""Maritime tanker equities — daily from CRSP `crsp.dsf`, with yfinance gap-fill.

CRSP is academic-cadence (updated annually, ~6-month lag past year-end).
When the requested window extends past the latest CRSP date, the post-cutoff
portion is filled from yfinance for the same tickers (see `yf_loaders.py`).

CRSP path:
    1. Resolve tickers → permnos via `crsp.stocknames` (handles ticker changes /
       delistings — a ticker can map to multiple permnos historically).
    2. Pull daily prices/returns/volume from `crsp.dsf` for those permnos.

Columns:
    date, permno, ticker, prc, ret, vol, shrout, source
`source` is "crsp" or "yfinance"; `permno`/`shrout` are null on yfinance rows.

Delisting note: tickers that no longer trade on US exchanges (e.g. EURN
merged into CMB.TECH in 2024, OSG acquired in 2023) will return no rows from
yfinance for the post-cutoff window. They still appear in the CRSP portion.
"""

from __future__ import annotations

import warnings
from datetime import date, timedelta

import polars as pl

from data_loading.tickers import TANKER_TICKERS
from data_loading.wrds_client import get_wrds_connection, query_wrds
from data_loading.yf_loaders import load_tanker_equities_yf


def _load_tanker_equities_crsp(
    start: str, end: str, tickers: list[str]
) -> pl.DataFrame:
    tickers_sql = ", ".join(f"'{t}'" for t in tickers)
    conn = get_wrds_connection()
    try:
        names = query_wrds(
            conn,
            f"""
                SELECT DISTINCT permno, ticker
                FROM crsp.stocknames
                WHERE ticker IN ({tickers_sql})
            """,
        )
        if names.is_empty():
            raise RuntimeError(
                f"No CRSP permnos found for tickers {tickers}. "
                "Either the symbols don't exist in CRSP or your subscription excludes them."
            )

        permnos = names["permno"].unique().to_list()
        permnos_sql = ", ".join(str(p) for p in permnos)

        prices = query_wrds(
            conn,
            f"""
                SELECT permno, date, prc, ret, vol, shrout
                FROM crsp.dsf
                WHERE permno IN ({permnos_sql})
                  AND date >= '{start}'
                  AND date <= '{end}'
                ORDER BY date, permno
            """,
        )
    finally:
        conn.close()

    return (
        prices.join(names, on="permno", how="left")
        .with_columns(pl.lit("crsp").alias("source"))
        .select(["date", "permno", "ticker", "prc", "ret", "vol", "shrout", "source"])
    )


def _crsp_dsf_max_date() -> date:
    conn = get_wrds_connection()
    try:
        df = query_wrds(conn, "SELECT MAX(date) AS max_date FROM crsp.dsf")
    finally:
        conn.close()
    return df["max_date"][0]


def load_tanker_equities(
    start: str,
    end: str,
    tickers: list[str] | None = None,
) -> pl.DataFrame:
    tickers = tickers or TANKER_TICKERS
    start_d = date.fromisoformat(start)
    end_d = date.fromisoformat(end)

    try:
        crsp_max = _crsp_dsf_max_date()
    except Exception as e:
        warnings.warn(
            f"Could not reach CRSP ({type(e).__name__}: {e}); falling back to pure yfinance.",
            stacklevel=2,
        )
        return load_tanker_equities_yf(start, end, tickers)

    parts: list[pl.DataFrame] = []
    if start_d <= crsp_max:
        crsp_end = min(end_d, crsp_max).isoformat()
        parts.append(_load_tanker_equities_crsp(start, crsp_end, tickers))
    if end_d > crsp_max:
        yf_start = max(start_d, crsp_max + timedelta(days=1)).isoformat()
        parts.append(load_tanker_equities_yf(yf_start, end, tickers))

    if not parts:
        raise RuntimeError(f"No data window resolved for {start}..{end}.")
    return pl.concat(parts, how="diagonal_relaxed").sort(["date", "ticker"])
