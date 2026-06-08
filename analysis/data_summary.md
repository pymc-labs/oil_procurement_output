# Data Summary

## Files inspected

- **data/raw/oil_futures.parquet**: 4,745 rows × 6 columns (2007-07-30 → 2026-06-05)
  - Primary series: WTI crude oil futures (open, close, volume)
  - Secondary: Brent crude futures (close, volume)
  
- **data/raw/ovx.parquet**: 4,919 rows × 2 columns (2007-07-30 → 2026-06-04)
  - CBOE Crude Oil Volatility Index (OVX)
  
- **data/raw/sp500.parquet**: 4,744 rows × 6 columns (2007-07-30 → 2026-06-05)
  - S&P 500 index level and returns (sprtrn, vwretd, ewretd)
  
- **data/raw/asian_indices.parquet**: 4,919 rows × 4 columns (2007-07-30 → 2026-06-04)
  - KOSPI (South Korea), Nikkei 225 (Japan), TOPIX (Japan)
  
- **data/raw/tanker_equities.parquet**: 46,480 rows × 8 columns (2007-07-30 → 2026-06-05)
  - Long-format panel: 12 energy-transport equity tickers (DHT, FRO, INSW, NAT, OSG, STNG, etc.)
  - Daily price, returns, volume, shares outstanding

---

## Historical analogues

**No historical event duration records are present.** 

The dataset contains continuous time-series of oil prices and related financial indicators, not discrete historical events with resolution dates. This is a price mean-reversion forecasting problem (when WTI will exceed $68.26), not a reference-class problem with past event durations.

To use hazard models or reference-class reasoning, external analogues would be required (e.g., historical episodes of oil price breakouts from low-volatility regimes, or duration of oil price rebounds following supply shocks).

---

## Continuous driver candidates

**Primary driver: WTI crude oil futures close price**
- **File**: `data/raw/oil_futures.parquet`
- **Column**: `wti_close`
- **Date range**: 2007-07-30 → 2026-06-05 (4,744 observations)
- **Current value** (2026-06-05): **$90.54**
- **Historical range**: $-37.63 (2020-04-20, COVID crash) to $145.29 (2008-07-03, pre-GFC peak)
- **Full-period statistics**:
  - Mean: $73.11
  - Std: $21.89
  - 25th percentile: $56.10
  - Median: $72.36
  - 75th percentile: $90.46

**Event definition**: The forecasting question operationalizes as "when will `wti_close` first sustain a value > $68.26 (2025 75th percentile threshold)?"

**Why this is a threshold-crossing problem**:
- The threshold ($68.26) is derived from the 2025 baseline distribution, representing the top quartile of prices during a calm year
- Current price ($90.54) is **already above** the threshold, so the event has occurred as of 2026-06-05
- However, if the question asks when it will *remain* above or *first exceed* from a lower state, the time series provides a long baseline for modeling the stochastic dynamics

**Secondary driver: Brent crude oil futures**
- **Column**: `brent_close`
- **Correlation with WTI**: r = +0.974 (nearly collinear)
- **Mean**: $78.30 (typically $4–5 premium over WTI)
- **Missing**: 53 observations (1.1%)

---

## Leading indicators

### 1. **CBOE Crude Oil Volatility Index (OVX)**
- **File**: `data/raw/ovx.parquet`
- **Column**: `ovx`
- **Date range**: 2007-07-30 → 2026-06-04 (4,919 observations)
- **Missing**: 174 (3.5%)
- **Statistics**: Mean = 39.15, Std = 17.70, Range = [14.50, 325.15]
- **Correlation with WTI**: r = –0.322 (moderate negative)
- **Causal link**: Higher oil volatility often precedes or accompanies large price moves (both up and down). Elevated OVX may signal impending regime change.

### 2. **S&P 500 index**
- **File**: `data/raw/sp500.parquet`
- **Column**: `spindx`
- **Date range**: 2007-07-30 → 2026-06-05 (4,744 observations, complete)
- **Correlation with WTI**: r = –0.126 (weak negative)
- **Returns columns**: `sprtrn`, `vwretd`, `ewretd` (7.5% missing for vw/ew)
- **Causal link**: Broad equity market sentiment; oil price shocks can affect equities (supply shock → inflation → rate risk), but correlation is weak

### 3. **Asian equity indices**
- **File**: `data/raw/asian_indices.parquet`
- **Columns**: `kospi` (KOSPI), `nikkei` (Nikkei 225), `topix` (TOPIX)
- **Date range**: 2007-07-30 → 2026-06-04 (4,919 observations)
- **Missing**: 1 observation each for Nikkei and TOPIX, 0 for KOSPI
- **Correlations with WTI**: KOSPI r = +0.011 (none), Nikkei r = –0.144, TOPIX r = –0.138 (both weak negative)
- **Causal link**: Asian economies are major oil importers; rising oil prices can pressure Asian equities, but the relationship is noisy

### 4. **Tanker equity basket**
- **File**: `data/raw/tanker_equities.parquet`
- **Columns**: `prc` (price), `ret` (returns), `vol` (volume)
- **Date range**: 2007-07-30 → 2026-06-05 (46,480 rows, 12 tickers)
- **Missing**: ~0.1% for price/returns
- **Causal link**: Tanker/shipping equity performance reflects oil transport demand, which correlates with oil price levels and volatility. Rising oil prices can indicate supply tightness, boosting tanker rates.

### Correlation summary

**High collinearity (|r| > 0.8):**
- WTI close × Brent close: r = +0.974 ✅ *expected; same commodity*
- S&P 500 × Nikkei: r = +0.976 ✅ *global equity co-movement*
- S&P 500 × TOPIX: r = +0.958 ✅
- KOSPI × Nikkei: r = +0.844 ✅
- KOSPI × TOPIX: r = +0.808 ✅
- Nikkei × TOPIX: r = +0.991 ✅ *both Japanese indices*

**Implication**: Brent can substitute for WTI; Asian indices are redundant with each other and with S&P. OVX is the only indicator with meaningfully independent information (r = –0.32 with WTI).

---

## Base rate information

**Not directly computable from this dataset.** 

The data contains continuous price levels, not labeled historical events of the form "WTI exceeded threshold X within time window Y." 

To derive a base rate, one would need to:
1. Define a reference class (e.g., "all instances where WTI was below $68.26 for at least 30 days")
2. Label each instance with time-to-threshold-crossing (or censoring)
3. Compute empirical survival curve

This could be constructed programmatically from the WTI time series (e.g., identify all episodes where price was < $68.26, then measure duration until crossing), but such episodes would be highly regime-dependent (2015–2017 low-price era vs. 2022 spike vs. 2025 calm).

**Broader reference class**: "Oil price breakouts from below 75th percentile of prior-year distribution" — would require historical regime analysis not present in the raw data.

---

## Quality issues

### Missing values
- **Minimal impact**: WTI close has only 1 missing value (0.02%); Brent has 53 (1.1%); OVX has 174 (3.5%)
- **S&P 500 return columns** (vwretd, ewretd) have 7.5% missing, but the index level (spindx) is complete
- **Tanker equities**: ~0.1% missing, negligible for panel analysis

### Duplicates
- **None detected** in any file

### Outliers
- **WTI close: $–37.63 on 2020-04-20** (COVID-19 May futures contract expiry anomaly)
  - This is the only value below $0; physically impossible but reflects futures contract settlement mechanics
  - **Not an outlier by 3×IQR rule** (lower bound = $–46.98), but contextually anomalous
  - Should be handled with care in models (log-transform will fail; consider winsorizing or using returns instead of levels)
- **No extreme high outliers** detected (max $145.29 in 2008 is within 3×IQR)

### Date gaps
- **No gaps > 5 days** in the WTI series (trading holidays are consistent; no data outages)

### Calendar misalignment
- **OVX and Asian indices extend to 2026-06-04** (one day shorter than WTI/S&P which go to 2026-06-05)
- **S&P 500 and WTI are perfectly aligned** (both 4,744 observations, 2007-07-30 → 2026-06-05)
- **Tanker equities**: long format complicates alignment, but date range matches WTI

### Type issues
- **Asian indices stored as Decimal**: KOSPI, Nikkei, TOPIX are stored as `object` dtype (Decimal type); must be cast to Float64 for numerical operations (already handled in `explore.py`)

---

## Data structure notes for forecasters

**Time-series length and granularity**:
- The WTI close series contains **4,744 daily observations** spanning **18.86 years** (2007-07-30 → 2026-06-05)
- This is a **long, dense, high-frequency baseline** suitable for fitting continuous stochastic process models
- Daily frequency enables modeling of short-term volatility dynamics, mean-reversion, and jump processes

**Regime heterogeneity**:
- The series exhibits **multiple distinct regimes** with different mean levels, volatilities, and autocorrelation structures:
  - **2007–2008**: High-volatility commodity boom → GFC crash (mean $99.75, std $28.42)
  - **2009–2013**: Post-GFC recovery, high plateau (mean $62–98, std $5–13)
  - **2014–2016**: Oversupply collapse (mean $43–49, std $6–7, lowest period)
  - **2017–2019**: Stabilization (mean $50–64, std $3–7)
  - **2020**: COVID shock (mean $39.34, includes negative price anomaly)
  - **2021–2022**: Post-COVID recovery + supply shock (mean $68–94, std $8–12)
  - **2023–2025**: Normalization (mean $64–78, std $5–6, low volatility)
  - **2026** (partial): Recent upswing (mean $83.44, std $17.41, only 107 obs)

**Stationarity properties**:
- **Levels are non-stationary**: Lag-1 autocorrelation = 0.995 (near-unit-root)
- **First differences are stationary-like**: Variance of first differences (4.34) is 0.9% of variance of levels (479.21)
- **Implication**: Models should work with returns or differenced series, or explicitly model non-stationarity (e.g., Ornstein-Uhlenbeck mean reversion, regime-switching)

**Threshold definition**:
- The 2025 75th percentile ($68.26) serves as a concrete, data-driven threshold
- **Current price ($90.54) is 32.7% above the threshold**, indicating the event has recently occurred
- The threshold lies between the 25th and median of the full-period distribution, representing a "moderately elevated" price

**Auxiliary series availability**:
- **One independent leading indicator** (OVX) with moderate negative correlation
- **Multiple collinear indicators** (Brent, Asian indices, S&P) that do not add independent information
- **Panel data** (tanker equities) offers potential sector-specific leading signals but requires aggregation or selection

**No labeled historical outcomes**:
- The dataset does not contain pre-labeled instances of past threshold-crossing events with durations
- Supervised learning (e.g., classification, survival regression) would require constructing labels from the WTI series itself or sourcing external event catalogs
- The time series can be used to **generate** synthetic labeled episodes (e.g., "time from below-threshold to above-threshold"), but this is an endogenous construction, not independent validation data

**Pre-event baseline for threshold models**:
- If the event is defined as "first crossing above $68.26 starting from a period when price was below," the 2025 baseline (mean $64.74) provides a clear pre-event window
- The 2026 partial year shows a rapid price increase (mean $83.44), suggesting a regime shift or transient shock

**Jump and volatility clustering**:
- The presence of the 2020 negative price event and the high-volatility 2008 regime suggests **jump diffusion** or **stochastic volatility** processes may be appropriate
- OVX time series (volatility index) can inform volatility forecasts

---

## What the data does not contain

1. **Historical event duration records**: No catalog of past "threshold-crossing episodes" with start dates, end dates, or censoring indicators. To use hazard models, such episodes must be synthetically constructed from the WTI series or sourced externally (e.g., oil market event databases).

2. **Exogenous shock indicators**: No direct measures of supply disruptions (OPEC cuts, geopolitical events), demand shocks (recession indicators, mobility data), or inventory levels. OVX captures volatility but not the *direction* or *cause* of shocks.

3. **Fundamental drivers**: No data on oil production, consumption, inventories, refining capacity, or geopolitical risk indices. These would enable causal mechanistic models (e.g., "price rises when inventory falls below X").

4. **Forward-looking information**: No futures curve data (contango/backwardation), analyst forecasts, or options-implied probability distributions beyond OVX (which is a 30-day volatility measure, not a directional forecast).

5. **Labeled regime transitions**: Annual statistics show regime changes, but there are no explicit labels (e.g., "2014-06-01: oversupply regime begins"). Regime detection would need to be inferred (e.g., via hidden Markov models or structural break tests).

6. **High-frequency intraday data**: Daily granularity limits modeling of intraday volatility or microstructure effects.

**What would unlock additional methods**:
- **OPEC production quotas, global inventory data**: Would enable supply-demand balance models with explicit thresholds (e.g., "price exceeds $68.26 when inventory < X million barrels")
- **Geopolitical risk index** (e.g., Caldara-Iacoviello GPR): Would enable event-driven scenario modeling (e.g., "Middle East conflict → supply shock → price spike")
- **Futures curve data**: Would enable extraction of market-implied forecasts and risk premia
- **Labeled historical analogues** from external sources (e.g., "Oil price breakout episodes 1980–2007"): Would enable true reference-class forecasting

---

## Issues for the orchestrator

### 1. **Collinearity among leading indicators**
- Brent is 97.4% correlated with WTI (redundant)
- Asian indices are 80–99% correlated with each other and with S&P 500 (use only one equity index or construct a principal component)
- **Recommendation**: Use WTI as primary driver, OVX as sole independent indicator, and either S&P or a composite equity index (not all three Asian indices)

### 2. **Non-stationarity of price levels**
- WTI close has lag-1 autocorrelation of 0.995 (near-unit-root)
- **Recommendation**: Models should use returns, log-differences, or explicitly model mean-reversion (Ornstein-Uhlenbeck) rather than assuming stationary levels

### 3. **Regime heterogeneity**
- Mean and volatility vary 3–5× across regimes (2008 std $28 vs. 2025 std $5)
- Forecasts based on recent data (2023–2025 calm) may underestimate tail risk from regime shifts
- **Recommendation**: Consider regime-switching models, or stratify analysis by regime, or use robust methods (quantile regression, non-parametric bootstrapping)

### 4. **Structural break in 2026**
- The partial 2026 data (107 obs) shows a sharp mean increase ($83.44) and volatility spike (std $17.41) relative to 2025 ($64.74, std $5.29)
- **Recommendation**: The 2026 upswing may indicate an ongoing regime transition; forecasters should check whether the event (crossing $68.26) has already occurred or if the question asks about *sustained* exceedance

### 5. **COVID-era negative price anomaly**
- 2020-04-20: WTI close = $–37.63 (May futures contract settlement anomaly)
- **Recommendation**: Winsorize or flag this observation in models using price levels; use returns-based models to avoid contamination

### 6. **Sparse OVX data**
- 174 missing values (3.5%) in OVX, mostly in early period (2007–2009) or recent days
- **Recommendation**: Interpolate or forward-fill for complete time series, or use only observations with complete data (reduces sample to ~4,686)

### 7. **Tanker equities require aggregation**
- 12 tickers in long format; no obvious "primary" ticker
- **Recommendation**: Construct an equal-weighted or value-weighted basket return series, or use principal component of returns

### 8. **No ground truth for model validation**
- There are no held-out labeled events to test forecast accuracy
- **Recommendation**: Use pseudo-out-of-sample backtesting (e.g., rolling-window forecasts on historical threshold crossings) or compare multiple methods on the current forecast and defer to ensemble/wisdom-of-models
