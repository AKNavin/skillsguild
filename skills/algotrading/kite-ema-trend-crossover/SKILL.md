---
name: kite-ema-trend-crossover
description: Separate moving-average trend state from fresh crossovers on completed stock candles. Use when building or running this specific Kite-compatible stock screener.
---

# EMA trend and crossover

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, bar interval, as-of timestamp, fast period f=20, slow period s=50, and explicit EMA warm-up history. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Calculate EMA using alpha=2/(n+1), seed with the first n-close simple average, then recurse EMA[t]=alpha*close[t]+(1-alpha)*EMA[t-1]. Record this convention so library defaults cannot silently change results. Bullish trend state is fastEMA>slowEMA; fresh bullish event additionally requires fastEMA[t-1]<=slowEMA[t-1]. Reverse inequalities for bearish. Optionally require price above slowEMA as a separate named filter. Use at least s observations for initialization and disclose finite-history seed sensitivity. Indicators may include the currently evaluated completed close; they cannot include its future bars.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `close,fast_ema,slow_ema,trend_state,crossover,seed_method,warmup_count`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A constant-price series produces no crossover. A persistent fast-above-slow state is not a new event every bar. Truncating future data leaves earlier computed events unchanged.

Example request: "Screen my stocks for fresh 20/50 daily EMA crosses and separately show the current trend state."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Zerodha Varsity: moving averages](https://zerodha.com/varsity/chapter/moving-averages/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

