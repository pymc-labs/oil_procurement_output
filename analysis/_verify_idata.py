"""Verify each forecaster idata.nc contains BOTH parameters and predictions."""
import glob
import os

import arviz as az

paths = sorted(glob.glob("/workspace/parallel/*/instance-*/outputs/idata.nc"))
print(f"Found {len(paths)} idata.nc files\n")
for p in paths:
    inst = p.split("/instance-")[1].split("/")[0]
    idata = az.from_netcdf(p)
    groups = [g.strip("/") for g in idata.groups if g.strip("/")]
    has_param = "posterior" in groups
    has_pred = ("predictions" in groups) or ("posterior_predictive" in groups)
    # report variable names in the prediction group
    pred_group = "predictions" if "predictions" in groups else (
        "posterior_predictive" if "posterior_predictive" in groups else None
    )
    pred_vars = list(getattr(idata, pred_group).data_vars) if pred_group else []
    size_mb = os.path.getsize(p) / 1e6
    status = "OK" if (has_param and has_pred) else "MISSING"
    print(f"instance-{inst} [{size_mb:5.1f} MB] {status}")
    print(f"    groups: {groups}")
    print(f"    params(posterior)={has_param}  predictions={has_pred} (group={pred_group}, vars={pred_vars})\n")
