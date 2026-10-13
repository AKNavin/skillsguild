---
name: trend-regime
description: "Label completed bars as uptrend, downtrend or range using a reproducible moving-average rule."
---

# Classify the trend regime

## Inputs

Accept instrument, timeframe, completed bars, adjustment policy and configuration. A transparent demonstration uses fast SMA 50, slow SMA 200, slow slope lag 20 and minimum separation 1%; all are configurable research choices. Require enough warm-up bars for the longest moving average and slope lag.

## Compute

For bar t, calculate `fast=mean(close[t-49:t+1])`, `slow=mean(close[t-199:t+1])`, `slope=slow_t/slow_(t-20)-1`, and `separation=fast/slow-1`. Label `uptrend` when close exceeds slow, separation exceeds the positive threshold and slope is positive. Label `downtrend` for the symmetric negative conditions. Otherwise label `range`; missing warm-up or invalid data is `unknown`, not range.

Emit the label only after the input bar closes; an intraday user of daily regime uses the last completed session. Weekly bars require an exchange-calendar-aware completed week. Avoid using a partial current candle or full-week aggregate midweek. Preserve the bar's timezone and `available_at` timestamp.

If reducing rapid switches, require a configurable number of consecutive completed candidate labels before changing state; record candidate and confirmed labels separately. This label describes a price rule, not proof of a structural economic regime. Never tune its thresholds against the evaluation period whose strategy performance it is meant to explain.

## Deliver and check

Write `trend-regime.csv`: bar end, available_at, close, fast, slow, slope, separation, candidate, confirmed and configuration hash. Test rising, falling and flat synthetic paths plus warm-up. Example: “Label NIFTY's daily regime with 50/200 SMAs and two-bar confirmation, using completed sessions only.” Produce analytics; changing a live strategy requires separate authorization.

## Sources

[Zerodha moving averages](https://zerodha.com/varsity/chapter/moving-averages/); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/). Accessed 2026-10-13.
