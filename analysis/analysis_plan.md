# Analysis Plan

## Question

**"When will the front-month WTI crude oil price return to our defined normalization threshold?"**

**Event / Resolution Criterion:**  
WTI front-month close has fallen to or below **$68.26/bbl** (the 75th percentile of the 2025 calendar-year WTI distribution) and stayed there.

**Current State (T0 = 2026-06-05):**  
- WTI close: **$90.54/bbl** (32.7% above threshold)
- OVX (oil volatility): **~59.79** (elevated)
- The price is currently elevated relative to 2025 baseline (mean ~$65, 75th pct ~$68.26, range ~$55–$80)
- This is treated as a market dislocation in price level — a time-series / mean-reversion phenomenon

## Horizon dates

Forecast P(WTI ≤ $68.26 by horizon) with credible intervals at:

| Horizon | Calendar date | Days from T0 |
|---------|--------------|--------------|
| 1 day | 2026-06-08 | ~1 |
| 1 week | 2026-06-12 | ~7 |
| 1 month | 2026-07-06 | ~31 |
| 3 months | 2026-09-07 | ~94 |
| 6 months | 2026-12-07 | ~185 |
| 12 months | 2027-06-07 | ~367 |

## Data available

**Primary series: WTI crude oil futures close**
- File: `data/raw/oil_futures.parquet`, column `wti_close`
- **4,744 daily observations** from 2007-07-30 to 2026-06-05 (18.86 years)
- Current value (2026-06-05): **$90.54**
- Full-period statistics: mean $73.11, std $21.89, range [$-37.63, $145.29]
- 2025 baseline: mean $64.74, std $5.29 (low volatility)
- 2026 partial (107 obs): mean $83.44, std $17.41 (regime shift or transient shock)

**Distinct regimes in 19-year history:**
- 2007–2008: Commodity boom → GFC crash
- 2009–2013: Post-GFC recovery, high plateau
- 2014–2016: Oversupply collapse (lowest period)
- 2017–2019: Stabilization
- 2020: COVID demand shock (includes negative price anomaly on 2020-04-20: $-37.63)
- 2021–2022: Post-COVID recovery + supply shock
- 2023–2025: Normalization (low volatility)
- 2026: Recent upswing (current state)

**Auxiliary series:**
- **OVX** (crude oil volatility index): 4,919 obs, r = -0.322 with WTI (only independent indicator)
- **S&P 500**: 4,744 obs, r = -0.126 with WTI (weak)
- **Brent crude**: r = +0.974 with WTI (collinear, not independent)
- **Asian indices** (KOSPI, Nikkei, TOPIX): highly collinear with S&P (r > 0.84)
- **Tanker equities**: 46,480 rows (12 tickers, long format panel)

**Data structure:**
- Long daily time series suitable for continuous stochastic process models
- Non-stationary levels (lag-1 autocorr = 0.995)
- Multiple regime history with different mean/volatility structures
- One extreme outlier (COVID negative price) requiring special handling
- No discrete historical event durations or labeled threshold-crossing episodes

**Data quality flags:**
- COVID negative price anomaly (2020-04-20: $-37.63) — models using levels must handle this
- High collinearity among auxiliary indicators (use WTI + OVX only)
- Regime heterogeneity: volatility varies 3–5× across periods
- 2026 structural break: mean jumped from $64.74 (2025) to $83.44 (2026 partial)
- Non-stationarity: must use returns or explicit mean-reversion models

## Current state

**Actors & situation:**
- Global oil market: WTI price is currently **$90.54**, having risen from a 2025 baseline of ~$65 (mean)
- The threshold $68.26 represents the 75th percentile of 2025 prices (a "normal high" level)
- Current elevation (~$90) suggests either a transient supply shock, demand surge, or regime shift
- OVX at ~59.79 indicates elevated market uncertainty
- This is a **mean-reversion question**: will the price fall back to ≤$68.26, and when?

**Domain context:**
- Oil prices are driven by supply/demand balance, geopolitical events, OPEC decisions, inventory levels
- The 2025 baseline was calm (low volatility, mean ~$65); 2026 shows a sharp upswing
- Historical precedent: prices have mean-reverted after shocks (2008 GFC, 2014 oversupply, 2020 COVID, 2022 supply shock)
- However, regime changes can persist (2014–2016 stayed low for ~2 years)

## Approach

**N = 5 independent forecasters** will be launched in parallel via `parallel-agents`.

**No method assignments are made by the orchestrator.** Method selection is left entirely to each forecaster.

Each forecaster will receive:
- The question verbatim
- Horizon dates (1d, 1w, 1m, 3m, 6m, 12m)
- Full `data_summary.md` content
- Domain context from this plan
- Instructions to:
  - Choose the method best supported by the data structure
  - State and justify the exact operational threshold ($68.26)
  - Calibrate baseline price dynamics from the full 19-year history
  - Justify calibration window (if down-weighting or excluding any period)
  - Run time-slice cross-validation / out-of-sample coverage check
  - Report P(WTI ≤ $68.26 by horizon) with credible intervals for all six horizons
  - Report posterior median time-to-threshold (conditional on reaching within 12mo) and P(not reaching $68.26 within 12mo)
  - Document convergence diagnostics and evidence quality

**What each forecaster must deliver:**
- `summary.md` with method selection reasoning, assumptions, convergence status, evidence quality, key findings
- `forecast.json` with P(event by horizon), median days to threshold, credible intervals, convergence status
- Out-of-sample validation results (time-slice cross-validation or coverage check)

**Synthesis (Step 5):**
After all forecasters complete, the orchestrator will:
- Evaluate technical quality (convergence status, evidence quality)
- Compare results across forecasters
- Note where methods CONVERGE (robust answer) and DIVERGE (uncertainty drivers)
- Write `model_comparison.md`, `report.md`, and `technical_report.md`

**Expected methods (forecasters choose freely):**
Given the data structure, plausible methods include:
- **JumpDiffusionModel** or **ContinuousDriverModel** (long daily series, threshold crossing, jump/volatility clustering)
- **MarkovStateModel** (identifiable regimes)
- **IndicatorModel** (OVX as leading indicator)
- Reference class / hazard models are NOT directly applicable (no discrete historical event durations), but forecasters may construct synthetic episodes from the WTI history

**Validation requirement:**
Each forecaster must run a time-slice cross-validation or out-of-sample coverage check to validate calibration.
