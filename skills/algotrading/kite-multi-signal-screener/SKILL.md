---
name: kite-multi-signal-screener
description: Combine transparent stock-signal predicates, filters and rankings into one reproducible screener. Use when building or running this specific Kite-compatible stock screener.
---

# Compose a stock screener

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Dated universe, OHLCV or supplied feature tables, as-of timestamp, session calendar and a JSON config naming each formula, lookback, threshold, Boolean expression and ranking rule. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

Implement each feature locally in the delivered project or consume versioned inputs; do not assume sibling skill ZIPs are installed. A sample rule is close>max(prior 252 highs) AND daily_volume/mean(prior 20 volumes)>=2. Require one shared signal timestamp and closed-bar convention. Join by exchange, symbol and timestamp; distinguish false from unavailable. For AND, a false predicate means false; otherwise any missing predicate makes the result unavailable. For OR, true wins; otherwise missing means unavailable. Emit only candidates whose overall predicate is true, plus an exclusions file. Rank deterministically; never turn a ranking into portfolio sizing or order placement.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `symbol,as_of,rule_version,feature_values,predicate_results,overall_result,rank,data_quality,exclusion_reason`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

The same data/config must yield identical sorted results. Changing future rows cannot change past candidates. An unavailable feature is never silently converted to false or a neutral score.

Example request: "Build one screener for 52-week close breakouts plus 2x daily volume, with complete feature evidence for every stock."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

