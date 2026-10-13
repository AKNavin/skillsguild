---
name: kite-daily-volume-breakout
description: Compare completed daily traded volume with a prior-session baseline and optional price confirmation. Use when building or running this specific Kite-compatible stock screener.
---

# Daily volume breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Daily OHLCV, as-of timestamp, baseline N=20 completed sessions, ratio threshold r=2, and optional price-direction condition. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

For completed day t, baseline=mean(volume[t-N:t]) and rvol=volume[t]/baseline. Flag rvol>=r with a positive baseline and full N-session coverage. Keep volume expansion separate from close[t]>close[t-1] or a requested price breakout. Report both predicates if combined. This uses traded volume, not delivery quantity, institutional activity or buy-volume minus sell-volume. A partly elapsed day's cumulative volume must never be divided by a full-day baseline for this signal; route such requests to same-time intraday relative volume.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `volume,baseline_volume,rvol,volume_breakout,price_condition,baseline_sessions`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

With prior volumes 100,200,300, current 400 has rvol=2 and passes threshold 2. Including 400 in the baseline must fail the leakage check. Zero baseline yields unavailable, not infinity.

Example request: "Find stocks with at least twice their previous 20-session average volume after today's close."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Zerodha Varsity: volumes](https://zerodha.com/varsity/chapter/volumes/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

