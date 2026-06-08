"""Reconstruct the per-draw prediction array for one forecaster and append it as a
`predictions` group to its idata.nc — WITHOUT re-sampling.

We monkeypatch pm.sample to return the already-saved posterior, then run a truncated
copy of the instance's own fit script (up to just after it computes the per-draw
horizon probabilities). This reuses each instance's exact forward-simulation and
standardization, so the reconstructed predictions are faithful to the saved posterior
(only Monte-Carlo path noise differs from the original forecast.json).

Usage:
    python recon_driver.py <script.py> <cut_line> <pred_var> <horizon_var>
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
print(f"[recon] {script}: posterior chain={n_chain} draw={n_draw}")

# Use the saved posterior instead of resampling; skip log-density recompute (already saved).
pm.sample = lambda *a, **k: saved
pm.stats.compute_log_likelihood = lambda *a, **k: None
pm.stats.compute_log_prior = lambda *a, **k: None
# Some scripts call idata.to_netcdf() mid-run (e.g. instance-5 at L286). That would try
# to truncate the file while `saved` holds it open read-only -> error. No-op it; we write
# the final idata (with predictions) ourselves below.
saved.to_netcdf = lambda *a, **k: None

# Truncate the script to the cut line (keeps everything up to and including the
# per-draw probability computation; drops forecast.json write, EVT, psense, plots).
with open(script) as fh:
    lines = fh.readlines()
trunc = "/tmp/_recon_trunc.py"
with open(trunc, "w") as fh:
    fh.writelines(lines[:cut_line])

ns = runpy.run_path(trunc, run_name="__main__")

# Copy the per-draw array into memory, then release ALL open file handles before
# writing — az.from_netcdf opens idata.nc lazily (read-only), which would otherwise
# block the mode="a" append ("file is already open for read-only").
pred = np.array(ns[pred_var], dtype=float)
hor = [float(x) for x in np.asarray(ns[hor_var]).ravel()[: pred.shape[-1]]]
del saved, ns
import gc

gc.collect()
try:
    xr.backends.file_manager.FILE_CACHE.clear()
except Exception as exc:  # pragma: no cover
    print(f"[recon] file-cache clear warning: {exc}")

if pred.ndim == 2:  # (n_post, H) -> (chain, draw, H)
    pred = pred.reshape(n_chain, n_draw, pred.shape[1])
assert pred.shape[:2] == (n_chain, n_draw), f"pred shape {pred.shape} != ({n_chain},{n_draw},H)"
H = pred.shape[2]
print(f"[recon] captured '{pred_var}' shape {pred.shape}; horizons={hor}")

da = xr.DataArray(
    pred,
    dims=["chain", "draw", "horizon"],
    coords={"horizon": list(range(H)), "horizon_days": ("horizon", hor)},
    name="p_event_by_horizon",
)
ds = xr.Dataset({"p_event_by_horizon": da})

# Append as a new group to the existing idata.nc (leaves posterior etc. untouched).
ds.to_netcdf(IDATA, group="predictions", mode="a", engine="h5netcdf")

chk = az.from_netcdf(IDATA)
groups = [g.strip("/") for g in chk.groups]
print(f"[recon] groups now: {groups}")
means = [round(float(chk.predictions["p_event_by_horizon"][:, :, i].mean()), 4) for i in range(H)]
print(f"[recon] predictions mean P(event) by horizon: {means}")
assert "predictions" in groups and "posterior" in groups
print(f"[recon] OK {script}")
