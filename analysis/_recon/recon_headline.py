"""Reconstruct the headline forecaster's predictions group AND a price-path npz.

Runs instance-1's own OU fit script (forecast_wti.py) with pm.sample patched to
return the already-saved posterior, truncated to just after the per-draw horizon
matrix is computed. Captures:
  - p_by_h_matrix  -> appended as the `predictions` group on idata.nc
  - paths/mean_log/std_log/fp_days -> outputs/sim_paths.npz (for the price fan chart)

Usage (run from the instance dir):
    python recon_headline.py forecast_wti.py 248 p_by_h_matrix horizon_trading_days
"""
import sys
import runpy

import numpy as np
import arviz as az
import xarray as xr
import pymc as pm

script, cut_line, pred_var, hor_var = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
IDATA = "outputs/idata.nc"

saved = az.from_netcdf(IDATA)
n_chain = int(saved.posterior.sizes["chain"])
n_draw = int(saved.posterior.sizes["draw"])
print(f"[recon-headline] {script}: posterior chain={n_chain} draw={n_draw}")

pm.sample = lambda *a, **k: saved
pm.stats.compute_log_likelihood = lambda *a, **k: None
pm.stats.compute_log_prior = lambda *a, **k: None
saved.to_netcdf = lambda *a, **k: None

with open(script) as fh:
    lines = fh.readlines()
trunc = "/tmp/_recon_headline_trunc.py"
with open(trunc, "w") as fh:
    fh.writelines(lines[:cut_line])

ns = runpy.run_path(trunc, run_name="__main__")

pred = np.array(ns[pred_var], dtype=float)
hor = [float(x) for x in np.asarray(ns[hor_var]).ravel()[: pred.shape[-1]]]
paths = np.asarray(ns["paths"], dtype=float)
mean_log = float(ns["mean_log"])
std_log = float(ns["std_log"])
fp_days = np.asarray(ns["fp_days"], dtype=float)

del saved, ns
import gc

gc.collect()
try:
    xr.backends.file_manager.FILE_CACHE.clear()
except Exception as exc:  # pragma: no cover
    print(f"[recon-headline] file-cache clear warning: {exc}")

if pred.ndim == 2:
    pred = pred.reshape(n_chain, n_draw, pred.shape[1])
assert pred.shape[:2] == (n_chain, n_draw), f"pred shape {pred.shape} != ({n_chain},{n_draw},H)"
H = pred.shape[2]
print(f"[recon-headline] captured '{pred_var}' shape {pred.shape}; horizons={hor}")

da = xr.DataArray(
    pred,
    dims=["chain", "draw", "horizon"],
    coords={"horizon": list(range(H)), "horizon_days": ("horizon", hor)},
    name="p_event_by_horizon",
)
xr.Dataset({"p_event_by_horizon": da}).to_netcdf(IDATA, group="predictions", mode="a", engine="h5netcdf")

np.savez_compressed("outputs/sim_paths.npz", paths=paths, mean_log=mean_log, std_log=std_log, fp_days=fp_days)
print(f"[recon-headline] saved sim_paths.npz: paths{paths.shape} mean_log={mean_log:.4f} std_log={std_log:.4f}")

chk = az.from_netcdf(IDATA)
groups = [g.strip("/") for g in chk.groups]
means = [round(float(chk.predictions["p_event_by_horizon"][:, :, i].mean()), 4) for i in range(H)]
print(f"[recon-headline] groups now: {groups}")
print(f"[recon-headline] predictions mean P(event) by horizon: {means}")
assert "predictions" in groups and "posterior" in groups
print("[recon-headline] OK")
