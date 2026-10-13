---
name: kite-opening-range-breakout
description: Freeze a session's opening range and detect later closed-bar breaks above or below it. Use when building or running this specific Kite-compatible stock screener.
---

# Opening range breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Intraday OHLCV, session calendar, range length R=15 minutes, evaluation interval=5 minutes, buffer b=0 and as-of timestamp. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Use the first R minutes of the regular session, with all included bars completed. Freeze ORH=max(high) and ORL=min(low) for that interval. Begin evaluation only after the range ends. A bullish event requires previous close<=ORH*(1+b/100) and current close>that level; bearish reverses against ORL*(1-b/100). Require two post-range evaluation closes, or explicitly use the final opening-range close as the previous comparison. Store one event per direction/session unless re-entry is requested. Missing opening bars invalidate the range rather than shrinking it.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `session,range_start,range_end,or_high,or_low,trigger_level,close,direction,event_id`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

A high inside the opening range cannot be a breakout of that same range. Later highs never expand the frozen range. Duplicate candle delivery cannot produce duplicate event_id values.

Example request: "Build five-minute close-confirmed alerts for breaks of the first 15-minute range on my NSE stocks."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

