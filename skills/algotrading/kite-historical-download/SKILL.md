---
name: kite-historical-download
description: Download resumable, validated Kite candles with explicit gaps and contract coverage.
---

# Historical Candle Downloader

Implement a resumable downloader for `GET /instruments/historical/{instrument_token}/{interval}` through `kite.historical_data()`. Use the existing authorized connection; otherwise build and test with cached responses. Do not substitute live orders for an entitlement check.

Accept exchange, dated contract identity, interval, from/to, and optional OI. Use timezone-aware Asia/Kolkata timestamps and retain source offsets. Supported native intervals are minute, 3minute, 5minute, 10minute, 15minute, 30minute, 60minute and day; construct weekly candles separately from completed daily sessions.

Choose configurable conservative request windows, initially seven calendar days for intraday and thirty for daily. This is a client batching choice, not a claimed API maximum. Respect the shared three-history-requests-per-second ceiling. On a documented range-size rejection, halve that window; on session/permission failures stop with a reason. Persist completed windows so a restart resumes them.

Deduplicate by contract identity, interval and timestamp; use overlapping boundaries without losing the final record. Validate OHLC ordering, nonnegative volume, ascending times and expected sessions. Separate incomplete current candles from closed candles. Record gaps rather than filling price or volume silently.

Deliver `candles.parquet`, `download_manifest.json` and `gaps.csv`, with `contract, timestamp, open, high, low, close, volume, oi, closed, source`. Manifest includes requested/actual coverage, snapshot hash and missing windows. Continuous data is only the documented daily NFO/MCX futures facility; it does not create an expired-options archive.

Example: “Download one year of five-minute NSE candles, resume safely and report missing sessions.”

Checks: overlapping downloads produce unique bars; interrupted windows resume; unavailable expired contracts fail explicitly.

Sources (verified 2026-10-13): [Kite historical candles](https://kite.trade/docs/connect/v3/historical/); [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/).

