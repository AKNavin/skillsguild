---
name: kite-order-margin-check
description: Compare current broker margin estimates with usable funds before accepting an order intent.
---

# Pre-trade Margin Check

Implement `check_margin(order, reserves)` as a read-only preflight for a proposed order. Use the existing authorized account connection; otherwise use recorded fixtures. A successful result is eligibility evidence, not permission to place an order.

Resolve exchange, tradingsymbol, product, side, quantity, order type, price and trigger price. Reject missing lot/tick validation or stale required prices before calling `kite.order_margins([order])`, equivalent to JSON `POST /margins/orders`. Retain the detailed response, not just total. Obtain current `kite.margins()` for the appropriate equity/commodity segment, together with open orders and positions needed to interpret existing commitments.

Return broker-calculated incremental requirements without hardcoding leverage multipliers. Distinguish cash, collateral, option premium and already-utilized margin. Do not add collateral twice, treat short-option premium as freely spendable cash, or subtract the same pending-order reservation twice. When usable-funds composition or concurrent reservations cannot be reconciled, return unknown and block the intent.

Apply a user-configured reserve and estimate validity period. Store the funds and positions snapshot hashes used. Any quantity, price, product, open-order or position change invalidates the check; recompute immediately before an authorized submission. An estimate can change before broker acceptance.

Deliver `margin_check.py` and `margin_decision.json` with `intent_id, as_of, order_hash, required_total, components, funds_snapshot, local_reservations, reserve, available_for_intent, decision, reasons[], expires_at`.

Example: “Check whether this 100-share CNC buy fits my cash after a ₹20,000 reserve.”

Checks: two simultaneous intents cannot spend one local reservation; stale estimates become ineligible; insufficient cash is not concealed by an unrelated collateral balance.

Sources (verified 2026-10-13): [Kite margin calculations](https://kite.trade/docs/connect/v3/margins/); [Kite login and user APIs](https://kite.trade/docs/connect/v3/user/).

