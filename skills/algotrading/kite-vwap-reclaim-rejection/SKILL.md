---
name: kite-vwap-reclaim-rejection
description: Detect close-confirmed crossings of session VWAP with an explicit exact-versus-proxy method. Use when building or running this specific Kite-compatible stock screener.
---

# VWAP reclaim and rejection

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed intraday OHLCV or captured exchange VWAP snapshots, session calendar, as-of timestamp, evaluation interval=5 minutes and minimum elapsed bars=3. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

For candles, define typical_price=(high+low+close)/3 and proxy_vwap=sum(typical_price*volume)/sum(volume), resetting at each session. Label this candle approximation; it is not exact trade-level VWAP. If using Kite average_price snapshots, retain their observation times and never backfill an earlier bar with a later snapshot. Reclaim: previous close<=previous VWAP and current close>current VWAP. Rejection: previous close>=previous VWAP and current close<current VWAP. Zero cumulative volume is unavailable. Require a completed bar and compare like-for-like VWAP methods throughout.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `session,cumulative_volume,vwap,vwap_method,previous_close,close,event,distance_bps`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

Session two starts a new accumulator. A later high-volume bar cannot change an earlier VWAP result. Constant-priced positive-volume candles produce that same proxy VWAP.

Example request: "Create five-minute VWAP reclaim and rejection alerts from my Kite candle CSV, marking VWAP as a candle proxy."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [Kite Connect quotes and instruments](https://kite.trade/docs/connect/v3/market-quotes/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays); [Zerodha Varsity: ATR and VWAP](https://zerodha.com/varsity/chapter/supplementary-notes-1/). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

