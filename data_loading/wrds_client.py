"""WRDS connection helper.

Auth: `wrds.Connection` reads username from `WRDS_USER` env var (loaded from
`.env` at the repo root via python-dotenv) and prompts for the password on
first use, caching it in `~/.pgpass`.

`query_wrds` bypasses `wrds.Connection.raw_sql()` because that path goes
through `pandas.read_sql_query`, which is broken under SQLAlchemy 2.x
(pandas tries to call `.cursor()` on a SQLAlchemy Connection that no longer
exposes one). We use the SQLAlchemy engine directly and load into Polars.
"""

from __future__ import annotations

import os

import polars as pl
import wrds
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()


def get_wrds_connection(username: str | None = None) -> wrds.Connection:
    user = username or os.getenv("WRDS_USER")
    if not user or user == "your_wrds_username":
        raise RuntimeError(
            "WRDS_USER not set. Add it to .env at the repo root or pass `username=`."
        )
    return wrds.Connection(wrds_username=user)


def query_wrds(conn: wrds.Connection, sql: str) -> pl.DataFrame:
    with conn.engine.connect() as c:
        result = c.execute(text(sql))
        rows = result.fetchall()
        cols = list(result.keys())
    return pl.DataFrame(rows, schema=cols, orient="row")
