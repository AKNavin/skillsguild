---
name: kite-health-monitor
description: Detect stale feeds, ambiguous orders and risk failures with deduplicated incident reports.
---

# Algo Health & Alert Monitor

Implement an operations monitor around an existing Kite strategy. Read its local telemetry and authorized account snapshots; monitoring must not create trades. Default notifications to a local dashboard/log. External messages require the user's chosen channel and authorization.

Monitor feed connection, last packet and per-instrument freshness separately; heartbeat traffic does not imply current prices. Track event-loop/queue lag, reconnect count, quote failures, token expiry, limiter saturation, order acknowledgement latency, unresolved submission age, pending order age, rejected orders, position discrepancies, margin reserve and risk-gate state.

Use thresholds tied to the exchange calendar and strategy cadence. Expected overnight silence is different from an intraday outage; an illiquid instrument is different from a dead connection. Keep measurements and evidence in each incident. Never include access tokens, credentials or full authenticated URLs in alerts.

Create stable incident keys such as `feed:connection` or `order:<intent>:unknown`. Deduplicate repeated observations, escalate only after configured duration/severity and emit a recovery event when healthy again. Alert delivery failure must be visible locally. Reporting success requires acknowledgement from the configured sink, not merely queueing a message.

Deliver `health_monitor.py`, `health_policy.json`, `incidents.jsonl` and `health.json`. Incident schema: `id,key,opened_at,updated_at,severity,state,metric,value,threshold,evidence,affected_intents,runbook_action,delivery_status`. Supply a compact terminal status command. Automatic halt requests may set an already-authorized local risk gate; cancellation/flattening remains governed by the existing execution policy.

Example: “Alert on stale data and unresolved orders during market hours without sending repeated messages.”

Checks: one outage creates one incident plus updates; market closure suppresses expected inactivity; a simulated notification failure stays visible until retried or acknowledged.

Sources (verified 2026-10-13): [Kite WebSocket protocol](https://kite.trade/docs/connect/v3/websocket/); [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/); [Kite orders](https://kite.trade/docs/connect/v3/orders/).

