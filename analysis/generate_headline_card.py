"""Render the headline forecast as a polished card-row graphic (figures/00_headline_card.png).

This is the single most important output of the analysis, so it gets a hero treatment:
one card per horizon with a large probability, a fill bar, and the 94% credible interval,
plus the two summary facts in the footer. Numbers are read from the headline forecaster
(instance-1) forecast.json so the card stays in sync with the run.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

BG = "#0d1117"; CARD = "#161b22"; EDGE = "#30363d"; TRACK = "#21262d"
WHITE = "#e6edf3"; SUBTLE = "#8b949e"; GREEN = "#3fb950"; AMBER = "#d29922"

ROOT = Path(__file__).resolve().parent
FORE = ROOT / "forecasters"          # surfaced forecast.json per instance
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)


def prob_color(p):
    """Amber (low probability) to green (high), linear in RGB."""
    t = max(0.0, min(1.0, p / 100.0))
    a = (0xD2, 0x99, 0x22); g = (0x3F, 0xB9, 0x50)
    return tuple((a[i] + (g[i] - a[i]) * t) / 255 for i in range(3))


def main():
    d = json.load(open(FORE / "instance-1" / "forecast.json"))
    idx = [2, 3, 4, 5]
    labels = ["1 month", "3 months", "6 months", "12 months"]
    dates = [d["horizon_dates"][i] for i in idx]
    p = [100 * d["p_event_by_horizon"][i] for i in idx]
    lo = [100 * d["ci_low_by_horizon"][i] for i in idx]
    hi = [100 * d["ci_high_by_horizon"][i] for i in idx]
    med = int(round(d["median_days_to_event"]))
    pnot = round(100 - p[-1])

    fig, ax = plt.subplots(figsize=(13, 5.8))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    aspect = 5.8 / 13

    ax.text(0.5, 0.965, "Will Oil Normalize? Probability WTI Closes ≤ $68.26",
            ha="center", va="top", fontsize=22, fontweight="bold", color=WHITE)
    ax.text(0.5, 0.885, "from $90.54 today (T0 = 2026-06-05)   ·   headline model: mean-reverting Ornstein-Uhlenbeck",
            ha="center", va="top", fontsize=12.5, color=SUBTLE)

    n = 4
    m = 0.030
    cw = (1 - (n + 1) * m) / n
    y0 = 0.305
    ch = 0.46
    for k in range(n):
        x = m + k * (cw + m)
        cx = x + cw / 2
        col = prob_color(p[k])
        ax.add_patch(FancyBboxPatch(
            (x, y0), cw, ch, boxstyle="round,pad=0,rounding_size=0.022",
            mutation_aspect=aspect, fc=CARD, ec=EDGE, lw=1.4, zorder=2))
        ax.text(cx, y0 + ch - 0.045, labels[k], ha="center", va="top",
                fontsize=15, fontweight="bold", color=WHITE, zorder=3)
        ax.text(cx, y0 + ch - 0.115, dates[k], ha="center", va="top",
                fontsize=10.5, color=SUBTLE, zorder=3)
        ax.text(cx, y0 + ch * 0.45, f"{p[k]:.1f}%", ha="center", va="center",
                fontsize=42, fontweight="bold", color=col, zorder=3)
        bx = x + 0.022; bw = cw - 0.044; by = y0 + 0.085; bh = 0.032
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0,rounding_size=0.016",
                     mutation_aspect=aspect, fc=TRACK, ec="none", zorder=3))
        if p[k] > 0.5:
            ax.add_patch(FancyBboxPatch((bx, by), bw * p[k] / 100, bh,
                         boxstyle="round,pad=0,rounding_size=0.016",
                         mutation_aspect=aspect, fc=col, ec="none", zorder=4))
        ax.text(cx, y0 + 0.038, f"94% CI   [{lo[k]:.0f}%, {hi[k]:.0f}%]",
                ha="center", va="center", fontsize=10.5, color=SUBTLE, zorder=3)

    ax.text(0.5, 0.185, f"Median time to normalize, if it happens:  ~{med} trading days  (~early October 2026)",
            ha="center", va="center", fontsize=13, color=WHITE)
    ax.text(0.5, 0.075, f"Probability it does NOT normalize within 12 months:  ~{pnot}%",
            ha="center", va="center", fontsize=13, color=WHITE)

    fig.savefig(OUT / "00_headline_card.png", facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close()
    print(f"OK 00_headline_card.png  (p={[round(v,1) for v in p]}, median={med}, pnot={pnot})")


if __name__ == "__main__":
    main()
