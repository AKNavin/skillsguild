---
name: option-hedge-roll-monitor
description: "Detect hedge deterioration and prepare a costed roll plan from reconciled positions."
---

# Monitor option hedges and rolls

## Inputs

Require reconciled positions by contract, pending orders, fresh quote/Greek snapshots, available funds, user-set delta/exposure limits and expiry/roll policy. Signed quantities are underlying units. Record current position version and quote timestamps so a plan cannot be reused against changed holdings.

## Monitor

Aggregate `position_delta=sum(q_i*delta_i)`; include stock delta and properly specified futures exposure. Aggregate other Greeks only after agreeing units. Report missing/stale Greeks as incomplete exposure instead of zero. Trigger a review on expiry proximity, a limit breach, missing protective leg or hedge quantity mismatch.

For a requested roll, construct explicit close-old/open-new legs with verified expiry, lot sizes and settlement type. Estimate each leg at its executable side of fresh depth and disclose uncovered size. Calculate fees and remaining exposure before, during and after the sequence. Request current `kite.basket_order_margins()` with the relevant existing-position policy; distinguish `initial` from `final` margin. A beneficial final basket can still require more cash during execution.

Prepare a leg sequence that preserves protection where feasible. Include what to do after a rejected or partially filled leg: reconcile first, recompute remaining size, then re-plan. Never assume all legs execute atomically or automatically double a failed order. Do not quietly liquidate a hedge to free margin.

## Deliver and check

Write `hedge-alerts.json` and a proposed `roll-plan.json` containing position version, triggers, legs, worst intermediate exposure/margin, estimated debit/credit and expiry obligations. Verify a partial-fill scenario and a protective-leg expiry mismatch. Example: “Monitor my covered stock-option positions and propose rolls within these limits.” The output is a proposed plan; execution needs separate explicit authorization.

## Sources

[Kite margin and virtual contract-note APIs](https://kite.trade/docs/connect/v3/margins/); [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [NSE individual-security derivatives specifications](https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities). Accessed 2026-10-13.
