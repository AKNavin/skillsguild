---
name: kite-partial-fill-management
description: Manage remaining order quantity through fill races and confirmed cancellation.
---

# Partial Fills, Modify & Cancel

Implement a controller for an existing order with a fixed intended total quantity. Default to dry-run commands unless modifications/cancellations are within the user's authorized connection and scope.

Read order history and order trades before each decision. Compute confirmed filled quantity from unique trades and reconcile it with the broker's cumulative quantity. Remaining target = max(0, intended_total - confirmed_fills). Do not infer a fill from an order acknowledgement, price touch or UPDATE status alone.

For repricing, modify only an open order using its original variety and ID. Kite quantity modification is the desired total order quantity, not the extra quantity still wanted. Require modified total >= already-filled quantity, valid lot/tick sizes and the configured price/slippage bound. Count modifications; the documented ceiling is 25 per order. Do not churn orders merely to evade a limit.

For cancel/replace, request cancellation and keep the old order active in local risk accounting until a terminal state is confirmed. Re-read trades after cancellation because fills can race the request. A replacement covers only reconciled residual target and gets its own linked intent ID. Timeout on modify/cancel is ambiguous: reconcile rather than repeating blindly.

Bound repricing attempts and total elapsed time. At deadline, follow the user's specified leave/cancel/reduce policy; no automatic market escalation unless previously authorized. Partial execution must update position and hedge exposure immediately.

Deliver `remaining_order_controller.py` and `execution_progress.json` with `parent_intent, order_ids, intended, filled, remaining, last_action, modification_count, deadline, residual_action`.

Example: “Cancel and replace this partially filled limit order without exceeding my 100-share target.”

Checks: a late fill reduces replacement quantity; cancel acknowledgement alone cannot unlock replacement; all linked fills combined stay within the intended total.

Sources (verified 2026-10-13): [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/).

