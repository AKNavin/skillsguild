---
name: kite-intraday-relative-volume
description: Compare intraday cumulative or bucket volume with the same elapsed session time across prior days. Use when building or running this specific Kite-compatible stock screener.
---

# Intraday same-time relative volume

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed intraday OHLCV, session calendar, as-of timestamp, N=20 prior comparable sessions, threshold r=2, and mode cumulative or bucket. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Align bars to the exchange session opening in Asia/Kolkata. For completed bucket k, cumulative mode compares sum(volume[session start:k]) with the mean of that same cumulative interval in N prior sessions. Bucket mode compares only bucket k with bucket k across prior sessions. Exclude today's observations from the baseline. Compare identical elapsed session durations; exclude shortened or missing-data sessions unless their matched interval is complete. Historical candles carry bar volume; live quote volume is cumulative for the day and must be differenced with reconnect/reset handling before bar aggregation.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `bucket_start,bucket_end,mode,observed_volume,baseline_volume,rvol,eligible_sessions,volume_breakout`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

At 10:00 only prior sessions' volume through 10:00 enters cumulative baselines. Removing a historical bucket invalidates that session rather than treating it as zero. Full-day volume never appears in a morning denominator.

Example request: "At each completed five-minute bar, alert when NSE stocks trade twice their usual cumulative volume at that same time."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Kite Connect quotes and instruments](https://kite.trade/docs/connect/v3/market-quotes/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

