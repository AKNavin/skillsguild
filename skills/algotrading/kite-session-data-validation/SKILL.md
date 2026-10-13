---
name: kite-session-data-validation
description: Validate market sessions, missing candles and price quality before running a scanner.
---

# Session Calendar & Data Checks

Implement a pre-signal validator for NSE cash/equity-derivative candles, configurable for other segments. Accept a local dataset or use the user's existing authorized data connection. No trading actions belong to this validator.

Build a versioned session table from the exchange's published trading calendar and applicable special-session circulars. Store `exchange, segment, session_date, open, close, breaks, session_type, source_url, checked_at`. Trading holidays and settlement holidays are distinct. Do not reduce the calendar to weekdays or assume all segments share hours. Missing special-session times remain unknown and block affected intraday scheduling.

Validate timezone-aware bar boundaries against that table. Deduplicate contract + interval + timestamp. Check finite positive OHLC, low <= open/close <= high, high >= low, nonnegative volume, and the intended closed-bar cutoff. Distinguish a confirmed zero-trade interval from missing ingestion; never invent a traded candle merely to satisfy frequency.

Produce a quality gate with explicit hard/soft rules: hard failures for impossible prices, duplicate conflicting bars or unknown identity; configurable warnings for low liquidity or incomplete lookback. Flag price discontinuities for corporate-action review rather than applying guessed split ratios. Preserve raw data and write corrections separately.

Deliver `sessions.csv`, `validate_data.py`, `quality_report.json` and `rejected_rows.csv`. Report `run_id, expected_sessions, observed_sessions, missing_intervals, duplicates, invalid_rows, incomplete_last_bar, eligibility_by_symbol`. A symbol cannot receive a valid 252-session signal with insufficient eligible history.

Example: “Check these daily and five-minute files before the 52-week and volume scans.”

Checks: a published holiday is not counted as missing; a special session uses its own close; a partial latest candle fails a closed-bar-only gate.

Sources (verified 2026-10-13): [NSE trading holidays](https://www.nseindia.com/resources/exchange-communication-holidays); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/); [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/).

