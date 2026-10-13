---
name: kite-bollinger-squeeze-breakout
description: Identify a defined volatility squeeze followed by a close beyond a frozen prior Bollinger band. Use when building or running this specific Kite-compatible stock screener.
---

# Bollinger squeeze breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, interval, band period N=20, deviation multiplier k=2, bandwidth history M=120, quantile q=0.20 and as-of timestamp. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

At each completed bar calculate mid=mean(last N closes), population standard deviation sigma (ddof=0), upper=mid+k*sigma and lower=mid-k*sigma. Bandwidth=(upper-lower)/mid requires mid>0. Declare squeeze[t-1] when bandwidth[t-1] is at or below the q quantile of M bandwidth observations ending at t-2; specify quantile interpolation=linear. Then bullish breakout at t requires squeeze[t-1] and close[t]>upper[t-1]; bearish uses lower[t-1]. Freeze the prior bands to avoid widening them with the breakout bar. Report the exact squeeze definition instead of implying a universal standard.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `prior_upper,prior_lower,prior_bandwidth,bandwidth_cutoff,squeeze,close,breakout,ddof`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A future outlier cannot change an earlier squeeze cutoff. The breakout bar is absent from its threshold band. Insufficient N+M warm-up returns insufficient_history.

Example request: "Find daily closes leaving a prior 20-period Bollinger squeeze, using the lowest 20% of historical bandwidths."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Zerodha Varsity: indicators part 2](https://zerodha.com/varsity/chapter/indicators-part-2/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

