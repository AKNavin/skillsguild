---
name: kite-opening-gap-scan
description: Measure session opening gaps versus prior close and prior range without using later-day information. Use when building or running this specific Kite-compatible stock screener.
---

# Opening gap scanner

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Previous completed daily OHLC, first completed regular-session intraday bar, exchange calendar, as-of timestamp and absolute gap threshold g=1 percent. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Use the first regular-session bar's open, not its close, as observed_open. gap_pct=100*(observed_open/previous_close-1). Classify gap_up when gap_pct>=g, gap_down when <=-g, otherwise small_gap. Separately classify full_up if observed_open>previous_high and full_down if observed_open<previous_low; these are different from a close-relative gap. Avoid pre-open indicative prices unless the user explicitly chooses that data mode. Flag splits/bonuses and unavailable prior closes before ranking. Optional gap-fill monitoring uses only subsequent completed bars observed so far, never the final day's low/high.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `previous_session,previous_close,previous_high,previous_low,observed_open,gap_pct,gap_class,range_gap_class`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

An opening price 102 versus prior close 100 is a 2% gap regardless of today's eventual close. A holiday changes the prior-session lookup. A gap below previous high is not a full gap-up.

Example request: "After the first five-minute bar, list stocks opening at least 1% away from the previous session's close."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

