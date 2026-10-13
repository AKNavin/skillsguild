---
name: kite-weekly-volume-breakout
description: Find completed weeks with unusually large traded volume using comparable prior weeks. Use when building or running this specific Kite-compatible stock screener.
---

# Weekly volume breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Daily OHLCV, exchange trading calendar, as-of timestamp, N=10 prior weeks, threshold r=1.5 and week definition Monday–Sunday in Asia/Kolkata. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Aggregate first open, maximum high, minimum low, last close and summed volume for each calendar week. Mark a week complete only after its last scheduled exchange session has completed; holiday-shortened weeks remain explicit. Baseline is mean(volume) of the N preceding completed weeks, excluding the evaluated week. Weekly rvol=current_week_volume/baseline. A current Tuesday must not be compared against full prior weeks. If session-count normalization is requested, compute volume per actual trading session for every week and label that separate measure; never switch silently.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `week_start,week_end,session_count,weekly_volume,baseline_volume,weekly_rvol,breakout,week_complete`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A partly completed week returns pending_week. A holiday-shortened completed week keeps its actual session_count. Current-week volume changes cannot alter its historical baseline.

Example request: "Screen the last completed NSE week for 1.5 times its previous ten completed weeks' average volume."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Zerodha Varsity: volumes](https://zerodha.com/varsity/chapter/volumes/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

