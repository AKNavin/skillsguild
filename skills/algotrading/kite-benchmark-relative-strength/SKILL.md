---
name: kite-benchmark-relative-strength
description: Rank stock performance relative to a chosen benchmark over identical completed sessions. Use when building or running this specific Kite-compatible stock screener.
---

# Benchmark relative strength

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Stock and benchmark daily closes, dated universe, benchmark identifier, as-of timestamp and lookback N=63 common trading intervals. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Select the required N+1 completed session dates from the exchange calendar, ending at t. Join stock and benchmark closes on exactly those dates and require complete coverage; do not drop missing dates to obtain a different window. Compute stock_factor=stock_close[t]/stock_close[t-N], benchmark_factor=benchmark_close[t]/benchmark_close[t-N], and relative_return=stock_factor/benchmark_factor-1. Rank descending, breaking ties by symbol. Separately report stock_return and benchmark_return. Do not call this RSI or mix a price index with a total-return stock series without disclosure. Never forward-fill missing benchmark observations. A current universe ranking is descriptive, not a survivorship-free historical universe.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `benchmark,window_start,window_end,stock_return,benchmark_return,relative_return,rank,common_intervals`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

Identical proportional paths give relative_return=0. Stock +10% versus benchmark +5% gives about 4.7619%, not 5%. A mismatched date fails alignment instead of silently shortening the horizon.

Example request: "Rank my NSE stock list by 63-session relative performance against NIFTY 50, using common completed dates."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

