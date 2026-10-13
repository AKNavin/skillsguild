---
name: kite-atr-range-expansion
description: Find unusually large true ranges against a prior Wilder ATR baseline and retain price direction. Use when building or running this specific Kite-compatible stock screener.
---

# ATR range expansion

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, interval, N=14, expansion threshold r=1.5, as-of timestamp, and previous close before the first evaluated bar. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

True range TR[t]=max(high-low,abs(high-previous_close),abs(low-previous_close)). Seed ATR with the mean of the first N valid true ranges; thereafter ATR[t]=((N-1)*ATR[t-1]+TR[t])/N. Compare expansion=TR[t]/ATR[t-1], excluding the evaluated bar from its denominator. Flag expansion>=r with a positive prior ATR. Report close location (close-low)/(high-low), or null for a zero-range bar, and direction by close versus previous close. Expansion is a volatility condition, not automatically a directional entry. A gap may drive TR even when high-low is small.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `true_range,prior_atr,expansion_ratio,close_location,direction,range_expansion`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A gap from previous close 100 to high 112/low 110 has TR=12, not 2. Current TR cannot inflate its own denominator. Zero prior ATR produces unavailable.

Example request: "Scan for daily true range at least 1.5 times prior 14-day Wilder ATR and include close location."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays); [Zerodha Varsity: ATR and VWAP](https://zerodha.com/varsity/chapter/supplementary-notes-1/). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

