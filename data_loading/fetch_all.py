"""Fetch all five data series and save as parquet to data/raw/.

Usage:
    pixi run fetch                              # last 2 years through today
    pixi run fetch 2020-01-01 2024-12-31        # custom window
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import polars as pl

from data_loading.asian_indices import load_asian_indices
from data_loading.oil_futures import load_oil_futures
from data_loading.ovx import load_ovx
from data_loading.sp500 import load_sp500
from data_loading.tanker_equities import load_tanker_equities

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "raw"

LOADERS = {
    "ovx":             load_ovx,
    "oil_futures":     load_oil_futures,
    "sp500":           load_sp500,
    "tanker_equities": load_tanker_equities,
    "asian_indices":   load_asian_indices,
}


def fetch_all(start: str, end: str, out_dir: Path = OUT_DIR) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}
    for name, loader in LOADERS.items():
        print(f"\n[{name}] fetching {start} → {end} …", flush=True)
        try:
            df: pl.DataFrame = loader(start, end)
            path = out_dir / f"{name}.parquet"
            df.write_parquet(path)
            results[name] = f"ok ({df.height} rows → {path.name})"
            print(f"[{name}] {results[name]}", flush=True)
        except Exception as e:
            results[name] = f"FAILED: {type(e).__name__}: {e}"
            print(f"[{name}] {results[name]}", flush=True)
    return results


def _default_window() -> tuple[str, str]:
    today = date.today()
    return (today - timedelta(days=365 * 2)).isoformat(), today.isoformat()


def main() -> None:
    if len(sys.argv) == 1:
        start, end = _default_window()
    elif len(sys.argv) == 3:
        start, end = sys.argv[1], sys.argv[2]
    else:
        print("usage: python -m data_loading.fetch_all [START END]", file=sys.stderr)
        sys.exit(2)

    results = fetch_all(start, end)
    print("\n=== summary ===")
    for name, status in results.items():
        print(f"  {name:<16} {status}")
    if any(s.startswith("FAILED") for s in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
