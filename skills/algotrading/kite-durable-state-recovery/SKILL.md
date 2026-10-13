---
name: kite-durable-state-recovery
description: Persist order intents and rebuild state after crashes before allowing new execution.
---

# Durable State & Restart Recovery

Implement a durable journal and restart procedure for a Kite strategy. Use local fixtures until the existing account connection is authorized. Recovery observes broker truth; resuming execution inherits the user's strategy scope and otherwise remains disabled.

Use SQLite on local persistent storage with foreign keys, WAL and an explicit durability setting such as synchronous=FULL. Do not place a live SQLite WAL database on an unsupported network filesystem or copy only its main file as a backup. Use the backup API or a safe checkpoint/closed-database backup.

Create tables `intents(intent_id UNIQUE,fingerprint,state)`, `order_links(intent_id,order_id UNIQUE)`, `events(event_key UNIQUE,payload,received_at)`, `fills(account,exchange,trade_id,quantity,price)`, `reservations(intent_id,amount)` and `checkpoints`. Choose a stable composite unique key for fills. Commit intent and reservation before network submission; commit broker acknowledgement promptly. Keep database transactions short, not open across network calls.

On startup acquire a single-writer lease/lock, disable new sends, replay events and reconcile every submitting/unknown/open intent against the daily orderbook, histories, trades and positions. A crash after sending but before saving the ID is ambiguous; tags aid discovery but do not guarantee idempotency. Persist unresolved intents instead of re-enqueueing them. Journal historical orders locally because daily broker views are not a permanent archive.

Return `recovery_report.json` with `run_id,last_checkpoint,recovered_orders,unknown_intents,position_deltas,reservations,execution_ready,blockers`. Deliver `journal.py`, schema migration and crash-injection tests.

Example: “Make my strategy restart safely after a crash during order submission.”

Checks: a crash after broker acceptance cannot cause resend; two processes cannot own execution simultaneously; replaying events twice yields the same positions and reservations.

Sources (verified 2026-10-13): [SQLite write-ahead logging](https://www.sqlite.org/wal.html); [SQLite transactions](https://www.sqlite.org/lang_transaction.html); [Kite orders](https://kite.trade/docs/connect/v3/orders/).

