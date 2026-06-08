"""Publication figures for the iteration-2 oil-procurement forecast (2007-2026 data).

Data-driven: reads the REAL WTI history and the five forecasters' forecast.json from
the run tree (no hard-coded synthetic series). Run from the deliverable root:

    python generate_plots.py            # writes figures 01-06 to ./figures
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data"          # raw parquets live at the repo root
FORE = ROOT / "forecasters"
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

THRESHOLD = 68.26
T0 = pd.Timestamp("2026-06-05")
CURRENT = 90.54
HZ_DATES = [pd.Timestamp(d) for d in
            ["2026-06-08", "2026-06-12", "2026-07-06", "2026-09-07", "2026-12-07", "2027-06-07"]]
HZ_LABELS = ["1 day", "1 week", "1 month", "3 months", "6 months", "12 months"]


def load_forecasts():
    """Return dict instance -> forecast.json, and the primary (instance-4)."""
    fc = {}
    for i in range(1, 6):
        with open(FORE / f"instance-{i}" / "forecast.json") as fh:
            fc[i] = json.load(fh)
    return fc


def load_wti():
    df = pd.read_parquet(DATA / "raw" / "oil_futures.parquet")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df[["date", "wti_close"]].dropna()


FC = load_forecasts()


def plot_price_timeline():
    df = load_wti()
    d = df["date"]; w = df["wti_close"]
    fig, ax = plt.subplots(figsize=(15, 6.5))
    ax.plot(d, w, color=BLUE, linewidth=0.9, zorder=3)
    ax.axhline(THRESHOLD, color=ORANGE, linestyle=":", linewidth=1.6,
               label=f"Normalization threshold (${THRESHOLD:.2f})")
    ax.fill_between(d, w.min() - 5, THRESHOLD, color=GREEN, alpha=0.04)

    def mark(lo, hi, text, color, dy=8):
        m = (d >= pd.Timestamp(lo)) & (d <= pd.Timestamp(hi))
        if not m.any():
            return
        sub = w[m]
        idx = sub.idxmax()
        ax.annotate(text, xy=(d[idx], w[idx]), xytext=(0, dy), textcoords="offset points",
                    fontsize=9, color=color, fontweight="bold", ha="center",
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.0))

    # GFC peak, 2022 spike, 2026 spike (peaks); COVID trough (min) annotated separately
    mark("2008-01-01", "2008-12-31", f"2008 GFC peak ${w[(d>='2008-01-01')&(d<='2008-12-31')].max():.0f}", RED)
    mark("2022-01-01", "2022-12-31", f"2022 Ukraine spike ${w[(d>='2022-01-01')&(d<='2022-12-31')].max():.0f}", ORANGE)
    mark("2026-01-01", "2026-12-31", f"2026 peak ${w[(d>='2026-01-01')&(d<='2026-12-31')].max():.0f}", RED)
    covid = w[(d >= "2020-01-01") & (d <= "2020-12-31")]
    if len(covid):
        ci = covid.idxmin()
        ax.annotate(f"2020 COVID low ${w[ci]:.0f}", xy=(d[ci], w[ci]), xytext=(0, -22),
                    textcoords="offset points", fontsize=9, color=PURPLE, fontweight="bold",
                    ha="center", arrowprops=dict(arrowstyle="->", color=PURPLE, lw=1.0))
    ax.annotate(f"T0 ${CURRENT:.2f}", xy=(T0, CURRENT), xytext=(-70, 18),
                textcoords="offset points", fontsize=10, color=BLUE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.2))

    ax.set_ylabel("WTI front-month close ($/bbl)", fontsize=13)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.3, edgecolor="#30363d")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_title("19 Years of WTI (2007-2026): Multiple Regimes Now Inform the Forecast",
                 fontsize=17, color="#e6edf3", pad=14)
    fig.savefig(OUT / "01_price_timeline.png", facecolor=BG); plt.close()
    print("OK 01_price_timeline.png")


def plot_headline_forecast():
    from scipy.interpolate import PchipInterpolator
    p = FC[1]  # primary (headline: Instance 1, mean-reverting OU)
    probs = [100 * x for x in p["p_event_by_horizon"]]
    lo = [100 * x for x in p["ci_low_by_horizon"]]
    hi = [100 * x for x in p["ci_high_by_horizon"]]
    days = [(dt - T0).days for dt in HZ_DATES]
    fig, ax = plt.subplots(figsize=(12, 6))
    xf = np.linspace(0, days[-1], 300)
    ip = PchipInterpolator([0] + days, [0] + probs)
    il = PchipInterpolator([0] + days, [0] + lo)
    ih = PchipInterpolator([0] + days, [0] + hi)
    xd = [T0 + pd.Timedelta(days=int(v)) for v in xf]
    ax.fill_between(xd, np.clip(il(xf), 0, 100), np.clip(ih(xf), 0, 100), color=BLUE, alpha=0.13,
                    label="94% credible interval")
    ax.plot(xd, np.clip(ip(xf), 0, 100), color=BLUE, linewidth=2.6, zorder=5)
    for dt, pr in zip(HZ_DATES, probs):
        ax.plot(dt, pr, "o", color=BLUE, ms=9, zorder=10, markeredgecolor=BG, markeredgewidth=2)
        ax.text(dt, pr + 3.5, f"{pr:.0f}%", ha="center", fontsize=11, fontweight="bold", color=BLUE)
    med = T0 + pd.Timedelta(days=int(p["median_days_to_event"]))
    ax.axvline(med, color=GREEN, ls="--", lw=1.4, alpha=0.7)
    ax.text(med, 62, f"  Median ~{int(p['median_days_to_event'])} trading days", color=GREEN,
            fontsize=10, fontweight="bold", va="center")
    ax.axhline(50, color=SUBTLE, ls=":", alpha=0.4)
    pnot = 100 * (1 - p["p_event_by_horizon"][-1])
    ax.annotate(f"~{pnot:.0f}% never normalize\nwithin 12 months", xy=(HZ_DATES[-1], probs[-1]),
                xytext=(HZ_DATES[3], 82), fontsize=10, color=RED, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    ax.set_ylabel("P(WTI <= $68.26) %", fontsize=13); ax.set_ylim(-2, 100)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.grid(True, alpha=0.3); ax.legend(loc="upper left", fontsize=11, framealpha=0.3, edgecolor="#30363d")
    ax.set_title("WTI Normalization Forecast (Primary: Mean-Reverting OU / Continuous-Driver)",
                 fontsize=16, color="#e6edf3", pad=14)
    fig.savefig(OUT / "02_headline_forecast.png", facecolor=BG); plt.close()
    print("OK 02_headline_forecast.png")


def plot_forecaster_convergence():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.2, 1]})
    colors = [BLUE, GREEN, TEAL, ORANGE, PURPLE]
    p3 = [100 * FC[i]["p_event_by_horizon"][3] for i in range(1, 6)]
    lo3 = [100 * FC[i]["ci_low_by_horizon"][3] for i in range(1, 6)]
    hi3 = [100 * FC[i]["ci_high_by_horizon"][3] for i in range(1, 6)]
    med = [FC[i]["median_days_to_event"] for i in range(1, 6)]
    x = np.arange(5)
    for i in range(5):
        ax1.plot([i, i], [lo3[i], hi3[i]], color=colors[i], lw=3, alpha=0.4)
        ax1.plot(i, p3[i], "o", color=colors[i], ms=12, markeredgecolor=BG, markeredgewidth=2)
        ax1.text(i, p3[i] + 2.5, f"{p3[i]:.0f}%", ha="center", fontsize=10, fontweight="bold", color=colors[i])
    consensus = float(np.mean(p3))
    ax1.axhline(consensus, color=SUBTLE, ls="--", alpha=0.5)
    ax1.text(4.4, consensus + 1.5, f"mean {consensus:.0f}%", color=SUBTLE, ha="right", fontsize=9)
    ax1.set_xticks(x); ax1.set_xticklabels([f"#{i}" for i in range(1, 6)], fontsize=12)
    ax1.set_ylabel("P(WTI <= $68.26 by 3 months) %", fontsize=11)
    ax1.set_ylim(0, max(hi3) + 10); ax1.grid(True, axis="y", alpha=0.3); ax1.set_axisbelow(True)
    ax1.set_title(f"P(3 months): all 5 in [{min(p3):.0f}%, {max(p3):.0f}%]", fontsize=14, color="#e6edf3")

    bars = ax2.barh(x, med, 0.55, color=[c + "80" for c in colors], edgecolor=colors, linewidth=1.5)
    for i, (b, m) in enumerate(zip(bars, med)):
        ax2.text(m + 2, i, f"{int(m)} d", va="center", fontsize=11, fontweight="bold", color=colors[i])
    ax2.set_yticks(x); ax2.set_yticklabels([f"#{i}" for i in range(1, 6)], fontsize=12)
    ax2.set_xlabel("Median trading days to normalization", fontsize=11)
    ax2.set_xlim(0, max(med) + 20); ax2.grid(True, axis="x", alpha=0.3); ax2.set_axisbelow(True); ax2.invert_yaxis()
    ax2.set_title("Median time to event", fontsize=14, color="#e6edf3")
    fig.suptitle("Five Independent Forecasters -> Mean-Reverting Models, Tightly Clustered Numbers",
                 fontsize=17, y=1.02, color="#e6edf3")
    fig.tight_layout()
    fig.savefig(OUT / "03_forecaster_convergence.png", facecolor=BG); plt.close()
    print("OK 03_forecaster_convergence.png")


def plot_procurement_decision():
    p = FC[1]
    idx = {"1 month": 2, "3 months": 3, "6 months": 4, "12 months": 5}
    horizons = list(idx.keys())
    p_norm = [100 * p["p_event_by_horizon"][idx[h]] for h in horizons]
    p_elev = [100 - v for v in p_norm]
    x = np.arange(len(horizons)); wbar = 0.38
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - wbar / 2, p_elev, wbar, color=RED + "80", edgecolor=RED, linewidth=1.5, label="P(stay elevated)")
    ax.bar(x + wbar / 2, p_norm, wbar, color=GREEN + "80", edgecolor=GREEN, linewidth=1.5, label="P(normalized)")
    for i in range(len(horizons)):
        ax.text(i - wbar / 2, p_elev[i] + 1.5, f"{p_elev[i]:.0f}%", ha="center", fontsize=10, color=RED, fontweight="bold")
        ax.text(i + wbar / 2, p_norm[i] + 1.5, f"{p_norm[i]:.0f}%", ha="center", fontsize=10, color=GREEN, fontweight="bold")
    ax.axhline(50, color=SUBTLE, ls=":", alpha=0.4)
    ax.set_xticks(x); ax.set_xticklabels(horizons, fontsize=12)
    ax.set_ylabel("Probability (%)", fontsize=13); ax.set_ylim(0, 105)
    ax.legend(fontsize=11, framealpha=0.3, edgecolor="#30363d", loc="upper center")
    ax.grid(True, axis="y", alpha=0.3); ax.set_axisbelow(True)
    ax.set_title("Procurement Read: Lock-in is Favoured Near-Term, a Coin-Flip by 6 Months",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "04_procurement_decision.png", facecolor=BG); plt.close()
    print("OK 04_procurement_decision.png")


def plot_why_jumpdiffusion():
    df = load_wti()
    w = df["wti_close"].to_numpy(dtype=float)
    # WTI went negative on 2020-04-20, so log() is undefined across that transition.
    # Compute log returns only on consecutive strictly-positive closes.
    logp = np.where(w > 0, np.log(np.where(w > 0, w, 1.0)), np.nan)
    logr = np.diff(logp)
    logr = logr[np.isfinite(logr)]
    from scipy.stats import kurtosis, skew
    exk = float(kurtosis(logr))          # excess kurtosis
    jump_frac = float(np.mean(np.abs(logr) > 3 * np.std(logr)) * 100)
    sk = float(skew(logr))
    labels = ["Excess kurtosis\n(returns)", ">3sigma jump days\n(% of obs)", "Return skew"]
    vals = [exk, jump_frac, sk]
    gauss = [0.0, 0.27, 0.0]  # Gaussian expectation (0.27% of N(0,1) beyond 3 sigma)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    xs = np.arange(len(labels))
    bars = ax.bar(xs, vals, 0.55, color=[RED + "60", ORANGE + "60", PURPLE + "60"],
                  edgecolor=[RED, ORANGE, PURPLE], linewidth=2, zorder=3)
    ax.bar(xs, gauss, 0.55, color="none", edgecolor=GREEN, linewidth=2, ls="--", zorder=4,
           label="Gaussian / OU expectation")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.02 * max(vals) if v >= 0 else -0.06 * max(vals)),
                f"{v:.1f}", ha="center", fontsize=12, fontweight="bold", color="#e6edf3")
    ax.axhline(0, color="#30363d", lw=1)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Value", fontsize=13); ax.grid(True, axis="y", alpha=0.3); ax.set_axisbelow(True)
    ax.legend(fontsize=10, framealpha=0.3, edgecolor="#30363d")
    ax.set_title("Why a Jump-Diffusion: Fat Tails the Gaussian/OU Model Cannot Produce",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "05_why_jumpdiffusion.png", facecolor=BG); plt.close()
    print(f"OK 05_why_jumpdiffusion.png  (exkurt={exk:.1f}, jump%={jump_frac:.2f}, skew={sk:.2f})")


def plot_inverse_probabilities():
    horizons = ["1 month", "3 months", "6 months", "12 months"]
    idxs = [2, 3, 4, 5]
    # cross-forecaster mean per horizon
    p_norm = [100 * np.mean([FC[i]["p_event_by_horizon"][k] for i in range(1, 6)]) for k in idxs]
    p_elev = [100 - v for v in p_norm]
    x = np.arange(4); wbar = 0.38
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(x - wbar / 2, p_elev, wbar, color=RED + "80", edgecolor=RED, linewidth=1.5, label="P(still elevated)")
    ax.bar(x + wbar / 2, p_norm, wbar, color=GREEN + "80", edgecolor=GREEN, linewidth=1.5, label="P(normalized)")
    for i in range(4):
        ax.text(i - wbar / 2, p_elev[i] + 1.5, f"{p_elev[i]:.0f}%", ha="center", fontsize=10, color=RED, fontweight="bold")
        ax.text(i + wbar / 2, p_norm[i] + 1.5, f"{p_norm[i]:.0f}%", ha="center", fontsize=10, color=GREEN, fontweight="bold")
    ax.axhline(50, color=SUBTLE, ls=":", alpha=0.4)
    ax.set_xticks(x); ax.set_xticklabels(horizons, fontsize=12)
    ax.set_ylabel("Probability (%)", fontsize=13); ax.set_ylim(0, 105)
    ax.legend(fontsize=11, framealpha=0.3, edgecolor="#30363d", loc="upper right")
    ax.grid(True, axis="y", alpha=0.3); ax.set_axisbelow(True)
    ax.set_title("Cross-Forecaster Mean: Odds Favour Elevation Until ~6 Months",
                 fontsize=15, color="#e6edf3", pad=14)
    fig.savefig(OUT / "06_inverse_probabilities.png", facecolor=BG); plt.close()
    print("OK 06_inverse_probabilities.png")


if __name__ == "__main__":
    plot_price_timeline()
    plot_headline_forecast()
    plot_forecaster_convergence()
    plot_procurement_decision()
    plot_why_jumpdiffusion()
    plot_inverse_probabilities()
    print(f"\nFigures 01-06 written to {OUT}")
