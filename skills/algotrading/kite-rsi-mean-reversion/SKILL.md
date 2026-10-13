---
name: kite-rsi-mean-reversion
description: Detect RSI exits from specified extremes with explicit Wilder smoothing and optional regime filters. Use when building or running this specific Kite-compatible stock screener.
---

# RSI recovery and rejection

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, interval, N=14, lower=30, upper=70, as-of timestamp and optional user-defined trend/regime filter. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Change=close[t]-close[t-1]; gain=max(change,0), loss=max(-change,0). Seed average gain/loss with means of the first N changes, then Wilder-smooth each with alpha=1/N. RSI=100-100/(1+avg_gain/avg_loss). When both averages are zero use 50; loss-only-zero gives 100 and gain-only-zero gives 0. Recovery event: RSI[t-1]<lower and RSI[t]>=lower. Rejection: RSI[t-1]>upper and RSI[t]<=upper. Merely remaining oversold is not an event. Keep any regime filter explicit; extreme RSI can persist in trends and does not establish reversal probability.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `rsi,previous_rsi,event,lower_threshold,upper_threshold,regime_pass,seed_method`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

Flat closes give RSI 50 and no event. A monotonic rising series eventually gives 100 without repeated recovery alerts. Future prices cannot alter earlier RSI values.

Example request: "Create daily RSI-14 recovery alerts crossing back above 30 for my stock universe; retain all exclusions."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Zerodha Varsity: indicators part 1](https://zerodha.com/varsity/chapter/indicators-part-1/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

