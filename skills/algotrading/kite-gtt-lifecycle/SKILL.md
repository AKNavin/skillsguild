---
name: kite-gtt-lifecycle
description: Create and reconcile single or OCO GTT plans without confusing triggers with fills.
---

# GTT Trigger Lifecycle

Implement a manager for user-specified single or two-leg GTT triggers. Use an existing authorized connection for reads; creating, modifying or deleting a trigger requires the user's GTT execution scope. Otherwise produce the exact proposed payload and simulate the lifecycle.

Use `place_gtt/get_gtt/get_gtts/modify_gtt/delete_gtt` or the documented `/gtt/triggers` endpoints. Resolve instrument, current price, tick size and quantity, then validate supported product and trigger ordering. A single trigger has one trigger value/order; two-leg OCO has two corresponding values/orders. The array index maps each trigger to its order. Use LIMIT orders with explicit prices.

Persist local intent ID, normalized payload hash, broker trigger ID, status, timestamps and expiry. Reconcile existing owned triggers before creation to avoid duplicate protection. A timed-out creation is ambiguous; inspect matching triggers and keep the intent blocked until resolved rather than creating another.

A triggered GTT means its order was attempted, not that the position was filled or protected. Follow returned order IDs into order history and trades. Funds, holdings authorization, price gaps and execution limits can still prevent execution. Track rejected/unfilled child orders and notify locally for follow-up. Only modify/delete an active owned trigger; preserve unrelated GTTs.

Refresh ownership and required quantities after partial exits, corporate actions or manual position changes. Do not silently resurrect an expired/cancelled trigger; require it to remain within the user's current plan.

Deliver `gtt_manager.py` and `gtt_state.json` with `intent_id,trigger_id,type,condition,orders,status,expires_at,child_order_ids,reconciled_position,action_required`.

Example: “Prepare an OCO GTT exit for this owned CNC position, with my specified stop and target.”

Checks: trigger firing does not mark a fill; repeated creation intent is deduplicated; a changed holding quantity produces a reviewed adjustment rather than an oversized exit.

Sources (verified 2026-10-13): [Kite GTT API](https://kite.trade/docs/connect/v3/gtt/); [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Kite portfolio APIs](https://kite.trade/docs/connect/v3/portfolio/).

