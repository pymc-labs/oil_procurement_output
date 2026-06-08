"""Oil futures — daily from Yahoo Finance.

Tickers:
    CL=F  — WTI crude front-month continuous (NYMEX)
    BZ=F  — Brent crude front-month continuous (ICE)

Columns returned (one row per trading day):
    date          — trading day (NYMEX/ICE calendar)
    wti_open
    wti_close
    wti_volume
    brent_close
    brent_volume
"""

from __future__ import annotations

import polars as pl
import yfinance as yf


def load_oil_futures(start: str, end: str) -> pl.DataFrame:
    raw = yf.download(
        tickers=["CL=F", "BZ=F"],
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        group_by="ticker",
        progress=False,
        threads=True,
    )
    if raw.empty:
        raise RuntimeError("yfinance returned no data for CL=F / BZ=F.")

    wti = raw["CL=F"][["Open", "Close", "Volume"]].rename(
        columns={"Open": "wti_open", "Close": "wti_close", "Volume": "wti_volume"}
    )
    brent = raw["BZ=F"][["Close", "Volume"]].rename(
        columns={"Close": "brent_close", "Volume": "brent_volume"}
    )
    merged = wti.join(brent, how="outer")
    merged.index.name = "date"
    merged = merged.reset_index()

    return pl.from_pandas(merged).with_columns(pl.col("date").cast(pl.Date)).sort("date")
