"""Reposition the label on plot 05 and generate the forest plot (fig 11) for P(3mo).

Run from the deliverable root (resolves paths relative to this file):

    python fix_plots.py
"""
import json
from pathlib import Path
import numpy as np
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
OUT = ROOT / "figures"

HEADLINE_P3 = None  # filled from instance-1 forecast.json below


def fix_why_jumpdiffusion():
    import pandas as pd
    from scipy.stats import kurtosis, skew
    df = pd.read_parquet(ROOT.parent / "data" / "raw" / "oil_futures.parquet")
    w = df["wti_close"].to_numpy(dtype=float)
    logp = np.where(w > 0, np.log(np.where(w > 0, w, 1.0)), np.nan)
    logr = np.diff(logp)
    logr = logr[np.isfinite(logr)]
    exk = float(kurtosis(logr))
    jump_frac = float(np.mean(np.abs(logr) > 3 * np.std(logr)) * 100)
    sk = float(skew(logr))

    labels = ["Excess kurtosis\n(returns)", ">3sigma jump days\n(% of obs)", "Return skew"]
    vals = [exk, jump_frac, sk]
    gauss = [0.0, 0.27, 0.0]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    xs = np.arange(len(labels))
    bars = ax.bar(xs, vals, 0.55, color=[RED + "60", ORANGE + "60", PURPLE + "60"],
                  edgecolor=[RED, ORANGE, PURPLE], linewidth=2, zorder=3)
    ax.bar(xs, gauss, 0.55, color="none", edgecolor=GREEN, linewidth=2, ls="--", zorder=4,
           label="Gaussian / OU expectation")

    for b, v in zip(bars, vals):
        label_y = max(v, 0) + 0.4
        ax.text(b.get_x() + b.get_width() / 2, label_y,
                f"{v:.1f}", ha="center", fontsize=12, fontweight="bold", color="#e6edf3")

    ax.axhline(0, color="#30363d", lw=1)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Value", fontsize=13)
    ax.set_ylim(-2, max(vals) * 1.15)
    ax.grid(True, axis="y", alpha=0.3); ax.set_axisbelow(True)
    ax.legend(fontsize=10, framealpha=0.3, edgecolor="#30363d")
    ax.set_title("Why a Jump-Diffusion: Fat Tails the Gaussian/OU Model Cannot Produce",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "05_why_jumpdiffusion.png", facecolor=BG); plt.close()
    print(f"OK 05_why_jumpdiffusion.png  (exkurt={exk:.1f}, jump%={jump_frac:.2f}, skew={sk:.2f})")


def plot_forest_p3mo():
    global HEADLINE_P3
    instances = []
    for i in range(1, 6):
        with open(ROOT / f"forecasters/instance-{i}/forecast.json") as f:
            d = json.load(f)
        p = d["p_event_by_horizon"][3] * 100
        lo = d["ci_low_by_horizon"][3] * 100
        hi = d["ci_high_by_horizon"][3] * 100
        instances.append({"p": p, "lo": lo, "hi": hi})
    HEADLINE_P3 = instances[0]["p"]

    names = [f"#{i+1}" for i in range(5)]
    names[0] += " (headline)"

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for i, inst in enumerate(instances):
        y = len(instances) - 1 - i
        color = COLORS[i]
        ax.plot([inst["lo"], inst["hi"]], [y, y], color=color, linewidth=3, alpha=0.5, zorder=3)
        ax.plot(inst["p"], y, "o", color=color, markersize=12, zorder=10,
                markeredgecolor="#0d1117", markeredgewidth=2)
        ax.text(inst["p"] + 1.5, y, f'{inst["p"]:.1f}%', va="center", fontsize=11,
                fontweight="bold", color=color)
        ax.text(inst["hi"] + 1.5, y - 0.15, f'[{inst["lo"]:.0f}, {inst["hi"]:.0f}]',
                va="center", fontsize=8, color=SUBTLE)

    ax.set_yticks(range(len(instances)))
    ax.set_yticklabels(list(reversed(names)), fontsize=11)
    ax.set_xlabel("P(WTI ≤ $68.26 by 3 months) %", fontsize=12)
    ax.set_xlim(0, 50)
    # Headroom above the top row so the headline label sits inside the axes,
    # clear of the title.
    ax.set_ylim(-0.5, 4.9)
    ax.axvline(HEADLINE_P3, color=BLUE, linestyle="--", alpha=0.3, linewidth=1)
    ax.text(HEADLINE_P3 + 0.7, 4.55, f"Headline: {HEADLINE_P3:.1f}%", fontsize=9,
            color=BLUE, alpha=0.6, va="center")
    ax.grid(True, axis="x", alpha=0.3); ax.set_axisbelow(True)
    ax.set_title("Forest Plot: P(Normalization by 3 Months) Across Forecasters",
                 fontsize=15, color="#e6edf3", pad=16)
    fig.tight_layout()
    fig.savefig(OUT / "11_forest_p3mo.png", facecolor=BG); plt.close()
    print(f"OK 11_forest_p3mo.png  (headline {HEADLINE_P3:.1f}%)")


if __name__ == "__main__":
    fix_why_jumpdiffusion()
    plot_forest_p3mo()
