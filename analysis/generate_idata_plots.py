"""Posterior figures built from the reconstructed idata `predictions` groups
(and the headline's saved forward paths).

    python generate_idata_plots.py      # writes figures 07-10 to ./figures

Figures 07/08/09 read the posterior idatas from the raw `run/` tree, which is NOT
shipped in this showcase repo (the rendered PNGs are bundled in figures/). When `run/`
is absent this script regenerates only figure 10 (the five-forecaster overlay), which
is read from the surfaced forecast.json files. To rebuild 07-09, restore the run tree.
"""
import glob
import json
from pathlib import Path

import numpy as np
import arviz as az
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.facecolor": "#0d1117", "axes.facecolor": "#0d1117",
    "axes.edgecolor": "#30363d", "axes.labelcolor": "#c9d1d9",
    "text.color": "#c9d1d9", "xtick.color": "#8b949e", "ytick.color": "#8b949e",
    "grid.color": "#21262d", "grid.alpha": 0.6, "font.family": "sans-serif",
    "font.size": 12, "axes.titlesize": 16, "axes.titleweight": "bold",
    "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.3,
})
BLUE = "#58a6ff"; GREEN = "#3fb950"; ORANGE = "#d29922"; RED = "#f85149"
PURPLE = "#bc8cff"; TEAL = "#39d2c0"; SUBTLE = "#8b949e"; BG = "#0d1117"
COLORS = [BLUE, GREEN, TEAL, ORANGE, PURPLE]

ROOT = Path(__file__).resolve().parent
FORE = ROOT / "forecasters"
_runs = sorted(glob.glob(str(ROOT / "run" / "parallel" / "run-*")))
RUNP = Path(_runs[0]) if _runs else None  # raw run tree (posterior idatas); absent in the showcase repo
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
THRESHOLD = 68.26
HZ_LABELS = ["1d", "1wk", "1mo", "3mo", "6mo", "12mo"]
# Instances that persisted a full posterior (idata.nc) and were reconstructed with a
# predictions group. Instances 3 and 4 saved no usable idata, so the posterior-level
# figures cover these three (the headline, Instance 1, is included).
INSTANCES = [1, 2, 5]
PRIMARY = 1


def pred_draws(i):
    """(n_post, n_horizon) per-draw P(event) for instance i."""
    idata = az.from_netcdf(RUNP / f"instance-{i}" / "outputs" / "idata.nc")
    da = idata.predictions["p_event_by_horizon"]
    return da.stack(s=("chain", "draw")).transpose("s", "horizon").values


def plot_normalization_curve():
    """Posterior distribution of the normalization curve for the primary forecaster."""
    p = pred_draws(PRIMARY) * 100  # (n_post, 6)
    x = np.arange(p.shape[1])
    med = np.median(p, axis=0)
    lo, hi = np.percentile(p, [3, 97], axis=0)
    q25, q75 = np.percentile(p, [25, 75], axis=0)
    fig, ax = plt.subplots(figsize=(12, 6))
    # thin sample of draws
    rng = np.random.default_rng(0)
    for j in rng.choice(p.shape[0], size=120, replace=False):
        ax.plot(x, p[j], color=BLUE, alpha=0.04, lw=1)
    ax.fill_between(x, lo, hi, color=BLUE, alpha=0.15, label="94% credible")
    ax.fill_between(x, q25, q75, color=BLUE, alpha=0.25, label="50% credible")
    ax.plot(x, med, color="#e6edf3", lw=2.6, marker="o", ms=7, label="posterior median")
    for xi, m in zip(x, med):
        ax.text(xi, m + 3, f"{m:.0f}%", ha="center", fontsize=10, fontweight="bold", color="#e6edf3")
    ax.axhline(50, color=SUBTLE, ls=":", alpha=0.4)
    ax.set_xticks(x); ax.set_xticklabels(HZ_LABELS, fontsize=12)
    ax.set_ylabel("P(WTI <= $68.26) %", fontsize=13); ax.set_ylim(-2, 100)
    ax.grid(True, alpha=0.3); ax.legend(loc="upper left", fontsize=10, framealpha=0.3, edgecolor="#30363d")
    ax.set_title("Normalization Curve from the Reconstructed Predictions (Primary Forecaster)",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "07_normalization_curve.png", facecolor=BG); plt.close()
    print("OK 07_normalization_curve.png")


def plot_prediction_uncertainty():
    """Per-draw P(3 months) distribution for each forecaster (from predictions group)."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for k, i in enumerate(INSTANCES):
        p3 = pred_draws(i)[:, 3] * 100
        ax.hist(p3, bins=40, histtype="stepfilled", color=COLORS[k] + "30",
                edgecolor=COLORS[k], linewidth=1.4, label=f"#{i}  (mean {p3.mean():.0f}%)", density=True)
    ax.set_xlabel("P(WTI <= $68.26 by 3 months) %  — per posterior draw", fontsize=12)
    ax.set_ylabel("density", fontsize=12)
    ax.grid(True, alpha=0.3); ax.legend(fontsize=10, framealpha=0.3, edgecolor="#30363d")
    ax.set_title("Posterior Uncertainty in P(3 months): Five Forecasters Overlap Heavily",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "08_prediction_uncertainty.png", facecolor=BG); plt.close()
    print("OK 08_prediction_uncertainty.png")


def plot_price_fanchart():
    """Price fan chart from instance-3's saved standardized forward paths."""
    npz = np.load(RUNP / f"instance-{PRIMARY}" / "outputs" / "sim_paths.npz")
    paths = npz["paths"]                     # (n_post, n_paths, T+1) standardized log-price
    mean_log = float(npz["mean_log"]); std_log = float(npz["std_log"])
    price = np.exp(paths * std_log + mean_log)
    flat = price.reshape(-1, price.shape[-1])  # (draws*paths, T+1)
    T = flat.shape[1]
    days = np.arange(T)
    med = np.median(flat, axis=0)
    p05, p95 = np.percentile(flat, [5, 95], axis=0)
    p25, p75 = np.percentile(flat, [25, 75], axis=0)
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.fill_between(days, p05, p95, color=BLUE, alpha=0.12, label="90% band")
    ax.fill_between(days, p25, p75, color=BLUE, alpha=0.22, label="50% band")
    ax.plot(days, med, color="#e6edf3", lw=2.2, label="median path")
    ax.axhline(THRESHOLD, color=ORANGE, ls=":", lw=1.8, label=f"threshold ${THRESHOLD:.2f}")
    ax.set_xlabel("Calendar days from T0 (2026-06-05)", fontsize=12)
    ax.set_ylabel("WTI ($/bbl)", fontsize=13)
    ax.set_xlim(0, T - 1)
    ax.grid(True, alpha=0.3); ax.legend(loc="upper right", fontsize=10, framealpha=0.3, edgecolor="#30363d")
    ax.set_title("Forward Price Fan Chart (Headline Instance-1 Posterior Paths -> Price Space)",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "09_price_fanchart.png", facecolor=BG); plt.close()
    print("OK 09_price_fanchart.png")


def plot_forecaster_overlay():
    """All five forecasters' mean normalization curves, read from forecast.json.

    The per-horizon mean P(event) is recorded in every forecaster's forecast.json,
    so this covers all five instances (not just the three that persisted an idata).
    """
    x = np.arange(6)
    fig, ax = plt.subplots(figsize=(12, 6))
    for i in range(1, 6):
        with open(FORE / f"instance-{i}" / "forecast.json") as fh:
            d = json.load(fh)
        m = [100 * v for v in d["p_event_by_horizon"]]
        ax.plot(x, m, color=COLORS[i - 1], lw=2, marker="o", ms=6, label=f"forecaster #{i}")
    ax.axhline(50, color=SUBTLE, ls=":", alpha=0.4)
    ax.set_xticks(x); ax.set_xticklabels(HZ_LABELS, fontsize=12)
    ax.set_ylabel("P(WTI <= $68.26) %", fontsize=13); ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3); ax.legend(fontsize=10, framealpha=0.3, edgecolor="#30363d", loc="upper left")
    ax.set_title("All Five Forecasters' Normalization Curves",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "10_forecaster_overlay.png", facecolor=BG); plt.close()
    print("OK 10_forecaster_overlay.png")


if __name__ == "__main__":
    if RUNP is not None:
        plot_normalization_curve()
        plot_prediction_uncertainty()
        plot_price_fanchart()
    else:
        print("No run/ tree found (posterior idatas not shipped); figures 07-09 use the "
              "bundled PNGs in figures/. Skipping their regeneration.")
    plot_forecaster_overlay()
    print(f"\nFigures written to {OUT}")
