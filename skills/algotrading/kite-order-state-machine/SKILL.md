---
name: kite-order-state-machine
description: Reduce order updates into durable state without losing fills or trusting event order.
---

# Order Event State Machine

Implement a pure reducer plus a durable event consumer for Kite order state. It observes the existing authorized account connection and does not place orders. Use WebSocket order updates for an individual account, including orders entered through other Kite interfaces; mark strategy ownership separately.

Retain raw broker status and map it to local states `pending, open, trigger_pending, partially_filled, complete, cancelled, rejected, unknown`. Partial fill is derived from cumulative filled quantity plus remaining status. UPDATE is an event notification, not proof of a fill; compare quantities and reconcile trades.

Persist each raw event before updating its projection. Deduplicate using order ID, broker timestamps, status, cumulative quantities and payload hash, because timestamps alone may collide. Events can arrive late, duplicated or after a REST snapshot. Do not regress terminal state or reduce confirmed filled quantity based solely on arrival order. When evidence conflicts, mark reconciliation_required and fetch order history/trades. A cancelled order may still contain real fills.

If an HTTP webhook is requested, verify its documented SHA-256 checksum of order_id + order_timestamp + api_secret before accepting it, check account/app ownership, acknowledge quickly after durable storage and process asynchronously. Preserve secrets outside logs.

Deliver `order_reducer.py`, `order_events.sqlite` and projections containing `order_id,intent_id,raw_status,state,quantity,filled,pending,cancelled,average_price,updated_at,reconciliation_required`. Keep strategy-owned and external orders visible separately.

Start with the bundled [offline SQLite reference](scripts/broker_state.py). It models intent submission, ambiguous acknowledgement, cumulative-fill reduction and restart blocking without a network client. Run `python -B -X utf8 -m unittest discover -s scripts -v` from this skill folder. Adapt it to the required schemas; a live adapter still needs unique-trade reconciliation, ownership checks and process-level execution control.

Example: “Build an order-state reducer that survives duplicate and out-of-order Kite updates.”

Checks: duplicate UPDATE does not double-count fills; a late OPEN cannot erase COMPLETE; cancellation after a partial fill retains executed quantity and triggers position reconciliation.

Sources (verified 2026-10-13): [Kite order postbacks](https://kite.trade/docs/connect/v3/postbacks/); [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Kite WebSocket protocol](https://kite.trade/docs/connect/v3/websocket/).

