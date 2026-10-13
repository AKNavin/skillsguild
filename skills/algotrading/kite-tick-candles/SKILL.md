---
name: kite-tick-candles
description: Convert sampled Kite ticks into session-aligned bars with honest volume and gap flags.
---

# Ticks to Intraday Candles

Implement an event-time bar aggregator from supplied Kite ticks. If live collection is requested, use only the existing authorized data connection. Producing candles does not authorize trading.

Inputs are dated contract identity, last price, last-trade/exchange timestamp when available, reception time and cumulative daily volume. Align bars to the configured exchange session open in Asia/Kolkata; use half-open intervals [start,end). Produce 1/5/15-minute bars or a requested interval. Do not assume that a UTC hour or midnight is a market boundary.

Kite tick messages are sampled quote updates, not a complete exchange trade tape. Label reconstructed OHLC as sampled and reconcile against historical bars after close when possible. Ignore heartbeat-only packets. Use trade timestamps for price changes where available; record uncertainty if only arrival time exists.

Calculate volume from increases in cumulative daily volume, never by summing cumulative values or last-traded quantity. The first mid-session observation has unknown prior volume; start a baseline and flag the first bar incomplete. Reset baseline on a new session. A same-session decrease, missing interval or disconnect marks affected bars incomplete; do not assign an entire reconnect jump confidently to the latest minute.

Use a configurable event-time watermark. Late ticks before finalization update their bar; later arrivals create a correction record, not a silent rewrite of an emitted signal.

Deliver `bar_builder.py`, `bars.parquet` and `bar_corrections.jsonl`; rows include `contract,start,end,open,high,low,close,volume,complete,quality_reason,source`.

Example: “Aggregate these ticks into five-minute bars for relative-volume screening.”

Checks: daily cumulative reset never creates negative volume; a boundary tick enters the next bar; a disconnect produces incomplete bars rather than fabricated continuity.

Sources (verified 2026-10-13): [Kite WebSocket protocol](https://kite.trade/docs/connect/v3/websocket/); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/).

