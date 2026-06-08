"""Reconstruct instance-3 predictions from its saved first-passage array.

instance-3's fit script did not survive, but outputs/sim_paths.npz stored fp_days
(first-passage day per posterior-draw x path, inf if never crossed). The per-draw
P(event by horizon) is therefore directly recoverable with no re-simulation.
"""
import json

import numpy as np
import arviz as az
import xarray as xr

IDATA = "outputs/idata.nc"

npz = np.load("outputs/sim_paths.npz")
fp = np.asarray(npz["fp_days"], dtype=float)  # (n_post, n_paths)

with open("outputs/forecast_results.json") as fh:
    fr = json.load(fh)
hcd = [float(x) for x in fr["horizon_calendar_days"]]

saved = az.from_netcdf(IDATA)
n_chain = int(saved.posterior.sizes["chain"])
n_draw = int(saved.posterior.sizes["draw"])
del saved
import gc

gc.collect()
try:
    xr.backends.file_manager.FILE_CACHE.clear()
except Exception as exc:
    print(f"[recon3] file-cache clear warning: {exc}")

n_post = fp.shape[0]
assert n_post == n_chain * n_draw, f"{n_post} != {n_chain}*{n_draw}"

# Per-draw probability of crossing by each horizon (mean over that draw's paths).
p_by_draw = np.array([[float(np.mean(fp[i] <= h)) for h in hcd] for i in range(n_post)])
pred = p_by_draw.reshape(n_chain, n_draw, len(hcd))

print(f"[recon3] recon mean P(event): {[round(float(pred[:, :, i].mean()), 4) for i in range(len(hcd))]}")
print(f"[recon3] forecast.json     : {[round(float(x), 4) for x in fr['p_event_by_horizon']]}")

da = xr.DataArray(
    pred,
    dims=["chain", "draw", "horizon"],
    coords={"horizon": list(range(len(hcd))), "horizon_days": ("horizon", hcd)},
    name="p_event_by_horizon",
)
xr.Dataset({"p_event_by_horizon": da}).to_netcdf(IDATA, group="predictions", mode="a", engine="h5netcdf")

chk = az.from_netcdf(IDATA)
groups = [g.strip("/") for g in chk.groups]
print(f"[recon3] groups now: {groups}")
assert "predictions" in groups and "posterior" in groups
print("[recon3] OK instance-3")
