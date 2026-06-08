# Oil Procurement Forecast: When Will WTI Come Back Down?

A probabilistic, defensible answer to a procurement question: with WTI crude elevated at
**$90.54/bbl** (about 33% above a normal level), when will it fall back to **$68.26/bbl**? We use
[PyMC's decision-lab](https://github.com/pymc-labs/decision-lab) to run five independent Bayesian
forecasters in parallel over **19 years** of daily price history (2007 to 2026) and consolidate
them into a single calibrated forecast.

*Teemu Säilynoja · Camilo Saldarriaga · Imri Sofer*

## The headline result

![Headline forecast](analysis/figures/00_headline_card.png)

Probability WTI closes at or below $68.26, from $90.54 at the forecast origin (T0 = 2026-06-05):

| Horizon | P(normalize) | 94% CI |
|---|---|---|
| 1 month | 2.5% | [0%, 6%] |
| 3 months | 23.3% | [14%, 34%] |
| 6 months | 44.5% | [31%, 60%] |
| 12 months | 65.9% | [49%, 82%] |

Near-term normalization is very unlikely, it is close to a coin flip by six months, and more
likely than not within a year. Median time to normalize (if it happens) is about 88 trading days.

**Read the full write-up:** [`analysis/blogpost.md`](analysis/blogpost.md).

## What's inside

```
.
├── README.md                  this page
├── pixi.toml  pixi.lock        locked environment (PyMC, ArviZ, Polars, matplotlib, ...)
├── .env.example               template for the data API keys (no secrets committed)
├── data/raw/*.parquet         daily market data through 2026-06-05 (WTI, OVX, S&P 500, Asian indices, tankers)
├── data_loading/              loaders that fetch and prepare the raw data (`pixi run fetch`)
└── analysis/                  the forecast deliverables
    ├── blogpost.md            the narrative write-up
    ├── forecast_prompt.txt    the exact prompt given to the forecasters
    ├── figures/               00 headline card, 01-11 charts
    ├── forecasters/           the five forecasters' forecast.json + summary.md
    ├── report.md, technical_report.md, model_comparison.md, consolidated_summary.md
    ├── data_summary.md, analysis_plan.md, steps_documentation.md
    └── generate_plots.py, fix_plots.py, generate_headline_card.py, generate_idata_plots.py
```

## How it works

Five forecasters each independently pick a method from a library of ten Bayesian approaches,
inspect the data, and produce a forecast with credible intervals; a consolidator then scores them
and selects a headline. Here all five converged on a mean-reverting model (Ornstein-Uhlenbeck): two
used pure OU, three added Merton-style jumps. They were also asked to validate out-of-sample with
time-slice cross-validation. The full methodology is in [`analysis/blogpost.md`](analysis/blogpost.md).

## Reproduce

```bash
pixi install                 # build the locked environment

# (optional) refresh the market data to the latest trading day
pixi run fetch               # writes data/raw/*.parquet  (needs FRED + WRDS keys, see .env.example)

# regenerate the data-driven figures from data/ and analysis/forecasters/
pixi run python analysis/generate_plots.py          # figures 01-06
pixi run python analysis/fix_plots.py               # figure 05 (label) + 11 (forest plot)
pixi run python analysis/generate_headline_card.py  # figure 00 (headline card)
```

Figures 07-10 are posterior-level charts built from the forecasters' saved MCMC traces. The traces
(110MB each) are not shipped here, so those four are included as rendered PNGs in `analysis/figures/`;
`analysis/generate_idata_plots.py` regenerates figure 10 (the five-forecaster overlay) from the
forecast JSONs and skips 07-09 when the trace tree is absent.

## Links

- [decision-lab](https://github.com/pymc-labs/decision-lab) — the forecasting framework
- [event-forecaster decision pack](https://github.com/pymc-labs/decision-lab/pull/34) — the pack used here

---

*Built with [PyMC](https://www.pymc.io), [decision-lab](https://github.com/pymc-labs/decision-lab),
and [Claude](https://claude.ai).*
