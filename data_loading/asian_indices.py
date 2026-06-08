"""Japanese and Korean stock indexes — daily from Compustat Global Index.

Source: WRDS `comp.g_idx_daily` (daily index series) keyed by `gvkeyx`,
with metadata in `comp.g_idx_index`.

The `INDEX_GVKEYX` map below uses placeholder gvkeyx values — they must be
confirmed once against your WRDS subscription. Use `discover_gvkeyx()` to
print the candidates and pick the right ones.

Columns returned:
    date    — trading day (each index on its own exchange calendar)
    nikkei  — Nikkei 225 close
    topix   — TOPIX close
    kospi   — KOSPI Composite close
"""

from __future__ import annotations

import polars as pl

from data_loading.wrds_client import get_wrds_connection, query_wrds

INDEX_GVKEYX: dict[str, str] = {
    "nikkei": "150069",  # Nikkei 225 Index
    "topix":  "150194",  # Topix Index
    "kospi":  "150035",  # Korea Stock Exchange Composite Index (KOSPI)
}


def discover_gvkeyx() -> pl.DataFrame:
    """Print candidate gvkeyx for Nikkei, TOPIX, KOSPI from `comp.g_idx_index`.

    Run this once to confirm the values in INDEX_GVKEYX match your subscription.
    """
    conn = get_wrds_connection()
    try:
        return query_wrds(
            conn,
            """
                SELECT gvkeyx, conm, tic, indexgeo, indexcat, idxstat
                FROM comp.g_idx_index
                WHERE conm ILIKE '%nikkei%'
                   OR conm ILIKE '%topix%'
                   OR conm ILIKE '%kospi%'
                ORDER BY conm
            """,
        )
    finally:
        conn.close()


def load_asian_indices(
    start: str,
    end: str,
    gvkeyx_map: dict[str, str] | None = None,
) -> pl.DataFrame:
    gvkeyx_map = gvkeyx_map or INDEX_GVKEYX
    gvkeyx_sql = ", ".join(f"'{g}'" for g in gvkeyx_map.values())

    conn = get_wrds_connection()
    try:
        long_df = query_wrds(
            conn,
            f"""
                SELECT gvkeyx, datadate AS date, prccd
                FROM comp.g_idx_daily
                WHERE gvkeyx IN ({gvkeyx_sql})
                  AND datadate >= '{start}'
                  AND datadate <= '{end}'
                ORDER BY datadate, gvkeyx
            """,
        )
    finally:
        conn.close()

    inverse = {v: k for k, v in gvkeyx_map.items()}
    long_df = long_df.with_columns(
        pl.col("gvkeyx").cast(pl.Utf8).replace(inverse).alias("name")
    )
    return long_df.pivot(index="date", on="name", values="prccd").sort("date")
