---
name: kite-trend-pullback
description: Find a defined pullback to a moving average followed by a completed-bar recovery in an existing trend. Use when building or running this specific Kite-compatible stock screener.
---

# Trend pullback and recovery

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, interval, fast EMA f=20, slow EMA s=50, tolerance p=1 percent, as-of timestamp and at least s warm-up bars. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Use EMA alpha=2/(n+1), first n-close mean seed. Establish bullish trend using fastEMA[t-1]>slowEMA[t-1] and slowEMA[t-1]>slowEMA[t-6]. Define a pullback touch on t-1 when low[t-1]<=fastEMA[t-2]*(1+p/100) and close[t-1]>=slowEMA[t-2]; freeze those reference averages before the pullback bar. Confirm on t only if close[t]>high[t-1] and close[t]>fastEMA[t-1]. These are transparent example rules, not a uniquely correct pullback definition. Report trend, touch and recovery separately; provide a mirrored bearish rule only if requested.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `prior_fast_ema,prior_slow_ema,trend_pass,pullback_touch,recovery_level,close,confirmed`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A recovery without a prior touch is false. A touch formed after t cannot qualify t. The output's recovery_level must equal the pullback bar's high, not the current high.

Example request: "Find daily bullish EMA pullbacks recovering above the previous bar's high and show each condition."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Zerodha Varsity: moving averages](https://zerodha.com/varsity/chapter/moving-averages/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

