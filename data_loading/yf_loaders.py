"""yfinance-backed loaders that match the CRSP schemas in `sp500.py` and
`tanker_equities.py`. Used to backfill CRSP series past their academic-cadence
cutoff (typically the prior calendar year-end).

Returns columns:
    load_sp500_yf:           date, spindx, sprtrn, vwretd, ewretd, source
    load_tanker_equities_yf: date, permno, ticker, prc, ret, vol, shrout, source

CRSP-only fields (vwretd, ewretd, permno, shrout) are filled with null on
yfinance rows. `source` is always "yfinance".
"""

from __future__ import annotations

import warnings

import polars as pl
import yfinance as yf

from data_loading.tickers import TANKER_TICKERS


def load_sp500_yf(start: str, end: str) -> pl.DataFrame:
    raw = yf.download(
        tickers="^GSPC",
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if raw.empty:
        raise RuntimeError("yfinance returned no data for ^GSPC.")

    if isinstance(raw.columns, type(raw.columns)) and raw.columns.nlevels > 1:
        raw.columns = raw.columns.get_level_values(0)

    pdf = raw[["Close", "Adj Close"]].copy()
    pdf["sprtrn"] = pdf["Adj Close"].pct_change()
    pdf = pdf.rename(columns={"Close": "spindx"})[["spindx", "sprtrn"]]
    pdf.index.name = "date"
    pdf = pdf.reset_index()

    return (
        pl.from_pandas(pdf)
        .with_columns(
            pl.col("date").cast(pl.Date),
            pl.lit(None, dtype=pl.Float64).alias("vwretd"),
            pl.lit(None, dtype=pl.Float64).alias("ewretd"),
            pl.lit("yfinance").alias("source"),
        )
        .select(["date", "spindx", "sprtrn", "vwretd", "ewretd", "source"])
        .sort("date")
    )


def load_tanker_equities_yf(
    start: str,
    end: str,
    tickers: list[str] | None = None,
) -> pl.DataFrame:
    tickers = tickers or TANKER_TICKERS
    raw = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,
        group_by="ticker",
        progress=False,
        threads=True,
    )
    if raw.empty:
        raise RuntimeError(f"yfinance returned no data for any of {tickers}.")

    frames: list[pl.DataFrame] = []
    for ticker in tickers:
        try:
            sub = raw[ticker][["Close", "Adj Close", "Volume"]].copy()
        except KeyError:
            warnings.warn(f"yfinance: no columns for ticker {ticker}, skipping.", stacklevel=2)
            continue
        sub = sub.dropna(how="all")
        if sub.empty:
            warnings.warn(f"yfinance: empty series for ticker {ticker} (likely delisted), skipping.", stacklevel=2)
            continue
        sub["ret"] = sub["Adj Close"].pct_change()
        sub = sub.rename(columns={"Close": "prc", "Volume": "vol"})[["prc", "ret", "vol"]]
        sub.index.name = "date"
        sub = sub.reset_index()
        sub["ticker"] = ticker
        frames.append(
            pl.from_pandas(sub).with_columns(
                pl.col("date").cast(pl.Date),
                pl.col("prc").cast(pl.Float64),
                pl.col("ret").cast(pl.Float64),
                pl.col("vol").cast(pl.Float64),
            )
        )

    if not frames:
        raise RuntimeError(f"yfinance returned no usable data for any of {tickers}.")

    return (
        pl.concat(frames, how="vertical")
        .with_columns(
            pl.lit(None, dtype=pl.Int64).alias("permno"),
            pl.lit(None, dtype=pl.Float64).alias("shrout"),
            pl.lit("yfinance").alias("source"),
        )
        .select(["date", "permno", "ticker", "prc", "ret", "vol", "shrout", "source"])
        .sort(["date", "ticker"])
    )
