# Data Loading

Utilities for fetching, parsing, and preparing the daily market series used in the oil-procurement forecast.

## Datasets

All series are **daily** (one row per trading day on each source's native calendar).

| # | Variable | Source | Symbol / table | Coverage | Access |
|---|---|---|---|---|---|
| 1 | Oil futures — WTI & Brent front-month | Yahoo Finance | `CL=F`, `BZ=F` | ~2000–present | yfinance, no auth |
| 2 | OVX (CBOE Crude Oil Volatility Index) | FRED | `OVXCLS` | 2007-05-10–present | FRED API key |
| 3 | Maritime tanker equities | WRDS — CRSP **+ yfinance gap-fill** | `crsp.dsf` ∪ yfinance | 1925–present (CRSP); auto-stitched past CRSP cutoff | WRDS + yfinance |
| 4 | S&P 500 (level + return) | WRDS — CRSP **+ yfinance gap-fill** | `crsp.dsi` ∪ yfinance `^GSPC` | 1925–present (CRSP); auto-stitched past CRSP cutoff | WRDS + yfinance |
| 5 | Nikkei 225, TOPIX, KOSPI | WRDS — Compustat Global Index | `comp.g_idx_daily` | varies by index | WRDS auth |

## Sources

### WRDS (Wharton Research Data Services)
- URL: https://wrds-www.wharton.upenn.edu/
- Auth: set `WRDS_USER` in `.env`; password is prompted on first run and cached in `~/.pgpass`.
- Tables used: `crsp.dsf`, `crsp.dsi`, `crsp.stocknames`, `comp.g_idx_daily`, `comp.g_idx_index`.

### FRED (Federal Reserve Bank of St. Louis)
- URL: https://fred.stlouisfed.org/
- Auth: free API key from https://fredaccount.stlouisfed.org/apikeys
- Key file: `fred_api_key.txt` at the repo root (gitignored); `FRED_API_KEY` env var also accepted.

### Yahoo Finance
- URL: https://finance.yahoo.com/
- Auth: none (yfinance scrapes public endpoints).

## Loaders

Each loader takes ISO-format `start`/`end` dates and returns a Polars DataFrame keyed on `date`.

| Module | Function | Output columns |
|---|---|---|
| `wrds_client.py` | `get_wrds_connection()`, `query_wrds(conn, sql)` | helpers; not a loader |
| `oil_futures.py` | `load_oil_futures(start, end)` | `date, wti_open, wti_close, wti_volume, brent_close, brent_volume` |
| `ovx.py` | `load_ovx(start, end)` | `date, ovx` |
| `sp500.py` | `load_sp500(start, end)` | `date, spindx, sprtrn, vwretd, ewretd, source` |
| `tanker_equities.py` | `load_tanker_equities(start, end, tickers=TANKER_TICKERS)` | `date, permno, ticker, prc, ret, vol, shrout, source` |
| `asian_indices.py` | `load_asian_indices(start, end, gvkeyx_map=INDEX_GVKEYX)` + `discover_gvkeyx()` | `date, nikkei, topix, kospi` |
| `yf_loaders.py` | `load_sp500_yf`, `load_tanker_equities_yf` | yfinance-only variants matching CRSP schema; used internally for gap-fill |

### Provenance: the `source` column

`sp500.parquet` and `tanker_equities.parquet` carry a `source` column with values `"crsp"` or `"yfinance"`. CRSP rows are used wherever CRSP covers; rows past the CRSP cutoff (`MAX(date) FROM crsp.dsi` / `crsp.dsf`, typically prior year-end) are pulled from yfinance. The split is automatic — `load_sp500` and `load_tanker_equities` handle it transparently.

CRSP-only fields are null on yfinance rows:
- `sp500`: `vwretd`, `ewretd` are CRSP-computed market returns, not available from yfinance.
- `tanker_equities`: `permno` (CRSP identifier) and `shrout` (shares outstanding) are null on yfinance rows.

**Delisted tickers:** `EURN` merged into CMB.TECH in 2024 and `OSG` was acquired in 2023. yfinance returns no data for these symbols, so they appear only in the CRSP portion. A `UserWarning` is emitted for each skipped ticker.

**Stitch seam:** CRSP returns are open-to-close-with-dividends; yfinance `ret = pct_change(Adj Close)` is close-to-close-with-dividends. A small one-day discrepancy at the CRSP/yfinance boundary is expected.

### Tanker tickers (default in `tickers.py`)

`FRO, EURN, STNG, DHT, INSW, TNK, NAT, TRMD, ASC, TNP, OSG, IMPP`.

### Asian index gvkeyx

`asian_indices.INDEX_GVKEYX` is pre-filled with confirmed values: Nikkei 225 = `150069`, Topix = `150194`, KOSPI ("Korea Stock Exchange Composite Index") = `150035`. Re-run `discover_gvkeyx()` if you suspect the codes have changed.

## Calendar caveat

Each series uses its own exchange calendar (NYSE, NYMEX/ICE, TSE, KRX). A naive inner-join on `date` drops a meaningful share of rows. Calendar reconciliation (forward-fill / business-day reindex / anchor to NYSE) belongs in a downstream merge utility — not in these loaders.

## Smoke test

```bash
pixi install
pixi run python -c "from data_loading import load_ovx; print(load_ovx('2024-01-01','2025-01-01').head())"
pixi run python -c "from data_loading import load_oil_futures; print(load_oil_futures('2024-01-01','2025-01-01').head())"
pixi run python -c "from data_loading import load_sp500; print(load_sp500('2024-01-01','2025-01-01').head())"
pixi run python -c "from data_loading import load_tanker_equities; print(load_tanker_equities('2024-01-01','2025-01-01').head())"
pixi run python -c "from data_loading import load_asian_indices; print(load_asian_indices('2024-01-01','2025-01-01').head())"
```

Run in that order — FRED and yfinance need no WRDS auth and are the quickest to validate.
