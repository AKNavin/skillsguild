---
name: kite-liquidity-spread-filter
description: Reject stale or thin stock candidates using prior traded value and current bid–ask depth. Use when building or running this specific Kite-compatible stock screener.
---

# Liquidity and spread filter

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Prior completed daily OHLCV, current full Kite quotes with depth/timestamps, as-of time, N=20, minimum mean daily traded-value proxy=INR 10 million, max spread=20 bps and max quote age=5 seconds. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Compute prior traded-value proxy=mean(close*volume) over N completed sessions; label it a proxy because candle close is not trade-by-trade turnover. Extract highest valid positive bid and lowest valid positive ask with positive quantity. mid=(bid+ask)/2; spread_bps=10000*(ask-bid)/mid. Fail missing, stale, crossed (ask<bid) or nonpositive depth; locked markets may have zero spread. Require all configured filters. Report displayed best-level quantities independently; they do not guarantee executable size or fills. Use exchange quote and last-trade timestamps separately; an old last trade can coexist with updated depth.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `traded_value_proxy,bid,ask,spread_bps,bid_quantity,ask_quantity,quote_age_seconds,last_trade_age_seconds,eligible,rejection_reasons`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

Bid=100/ask=100.10 gives about 9.995 bps. A missing quote is rejected, not zero spread. Future quote timestamps outside allowed clock skew are invalid.

Example request: "Filter this stock watchlist to at least INR 1 crore prior daily traded value and at most 20 bps live spread."

Sources: [Kite Connect quotes and instruments](https://kite.trade/docs/connect/v3/market-quotes/); [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

