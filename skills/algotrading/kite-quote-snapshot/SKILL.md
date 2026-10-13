---
name: kite-quote-snapshot
description: Fetch timestamped stock and option snapshots while detecting missing or stale quotes.
---

# Batched Quote Snapshots

Build a quote service for a supplied resolved universe. Use the user's existing authorized data connection, with offline fixtures when unavailable. This skill reads market data and produces no orders.

Choose `quote()` for depth, volume and OI; `ohlc()` for session OHLC; `ltp()` only when last price is sufficient. Deduplicate exchange:tradingsymbol keys and chunk at 500 for full quotes or 1000 for OHLC/LTP. Route all workers through one shared quote limiter capped at one request per second. Prefer streaming for continuous monitoring.

Persist request start/end times and each exchange quote/last-trade timestamp when provided. Do not label a multi-batch universe atomic: record its collection span and reject cross-symbol comparisons exceeding configured skew. If a requested key is absent, output a missing row rather than dropping it. A present zero OI/volume can be valid; distinguish it from an absent field.

Normalize `symbol, instrument_token, fetched_at, exchange_timestamp, last_trade_time, ltp, volume, oi, bid, ask, status`. Keep unsupported fields null and status one of `ok, missing, stale, invalid`. Validate finite positive prices and non-crossed usable depth; report illiquidity separately from transport failure. The OHLC close is the previous trading session's close, not today's final close.

Deliver `quotes.py`, `snapshot.parquet` and `snapshot_manifest.json` with requested/returned counts, collection span, stale/missing symbols and source mode.

Example: “Snapshot all NFO options in this expiry, preserving missing contracts and quote times.”

Checks: 501 full-quote keys make two limited requests; an absent symbol remains in the output; stale batches cannot pass a freshness-sensitive scanner.

Sources (verified 2026-10-13): [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/).

