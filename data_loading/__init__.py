"""Data loaders for the oil-procurement forecast."""

from data_loading.asian_indices import discover_gvkeyx, load_asian_indices
from data_loading.oil_futures import load_oil_futures
from data_loading.ovx import load_ovx
from data_loading.sp500 import load_sp500
from data_loading.tanker_equities import load_tanker_equities
from data_loading.tickers import TANKER_TICKERS
from data_loading.wrds_client import get_wrds_connection, query_wrds
from data_loading.yf_loaders import load_sp500_yf, load_tanker_equities_yf

__all__ = [
    "TANKER_TICKERS",
    "discover_gvkeyx",
    "get_wrds_connection",
    "load_asian_indices",
    "load_oil_futures",
    "load_ovx",
    "load_sp500",
    "load_sp500_yf",
    "load_tanker_equities",
    "load_tanker_equities_yf",
    "query_wrds",
]
