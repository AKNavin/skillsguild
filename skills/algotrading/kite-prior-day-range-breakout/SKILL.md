---
name: kite-prior-day-range-breakout
description: Detect intraday crossings of the previous completed trading session's high and low. Use when building or running this specific Kite-compatible stock screener.
---

# Prior-day high and low breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Daily plus intraday OHLCV, exchange calendar, as-of timestamp, evaluation interval=5 minutes and buffer b=0. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Resolve the previous actual trading session, not yesterday's calendar date. Freeze PDH and PDL from its completed daily candle. For each closed intraday bar, bullish crossing is previous_close<=PDH*(1+b/100) and close>that level; bearish crossing is previous_close>=PDL*(1-b/100) and close<that level. On the first bar compare with previous-session close and label a first-bar gap event separately. Preserve sustained_above/sustained_below as states distinct from a new crossing. Deduplicate by symbol, session, direction and crossing time.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `previous_session,pdh,pdl,close,direction,event_type,trigger_level,event_id`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A Monday uses Friday or the previous eligible holiday-adjusted session. Repeated closes above PDH create one crossing until price resets below. Today's high cannot replace PDH.

Example request: "Alert me when a closed five-minute bar first crosses the previous trading day's high or low."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

