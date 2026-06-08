# WTI Oil Price Normalization Forecast — Procurement Planning Read

**Prepared for:** Procurement decision: lock in oil supply now vs wait for normalization  
**Forecast as of:** 2026-06-06  
**Current state:** WTI crude oil = **$90.54/bbl** (elevated 32.6% above normalization threshold)  
**Normalization threshold:** **$68.26/bbl** (2025 75th percentile — a "normal high" baseline)

---

## Executive Summary

We forecast **a 44% probability that oil prices will normalize to ≤$68.26 by 6 months (Dec 2026)** and **a 66% probability by 12 months (Jun 2027)**, based on Ornstein-Uhlenbeck mean-reversion calibrated on 19 years of daily WTI data.

**However, an alternative jump-diffusion approach assigns 34% probability at 6 months and 49% at 12 months** — a coin flip at the 1-year horizon. The 10–17pp divergence reflects genuine uncertainty about whether current elevation is a transient spike (favoring mean-reversion) or a structural regime shift (favoring jump-diffusion).

**Key findings for procurement planning:**

1. ✅ **Short-term normalization is very unlikely:** P < 5% within 1 month. **Waiting 1–4 weeks for price clarity has negligible downside** — prices are not expected to normalize that quickly.

2. ⚠️ **Medium-term (3–6 months) is genuinely uncertain:** Probability ranges from 23–44% depending on forecasting method. **This is the critical planning window.**

3. 📊 **12-month outlook is moderately optimistic but not guaranteed:** 49–66% probability range. **Roughly even odds to 2-in-3 chance** of normalization.

4. 🎯 **If normalization occurs, it happens around 4 months from now (early October 2026)** — median timing across all forecasters.

5. 🔴 **Critical assumption: 2026 price elevation is transient, not structural.** If the current high-price regime persists (sustained OPEC cuts, geopolitical risk), probabilities drop by ~20–30pp.

---

## What the Forecast Means for the Lock-In Decision

### Scenario 1: Lock in oil supply NOW at $90.54

**Pros:**
- Eliminates price risk if current elevation persists or worsens
- Secures supply certainty in a tight market
- Avoids exposure to tail risk (geopolitical shocks, supply disruptions)

**Cons:**
- Pay **32.6% premium** over normalization level ($68.26)
- Forfeit **44% chance (6mo) to 66% chance (12mo)** of buying at lower prices if you wait
- If prices normalize to $68.26 within 6 months (44% probability), you overpay by **$22.28/bbl**

**Best if:**
- Your business cannot tolerate oil price volatility (e.g., thin margins, no hedging capacity)
- You believe 2026 elevation is structural (OPEC discipline, geopolitical risk persistent)
- Opportunity cost of waiting > $22/bbl × 44% = ~$10/bbl expected overpayment

### Scenario 2: WAIT for normalization (do not lock in now)

**Pros:**
- **44% chance (6mo) to 66% chance (12mo)** of buying at ≤$68.26 — a **$22.28/bbl savings** if normalization occurs
- Preserve optionality: can lock in later if prices fail to fall
- If normalization occurs, median timing is ~4 months (early October 2026) — manageable delay

**Cons:**
- **34% chance (12mo) to 51% chance (6mo)** that prices stay elevated or rise further
- Exposure to tail risk: geopolitical shocks, OPEC cuts, demand surges could push WTI to $100+
- If prices don't normalize, you're forced to lock in at high levels later (or face spot market volatility)

**Best if:**
- Your business can tolerate 6–12 months of price uncertainty
- You have hedging tools (futures, options) to manage interim volatility
- You believe 2026 elevation is transient (speculative spike, temporary supply disruption)
- Your procurement timeline allows waiting 3–6 months for price signals

### Scenario 3: HYBRID — Partial lock-in now, partial wait

**Strategy:** Lock in 40–60% of 12-month oil needs now at $90.54; leave 40–60% flexible to buy at spot if/when prices normalize.

**Rationale:**
- Hedge against tail risk (prices stay high or rise) by securing partial supply
- Preserve upside optionality (prices normalize) by keeping flexibility
- **Matches the 44–66% probability range** — lock in at the inverse of normalization probability

**Example allocation:**
- Lock in **40%** now (inverse of 6-month 60% "stay high" probability)
- Leave **60%** flexible to buy at spot over next 6 months
- If prices normalize to $68.26 within 6 months (44% chance), 60% exposure captures the $22/bbl savings
- If prices stay high (56% chance), 40% locked-in supply cushions the impact

**Best if:**
- Your procurement can be staged over 6–12 months
- You want to balance risk mitigation (lock-in) with cost optimization (wait for normalization)
- You have internal flexibility to adjust procurement timing based on price signals

---

## Decision Tree: Lock-In vs Wait

```
Current WTI: $90.54
Normalization threshold: $68.26
Premium: +$22.28/bbl (32.6%)

┌─────────────────────────────────────────┐
│ DECISION: Lock in now vs wait?          │
└─────────────────────────────────────────┘
         │
         ├─ [Lock in NOW] → Pay $90.54/bbl
         │   → Outcome A: Prices normalize to $68.26 within 6mo (44% probability)
         │      → You overpaid $22.28/bbl
         │   → Outcome B: Prices stay ≥$90 (56% probability)
         │      → Lock-in avoided further risk
         │
         └─ [WAIT 6 months] → No commitment now
             → Outcome C: Prices normalize to $68.26 (44% probability)
                → You saved $22.28/bbl
             → Outcome D: Prices stay ≥$90 (56% probability)
                → You lock in later at $90+ (or higher if tail risk materializes)

Expected value of WAIT (6-month horizon):
  = 0.44 × (+$22.28 savings) + 0.56 × ($0 or negative if prices rise)
  = +$9.80/bbl upside IF prices stay flat or fall
  = Risk: tail scenarios (WTI → $100+) not captured in point estimate

Break-even: If your cost of waiting (inventory, volatility, operational risk) < $9.80/bbl,
            WAITING is financially rational.
```

---

## Probabilities by Planning Horizon

| Horizon | Date | P(WTI ≤ $68.26) | 94% Credible Interval | Procurement Implication |
|---------|------|----------------:|----------------------:|-------------------------|
| **1 week** | 2026-06-12 | **0.0%** | [0.0%, 0.0%] | Near-zero chance. Locking in now vs next week is equivalent. |
| **1 month** | 2026-07-06 | **2%** | [0%, 6%] | Very unlikely. **Safe to defer decision by 2–4 weeks** to gather more price signals. |
| **3 months** | 2026-09-07 | **23%** | [14%, 34%] | **Critical window begins.** Roughly 1-in-4 to 1-in-3 chance of normalization. Monitor OPEC, geopolitics, demand. |
| **6 months** | 2026-12-07 | **44%** | [31%, 60%] | **Decision-critical horizon.** Moderately likely normalization. Hybrid strategy (partial lock-in) hedges both outcomes. |
| **12 months** | 2027-06-07 | **66%** | [49%, 82%] | **Long-term moderately optimistic.** 2-in-3 chance of normalization, but wide interval [49%, 82%] reflects uncertainty. |

**Conditional on normalization occurring within 12 months:**
- **Median timing:** 88 trading days (~4 months, early October 2026)
- **10th–90th percentile:** 30–202 trading days (~6 weeks to 9 months)

**Interpretation:** If normalization happens, it's most likely to occur around **Q4 2026**. Procurement plans targeting Q4 2026–Q1 2027 delivery have the highest chance of benefiting from lower prices.

---

## Alternative Forecast Range: Jump-Diffusion (Tail-Risk Adjusted)

Three forecasters using jump-diffusion (which explicitly models fat-tailed shocks and regime changes) assign **lower probabilities:**

| Horizon | OU (Mean-Reversion) | JD (Jump-Diffusion) | Gap |
|---------|---------------------|---------------------|-----|
| 6 months | **44%** [31%, 60%] | **34–35%** [24%, 47%] | −10pp |
| 12 months | **66%** [49%, 82%] | **49–50%** [34%, 66%] | −16pp |

**Why jump-diffusion assigns lower probabilities:**
- JD models capture fat-tailed shock structure (2008 spike, 2020 crash, 2022 supply shock)
- Jump volatility *disperses* price paths both upward and downward, reducing net crossing probability
- JD forecasters argue that if normalization requires a discrete shock (geopolitical resolution, demand collapse), the coin-flip odds (50% at 12mo) are more realistic than mean-reversion's 66%

**When to use JD range instead of OU:**
- If you believe current elevation is structural (sustained OPEC cuts, geopolitical risk persistent)
- If tail-risk accounting is critical (JD has wider credible intervals)
- If your procurement planning is conservative and prefers lower-probability scenarios

**Decision implication:**
- Under JD forecast, **waiting is riskier** — only 34% chance at 6mo, 50% at 12mo
- Under OU forecast, **waiting is more attractive** — 44% chance at 6mo, 66% at 12mo
- **Hedge by using hybrid strategy:** Lock in 50–60% now (matching JD probabilities), leave 40–50% flexible (capturing OU upside)

---

## What Could Change This Forecast

### Factors that would INCREASE normalization probability (favor waiting):

1. **OPEC+ announces production increases** (supply relief)
2. **Geopolitical de-escalation** (Middle East conflicts resolve, sanctions lifted)
3. **Demand weakness signals** (recession indicators, refinery utilization drops, mobility data declines)
4. **Inventory builds** (global crude stocks rise, indicating oversupply)
5. **Forward curve flips to contango** (distant futures > near-term, signaling oversupply expectations)

### Factors that would DECREASE normalization probability (favor locking in now):

1. **OPEC+ maintains or deepens production cuts** (supply tightness persists)
2. **Geopolitical escalation** (new conflicts, expanded sanctions, pipeline disruptions)
3. **Demand surge** (economic growth accelerates, mobility rebounds, refinery runs increase)
4. **Inventory draws** (stocks decline, indicating tight supply/demand balance)
5. **2026 regime persists >3 months** (if prices stay $80–90 through Q3 2026, structural shift becomes more credible)

**Monitoring schedule:**
- **Weekly:** WTI spot price, OVX volatility index, OPEC+ news
- **Monthly:** EIA inventory data, forward curve shape, refinery utilization
- **Quarterly:** Reassess forecast if 2026 price level persists (update regime stationarity assumption)

---

## What We Cannot Say

### 1. **Whether 2026 is a transient spike or structural shift**

The forecast assumes the 2026 price elevation ($83–90 range) is **transient** and will revert to the 2007–2025 historical equilibrium (~$70).

**If 2026 represents a structural shift** (e.g., sustained OPEC discipline, energy transition slowing investment, geopolitical risk premium):
- Historical calibration is invalid
- Probabilities are overstated by ~20–30pp
- New equilibrium may be $75–85, not $70

**What would resolve this:** Wait 2–3 months. If prices stay $80–90 through Q3 2026, structural shift becomes more credible.

### 2. **Exact threshold sensitivity**

The $68.26 threshold is the 2025 75th percentile. If your "normalization" definition differs:
- $70 (long-run mean): P(12mo) ≈ 50% (lower)
- $65 (2025 median): P(12mo) ≈ 40–50% (lower)
- ±10% threshold shift: probabilities change by ~15–20pp

**What would resolve this:** Define your business's break-even price — the level at which locking in now vs waiting is cost-neutral.

### 3. **Tail risk scenarios**

The forecast provides probabilities for $68.26 crossing, not tail scenarios:
- **Upside tail:** What's P(WTI > $100 within 6 months)? Not reported.
- **Downside tail:** What's P(WTI < $60 within 6 months)? Not reported.

Jump-diffusion forecasters note fat-tailed structure but don't quantify extreme tails. For full risk assessment, request:
- P(WTI > $100 | 6mo) — tail risk of locking in too late
- P(WTI < $60 | 6mo) — upside of waiting

---

## Recommended Procurement Strategy

### BASE CASE: Hybrid Lock-In (40–60% now, 40–60% flexible)

**Rationale:**
- Hedge tail risk (prices stay high) by securing 40–60% of 12-month needs at $90.54
- Preserve upside (prices normalize) by leaving 40–60% flexible for spot purchases
- Matches the 44–66% normalization probability range
- Reduces regret in both scenarios (prices normalize or stay high)

**Implementation:**
1. Lock in **50%** of 12-month oil needs now at current prices (~$90)
2. Stage remaining **50%** over 6 months (monthly spot buys or forward contracts)
3. Adjust allocation if new information emerges (see monitoring schedule above)

**Expected outcome:**
- If prices normalize to $68.26 within 6 months (44% chance):
  - 50% locked in at $90 → overpay $22/bbl on half the volume
  - 50% spot buy at $68 → save $22/bbl on half the volume
  - Net: ±$0 (hedged position)
- If prices stay ≥$90 (56% chance):
  - 50% locked in at $90 → avoided further upside risk
  - 50% spot buy at $90+ → neutral to negative
  - Net: Tail risk partially mitigated

### ALTERNATIVE 1: Full Lock-In Now (100% at $90.54)

**Choose if:**
- Your business cannot tolerate 6–12 months of price volatility
- You believe 2026 elevation is structural (OPEC discipline, geopolitical risk persistent)
- Opportunity cost of $22/bbl overpayment (if prices normalize) < cost of operational disruption

**Trade-off:** Eliminate price risk, but forfeit 44–66% chance of $22/bbl savings.

### ALTERNATIVE 2: Full Wait (0% lock-in, 100% spot over 6–12 months)

**Choose if:**
- Your business can tolerate price volatility (hedging tools available, flexible operations)
- You believe 2026 elevation is transient (speculative spike, temporary supply shock)
- You have high confidence in mean-reversion (OU forecast: 66% normalization by 12mo)

**Trade-off:** Capture $22/bbl savings if normalization occurs (44–66% probability), but expose to tail risk if prices stay high or rise.

### ALTERNATIVE 3: Staged Lock-In (tiered approach)

**Strategy:**
- **Month 1–2 (Jun–Jul 2026):** Wait — normalization probability < 5%, no urgency
- **Month 3 (Sep 2026):** Lock in **30%** if prices still ≥$85 — hedge against structural shift
- **Month 4–6 (Oct–Dec 2026):** Lock in remaining **70%** at spot — capture normalization if it occurs (median timing ~Oct 2026)

**Rationale:** Defer maximum commitment to the 3–6 month window when normalization probability peaks (23–44%).

---

## One-Page Summary for Executive Decision

| Question | Answer |
|----------|--------|
| **Will oil prices normalize to ≤$68.26 within 6 months?** | **44% probability** [31%, 60%]. Moderately likely but not guaranteed. |
| **Will oil prices normalize within 12 months?** | **66% probability** [49%, 82%]. 2-in-3 chance, but wide uncertainty. |
| **If normalization occurs, when?** | **Median: 4 months (~early October 2026)**. Range: 6 weeks to 9 months. |
| **Should we lock in oil supply now at $90.54?** | **Hybrid strategy recommended:** Lock in 40–60% now, leave 40–60% flexible. Hedges both outcomes. |
| **What's the cost of locking in now if prices normalize?** | **$22.28/bbl overpayment** (32.6% premium over threshold). |
| **What's the risk of waiting if prices stay high?** | **34–56% probability** (depending on method) that prices stay ≥$90 for 6–12 months. Tail risk: prices could rise further. |
| **Critical assumption?** | **2026 elevation is transient, not structural.** If prices stay $80–90 through Q3 2026, forecast may overstate normalization by ~20–30pp. |
| **When should we reassess?** | **Monthly** (track WTI, OPEC news, inventories). **Quarterly** if prices stay elevated (update regime assumption). |

---

## Appendix: Technical Notes

- **Primary forecast:** Ornstein-Uhlenbeck mean-reversion (Instance 1), 19-year calibration, convergence OK, prior sensitivity PASS
- **Alternative forecast:** Jump-diffusion (Instances 2, 3), 19-year calibration, convergence OK, prior sensitivity WARN (10–12pp on jump parameters)
- **Methodological divergence:** OU assigns 66% at 12mo; JD assigns 49–50%. Both are technically sound. See **model_comparison.md** for full analysis.
- **Cross-validation:** OU shows 99–100% coverage at 12–24mo horizons; JD validates against historical base rates (0.82× ratio, within tolerance).
- **Data:** 4,744 daily WTI observations (2007–2026), excluding COVID negative price anomaly (2020-04-20).

**For full technical details, see:**
- `model_comparison.md` — detailed method comparison, convergence diagnostics, cross-validation results
- `technical_report.md` — complete audit trail, all forecasters, all rounds
- Individual forecaster summaries in `parallel/run-*/instance-*/summary.md`
