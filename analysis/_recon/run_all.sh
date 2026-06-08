#!/bin/bash
# Reconstruct predictions for the final run's saved posteriors (instances 1,2,5;
# instances 3,4 saved no idata.nc). Re-runs each instance's own forward-sim against
# its SAVED posterior (pm.sample patched), inside the dlab Docker image so the HDF5
# append works on the ext4 work-dir. The headline (instance-1) also gets a
# sim_paths.npz for the price fan chart.
set -u

SRC=/home/camil/decision-lab/dlab-event-forecaster-oil-final
RUNREL=$(cd "$SRC" && ls -d parallel/run-* | head -1)
DRV=/mnt/c/Users/camil/Documents/Servicios/PYMC-LABS/repos/strait_of_hormuz_opening/iterations/oil_forecasting_final
IMG=dlab-event-forecaster

run_one () {
  inst="$1"; driver="$2"; script="$3"; cut="$4"; pred="$5"; hor="$6"
  echo "==================== $inst ===================="
  docker run --rm -e HDF5_USE_FILE_LOCKING=FALSE \
    -v "$SRC":/workspace \
    -v "$DRV":/s \
    -w "/workspace/$RUNREL/$inst" \
    "$IMG" \
    python "/s/_recon/$driver" "$script" "$cut" "$pred" "$hor" 2>&1 \
    | grep -vE "WARN the lock file|pixi lock|UserWarning|warnings.warn|^\s*$" | tail -25
  echo "exit: ${PIPESTATUS[0]}"
}

run_one instance-1 recon_headline.py forecast_wti.py  248 p_by_h_matrix horizon_trading_days
run_one instance-2 recon_driver.py   forecast_wti.py  249 p_by_h        horizon_trading
run_one instance-5 recon_driver.py   forecast_oil.py  313 p_by_h        horizon_trading_days
echo "ALLDONE"
