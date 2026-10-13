---
name: kite-52-week-breakdown
description: Identify stocks closing below a previous 252-session low with an optional buffer. Use when building or running this specific Kite-compatible stock screener.
---

# 52-week low breakdown

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Completed daily OHLCV, dated universe, as-of timestamp, N=252 and downside buffer b=0 percent. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Set L=min(low[t-N:t]), excluding the evaluation session. Mark breakdown if close[t]<L*(1-b/100). An equal close is only a touch. If a near-low watchlist is requested, report 100*(close[t]-L)/L separately and restrict it to a nonnegative configured band. Do not label stocks already below L as near-low. N=252 approximates 52 trading weeks; record whether the user instead chose the prior calendar year. This identifies a price condition; it does not imply that an equity can be sold short overnight.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `reference_low,reference_start,reference_end,close,distance_below_pct,breakdown,history_count`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

Today's low cannot lower today's reference L. With L=100, closes 100 and 101 are false and 99 is true at zero buffer.

Example request: "Export close-confirmed 52-week low breakdowns for this stock list; use a 0.2% buffer."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

