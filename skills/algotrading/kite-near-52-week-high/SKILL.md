---
name: kite-near-52-week-high
description: Rank stocks within a chosen percentage below their prior 52-week high, excluding breakouts. Use when building or running this specific Kite-compatible stock screener.
---

# Near 52-week high

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Completed daily OHLCV, dated universe, as-of timestamp, N=252 sessions and distance threshold d=3 percent. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Calculate H=max(high[t-N:t]), strictly before the evaluated session. distance_pct=100*(H-close[t])/H. A candidate requires 0<=distance_pct<=d; prices above H have negative distance and are excluded as breakouts. Rank ascending by distance, using symbol as deterministic tie-breaker. N=252 is a trading-session approximation to 52 weeks; support a separate preceding-calendar-year mode if explicitly selected. Do not substitute the largest close for the largest high. Optional volume or trend filters must appear as separate booleans.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `reference_high,close,distance_pct,near_high,rank,history_count,lookback_mode`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

With H=100 and d=3, closes 97 and 100 qualify, 96 and 101 do not. Adding future candles leaves prior results unchanged.

Example request: "Find NSE stocks between 0% and 3% below their prior 252-session high, closest first."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

