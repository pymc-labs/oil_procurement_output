"""Inspect instance-3 artifacts to plan prediction reconstruction (no fit script survives)."""
import json
import numpy as np

npz = np.load("outputs/sim_paths.npz", allow_pickle=True)
print("=== sim_paths.npz keys / shapes / dtypes ===")
for k in npz.files:
    a = npz[k]
    print(f"  {k}: shape={getattr(a,'shape',None)} dtype={getattr(a,'dtype',None)} "
          f"min={np.nanmin(a) if a.size and np.issubdtype(a.dtype,np.number) else 'NA'} "
          f"max={np.nanmax(a) if a.size and np.issubdtype(a.dtype,np.number) else 'NA'}")

for fn in ("outputs/forecast_results.json", "outputs/model_diagnostics.json", "forecast.json"):
    try:
        with open(fn) as fh:
            d = json.load(fh)
        print(f"\n=== {fn} (keys) ===")
        print(list(d.keys()))
        for key in ("horizon_trading_days", "horizon_days", "horizon_dates", "tau_scaled",
                    "threshold", "mean_log", "std_log", "y_current", "n_paths",
                    "p_event_by_horizon", "crossing_direction"):
            if key in d:
                print(f"  {key} = {d[key]}")
    except FileNotFoundError:
        print(f"\n=== {fn}: not found ===")
