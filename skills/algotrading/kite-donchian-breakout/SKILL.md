---
name: kite-donchian-breakout
description: Detect configurable rolling high or low breaks without including the signal bar in the channel. Use when building or running this specific Kite-compatible stock screener.
---

# Donchian channel breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, selected interval, N=20 preceding bars, buffer b=0, as-of timestamp, and state versus event output mode. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Upper[t]=max(high[t-N:t]); lower[t]=min(low[t-N:t]); midpoint=(upper+lower)/2. A bullish state is close[t]>upper[t]*(1+b/100); bearish is close[t]<lower[t]*(1-b/100). The current bar must be excluded or a close can never exceed a channel that includes its own high. For fresh events, require the corresponding prior-bar breakout state to be false. If the rolling boundary itself changes, report that fact instead of claiming a same-level crossing. Default closes confirm breaks; high/low touch mode is an explicitly different rule.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `channel_upper,channel_lower,channel_mid,close,breakout_state,new_event,reference_bars`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

With prior maximum 100 and current high 110/close 105, bullish must be true. Equality at a channel boundary is false. A missing required reference bar makes the result unavailable.

Example request: "Build a 20-day Donchian breakout screener with prior-bar channels and export fresh events."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

