---
name: kite-52-week-breakout
description: Find stocks closing above their previous 252-session high with explicit reference windows. Use when building or running this specific Kite-compatible stock screener.
---

# 52-week high breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Daily OHLCV, dated stock universe, as-of timestamp, lookback N=252, optional percentage buffer b=0, and split/bonus adjustment policy. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

For each completed session t, calculate H=max(high[t-N:t]), excluding t. Mark breakout when close[t]>H*(1+b/100). Equality is not a breakout. Default N=252 approximates 52 trading weeks; offer an explicit prior-calendar-year window when requested, with its coverage reported. Do not silently mix the two. An intraday high crossing H is a provisional touch, not this close-confirmed signal. Preserve H and the timestamp at which the candidate became knowable.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `reference_high,reference_start,reference_end,close,distance_above_pct,breakout,lookback_mode,history_count`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

An offline baseline is provided in scripts/core_signals.py; run `python scripts/core_signals.py fixtures/core.csv --calendar fixtures/sessions.csv --as-of 2026-10-09T16:00:00+05:30 --lookback 3 --volume-lookback 3` for its synthetic fixture. The helper supports session windows and --buffer-pct; calendar-year windows require an extension. Production requires a verified session calendar and full lookback. Run checks with `python -m unittest discover -s scripts`.

## Check

A new extreme in today's high cannot change today's reference H. Close exactly equal to H produces false. A recent listing with fewer than N sessions is insufficient_history.

Example request: "Scan my NSE universe for close-confirmed 52-week breakouts using the prior 252 sessions; export candidates."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

