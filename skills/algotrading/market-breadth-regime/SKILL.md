---
name: market-breadth-regime
description: "Classify broad participation using point-in-time constituents, advances and moving-average breadth."
---

# Measure market breadth

## Inputs

Require a named universe with membership effective dates, completed adjusted closes, calendar and coverage threshold. For a historical NIFTY universe, current constituents are insufficient: use membership known at each timestamp, including later deletions. If unavailable, label the result a fixed-current-universe analysis and do not present it as historical index breadth.

## Compute

For every session count advances `C_t>C_previous`, declines `C_t<C_previous` and unchanged stocks. Use comparable prices across corporate actions. Calculate `advance_share=A/(A+D)` when the denominator is positive, `net_breadth=(A-D)/(A+D)`, and cumulative advance-decline line from an explicitly arbitrary starting value.

Calculate each eligible stock's 50-session SMA from completed data, then `above_sma_share=count(C_t>SMA50_t)/valid_sma_count`. Report denominators separately: newly listed stocks may have a valid daily change but insufficient SMA history. Missing or suspended names remain in expected membership and reduce coverage, rather than silently improving breadth.

A demonstration classifier is broad strength when both advance share and above-SMA share exceed 0.6, broad weakness when both are below 0.4, otherwise mixed. Gate the label on a configurable coverage floor such as 0.95 and emit unknown when it fails. Thresholds are testable research choices. Daily results become available after session close; intraday breadth needs fresh synchronized snapshots and a separate label.

## Deliver and check

Write `breadth.csv` with as-of, universe version, expected/valid counts, A/D/U, both shares, coverage and label. Check all-unchanged sessions, membership changes and missing losers. Example: “Measure daily participation for my dated F&O universe and reject days below 95% coverage.” Return analytics only.

## Sources

[NSE advances and declines](https://www.nseindia.com/market-data/advance); [Zerodha moving averages](https://zerodha.com/varsity/chapter/moving-averages/). Accessed 2026-10-13.
