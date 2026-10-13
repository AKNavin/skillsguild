---
name: kite-websocket-feed
description: Build a reconnecting market-data feed with subscriptions, freshness and gap tracking.
---

# Reliable Kite WebSocket Feed

Implement a `KiteTicker` service for the existing authorized connection. In the absence of that connection, replay recorded tick fixtures. Keep feed collection separate from strategy evaluation and order submission.

Maintain a desired subscription map of token to mode. Respect at most 3000 instruments per connection and three connections per API key, including other processes. Use full mode when timestamps, OI or depth are needed; LTP mode is insufficient for those fields. On each connection, reconcile desired subscriptions and modes idempotently. Let one reconnect policy own backoff; do not nest an unbounded retry loop around SDK reconnects.

In tick callbacks, enqueue compact events and return immediately. A bounded queue that overflows must record a gap and pause dependent signals rather than silently discarding evidence. Store both reception time and exchange/last-trade timestamps when available. Distinguish connection heartbeat, fresh quote and actual trade activity. A heartbeat does not prove every subscribed instrument is fresh.

Record disconnect intervals and subscription generations. After reconnect, obtain a fresh snapshot or historical backfill appropriate to the consumer; keep affected bars incomplete until reconciled. On session expiry, stop retries and expose login_required. Process order-update callbacks through a separate durable queue.

Deliver `feed.py`, `subscription_state.json`, append-only `ticks.jsonl` and `feed_health.json` with `connected, last_message_at, last_quote_at, reconnect_count, queue_depth, stale_tokens, gaps[]`. Redact WebSocket URLs containing tokens.

Example: “Stream these 500 option contracts with reconnects and an explicit stale-data gate.”

Checks: reconnect restores modes once; overflow emits a gap; expired authentication stops the reconnect loop.

Sources (verified 2026-10-13): [Kite WebSocket protocol](https://kite.trade/docs/connect/v3/websocket/); [Official Python SDK](https://github.com/zerodha/pykiteconnect); [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/).

