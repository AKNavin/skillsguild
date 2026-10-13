---
name: kite-order-submit-reconcile
description: Submit authorized order intents while resolving timeouts without duplicate placement.
---

# Order Submission & Reconciliation

Implement an order gateway whose default mode is dry-run. Real placement requires the user's existing authorized connection and strategy/account scope. Generate a normalized order preview otherwise.

Assign each strategy decision a stable `intent_id`; atomically store its fingerprint and state before transmission. Lock that identity across workers. Derive an alphanumeric tag of at most 20 characters for correlation; Kite tags are not server-enforced idempotency keys. Reject a reused intent ID with different parameters.

Validate dated contract metadata, lot/tick sizes, product permissions, fresh margin/risk gates and configured static egress. For MARKET/SL-M use supported nonzero market_protection, including -1 auto where appropriate; do not silently convert order semantics. Verify SDK support. Submit once via `place_order()` or `POST /orders/{variety}`.

Persist the returned order ID before further work. Acknowledgement means accepted for processing, not filled. On timeout, network ambiguity or uncertain server failure, set `SUBMIT_UNKNOWN`, retain the reservation and reconcile the daily orderbook/trades using tag, account, symbol, side, quantity and submission window. Match exactly one order; multiple matches require investigation. Repeated absence is not proof of non-acceptance: keep risk blocked and require a resolved outcome before resubmission.

For requested autoslicing, process every returned slice/error independently; never treat an array with partial failures as total success. Keep child orders linked to one intent.

Deliver `order_gateway.py`, `order_intents.sqlite` and `submission_result.json` with `intent_id, mode, fingerprint, state, order_ids[], errors[], reconciliation_evidence`.

Example: “Add duplicate-safe placement to my already-authorized strategy.”

Checks: duplicate callers transmit once; a timeout after broker acceptance finds the original; a mixed slice response preserves successful IDs and failed quantities.

Sources (verified 2026-10-13): [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Zerodha API execution rules, effective April 2026](https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types); [Zerodha static IP requirements](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip).

