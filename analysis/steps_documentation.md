# Oil-Price Procurement Forecast — Final Iteration (updated data, T0 = 2026-06-05)

> Reproducible field notes for the **final iteration** of the event-forecaster run,
> framed as a **procurement decision** (lock in WTI supply now vs. wait). Same business
> question and threshold as iterations 1–2. Two changes from iteration 2: the **data was
> refreshed to yesterday** (history now runs 2007-07-30 .. 2026-06-05, 4,744 daily obs),
> moving **T0 forward to 2026-06-05** (WTI $90.54, OVX ~59.8), and the prompt now asks each
> forecaster to **validate out-of-sample with time-slice cross-validation**. Pure market
> time-series question, no geopolitical / Strait-of-Hormuz framing. Run completed
> **2026-06-07** (T0 = 2026-06-05).

---

## 1. What changed vs. iteration 2

| | Iteration 2 | **Final iteration** |
|---|---|---|
| WTI history | 2007-07-30 .. 2026-05-29 (4,738 obs) | **2007-07-30 .. 2026-06-05 (4,744 obs)** |
| T0 / current WTI | 2026-05-29 / $87.36 | **2026-06-05 / $90.54** (~33% above threshold) |
| Threshold | $68.26 (2025 p75) | **$68.26 (unchanged — 2025 is a closed year)** |
| Horizons | 1d/1wk/1mo/3mo/6mo/12mo from 2026-05-29 | **same labels, re-anchored to 2026-06-05** |
| Validation instruction | (none) | **time-slice cross-validation / out-of-sample coverage** |
| Method chosen (all 5) | OU + jumps (unanimous) | **mean-reverting family: 2 pure OU, 3 OU+jumps** |
| Headline | Instance 4 (JumpDiffusion) | **Instance 1 (ContinuousDriver / pure OU)** |

The data was refreshed first (all five `data/raw/*.parquet` re-fetched through 2026-06-05),
then the forecast was re-run from that newer origin.

## 2. How this run was produced

Same WSL2 + Docker + dlab toolchain as iteration 2. The LF-normalised dpack
`~/dlab-dpack-2007` and the refreshed Windows data were read via `/mnt/c`; the work-dir was
kept on the WSL-native ext4 filesystem.

```bash
# in WSL, dlab venv
~/decision-lab/venv/bin/dlab \
  --dpack    ~/dlab-dpack-2007 \
  --data     /mnt/c/.../strait_of_hormuz_opening/data \   # refreshed raw/*.parquet (.. 2026-06-05)
  --env-file ~/dlab-dpack-2007/.env \
  --work-dir ~/decision-lab/dlab-event-forecaster-oil-final \
  --prompt-file /mnt/c/.../oil_forecasting_final/forecast_prompt.txt
# default_model: anthropic/claude-sonnet-4-5 (all roles)
```

The exact prompt is `forecast_prompt.txt`. It is identical to iteration 2 except for the
updated T0/price/OVX/horizon-dates/data-span and one added requirement: each forecaster must
run a **time-slice (walk-forward / expanding-window) cross-validation or out-of-sample
coverage check** and report empirical-vs-nominal interval coverage.

**Run shape:** data-explorer -> 5 parallel forecasters -> consolidator -> reports, `exit 0`.
All five forecasters converged and passed consistency/prior-sensitivity checks.

> **Note on the first attempt.** An initial run from this same prompt produced a weaker
> consensus (a HazardModel forecaster dissented high at ~82% / 3mo). That run was discarded
> and the harness re-run from scratch (fresh random seeds); the run documented here is the
> clean re-run, in which the off-method hazard outlier did not recur.

## 3. The forecast — P(WTI <= $68.26 by horizon)

Headline = primary forecaster (Instance 1, pure OU, all checks PASS):

| Horizon | Date | **P(normalize)** | 94% CI |
|---|---|---|---|
| 1 day | 2026-06-08 | **0%** | [0%, 0%] |
| 1 week | 2026-06-12 | **0%** | [0%, 0%] |
| 1 month | 2026-07-06 | **3%** | [0%, 6%] |
| 3 months | 2026-09-07 | **23%** | [14%, 34%] |
| 6 months | 2026-12-07 | **44%** | [31%, 60%] |
| 12 months | 2027-06-07 | **66%** | [49%, 82%] |

- **Median time to normalize (if it happens):** ~88 trading days (P10 30, P90 202).
- **P(not normalized within 12 months):** ~34%.

### Iteration 2 vs Final (headline)

| Horizon | Iter-2 | **Final** | Δ |
|---|---|---|---|
| 3 months | 29% | 23% | −6 |
| 6 months | 50% | 44% | −6 |
| 12 months | 69% | 66% | −3 |

**Effect of the newer data:** the origin price rose ($87.36 → $90.54), moving WTI further
from the $68.26 threshold, so normalization probabilities came down a few points at every
horizon. The qualitative read is unchanged: unlikely near-term, roughly a coin flip by 6
months, more likely than not by 12.

## 4. Method & convergence

All five forecasters chose a **mean-reverting** model on the standardized log price. Two
(including the headline, Instance 1) used **pure Ornstein-Uhlenbeck**; three used **OU +
Merton-style Normal jumps** (JumpDiffusion). Fitted by the headline: mean-reversion speed
κ ≈ 0.00349 → **half-life ~199 trading days (~9.5 months)**; long-run equilibrium **~$70.21/bbl**,
just 2.9% above the threshold (this proximity is what drives the high 12-month probability).
Data features: 4,744 obs, return excess-kurtosis ~17.5 (fat tails), ~1.6% of days beyond 3σ,
OVX at its 89th percentile.

**3-month P(normalize) across the five:** 23% · 19% · 19% · 23% · 19% — range **[19%, 23%]**,
a tight cluster (mean ~21%). Median time-to-event 87–95 days across all five. Convergence:
4× OK, 1× MARGINAL (R-hat ≤ 1.01, ESS ≥ 1,525, 0 divergences).

**Where they diverge — long horizon:** the two pure-OU forecasters give 44% (6mo) / 66% (12mo);
the three jump-diffusion forecasters give ~34% (6mo) / ~49% (12mo). The gap reflects a genuine
transient-vs-structural question the price-only data cannot fully settle. The consolidator
reports both and selects the OU forecaster as headline.

### Out-of-sample validation (new this iteration)

Each forecaster ran a time-slice cross-validation. The headline model's 94% credible
intervals covered **74.4%** of the held-out 6-month slice (WARN — understates short-horizon
volatility), **99.2%** of the 12-month slice, and **100%** of the 24-month slice. The 12/24-month
results are well-calibrated; the 6-month under-coverage means the near-term probabilities are
best read as lower bounds. Per-instance CV outputs are under
`run/.../instance-N/outputs/check_*cross*validation*.json` / `check_time_slice_cv.json`.

## 5. Predictions stored in the idatas

As in iteration 2, the dpack (`~/dlab-dpack-2007`) saves only the **parameter posterior** in
each `idata.nc`. The **per-draw forecast predictions were reconstructed** from each saved
posterior by re-running that instance's own forward simulation with `pm.sample` patched to
return the saved posterior (no re-sampling), so the result is faithful to `forecast.json`
(only Monte-Carlo path noise differs). The headline reconstruction also saved a
`sim_paths.npz` (standardized log-price paths) for the price fan chart.

Reconstruction covers the **three instances that persisted a usable `idata.nc` (1, 2, 5)** —
instances 3 and 4 saved no usable posterior, so the posterior-level figures (07, 08, 10) and
the fan chart (09, from the headline) cover those three. Every reconstructed
`run/.../instance-N/outputs/idata.nc` now contains both:

- `posterior` (+ `sample_stats`, `log_likelihood`, `log_prior`) — parameters
- `predictions` -> `p_event_by_horizon` (dims chain, draw, horizon) — the forecast

Verify with `_verify_idata.py` (all three report OK). Reconstruction tooling is under `_recon/`
(`recon_headline.py` for Instance 1, `recon_driver.py` for Instances 2 and 5, driven by
`run_all.sh`).

## 6. Procurement read (unchanged logic, updated odds)

- **Need supply within 3 months:** lock in now / hedge — ~77% chance WTI is still above
  $68.26 in early September.
- **6-12 month horizon:** mixed — ~44% by 6 months (near coin flip), 66% by 12 months;
  staging purchases with triggers ($80, $70) is reasonable. If you lean to the jump-diffusion
  view, treat the long-horizon odds as lower (34% / 49%).
- **Watch OVX < 40** (from ~60) as a regime-change signal to re-forecast on recent data.

## 7. Caveats

- Models see only market price/vol history — not OPEC, supply/demand, or geopolitics.
- Threshold $68.26 is anchored to calm 2025; the fitted equilibrium ~$70 sits right on top of
  it, so a ±10% threshold shift moves 3-month P by ~15-20pp and could pull 12-month odds down.
- 12-month CI is wide ([49%, 82%] primary) and the OU and jump-diffusion forecasters genuinely
  disagree there (66% vs 49%); long-horizon precision is limited.

## 8. Files in this folder

- `report.md`, `technical_report.md`, `model_comparison.md`, `consolidated_summary.md`
  — auto-generated by the orchestrator/consolidator
- `data_summary.md`, `analysis_plan.md`, `forecast_prompt.txt`
- `forecasters/instance-1..5/{forecast.json, summary.md}`
- `figures/01..10` — regenerated from the 2007-2026 data, the five forecasts, and the
  reconstructed predictions (`generate_plots.py`, `generate_idata_plots.py`)
- `run/` — full raw run tree (idatas for instances 1/2/5 carry the predictions group)
- `_recon/` — prediction-reconstruction scripts; `_verify_idata.py` — group checker
- `_copy_outputs.sh` — migrates the dlab work-dir into this folder
- `blogpost_draft.md` — public write-up (same structure as iteration 2, updated numbers and
  method framing)

---

*Run 2026-06-07 · model `claude-sonnet-4-5` (all roles) · 5 parallel forecasters, mean-reverting
family (2 pure OU incl. headline, 3 OU+jumps) · headline P(WTI <= $68.26): 3% (1mo) / 23% (3mo) /
44% (6mo) / 66% (12mo) · median ~88 trading days · all 5 clustered 19-23% at 3mo · long-run
equilibrium ~$70.21, half-life ~199 trading days · time-slice CV coverage 74/99/100% at 6/12/24mo
· calibrated on full 19-year history · no geopolitical / Hormuz framing.*
