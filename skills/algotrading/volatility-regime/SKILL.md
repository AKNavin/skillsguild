---
name: volatility-regime
description: "Compare realized volatility and India VIX with trailing history using only completed observations."
---

# Classify volatility regimes

## Inputs

Accept instrument, completed adjusted daily closes, optional India VIX history, calendar and percentile window. Demonstration defaults are 20 return observations for realized volatility and 252 earlier valid observations for regime thresholds. Confirm the history is sufficiently long; do not fabricate a full percentile window.

## Compute

Calculate log returns `r_t=ln(C_t/C_(t-1))`; realized annual volatility is `sample_std(r_(t-19):r_t)*sqrt(252)`. Keep it as a decimal and expose the annualization convention. Determine percentile thresholds from strictly earlier volatility values, excluding the current observation. Label low at or below the prior 25th percentile, high at or above the prior 75th percentile, otherwise normal; missing coverage yields unknown.

India VIX is an option-implied annualized percentage for roughly the next 30 calendar days, not realized volatility or direction. If present, convert `VIX/100` and compute its own trailing percentile. Report disagreement between realized and implied regimes instead of combining incomparable levels blindly. Use a timestamp-aligned, completed VIX observation; never insert today's final VIX into an earlier intraday decision.

For intraday realized volatility, define return sampling, overnight treatment and annualization separately. Session gaps and missing bars cannot be treated as genuine zero returns. Option IV percentile or rank requires its own consistent tenor/moneyness archive; do not substitute VIX for a stock option's IV.

## Deliver and check

Save `volatility-regime.csv` with realized value, prior thresholds, optional VIX, both labels and coverage. Test constant-price history, insufficient history and future-data invariance. Example: “Flag high-volatility NIFTY sessions using trailing RV20 quartiles and compare with India VIX.” This classifies data and does not prescribe trades.

## Sources

[NSE India VIX methodology overview](https://www.nseindia.com/static/products-services/indices-indiavix-index); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/). Accessed 2026-10-13.
