---
name: kite-basket-margin-plan
description: Plan multi-leg entry and exit using peak margin and confirmed hedge fills.
---

# Basket Margins & Hedge Sequencing

Implement a planner for a specified multi-leg spread, returning a dry-run plan unless that strategy's execution is already authorized. Use the user's existing connection for margin reads. Do not translate a margin quote into a live basket order.

Normalize each leg to exchange, symbol, side, quantity, product, type and price; verify matching intended expiry/underlying and lot ratios. Call `kite.basket_order_margins(legs, consider_positions=True)` when existing positions should count. Save the returned initial and final totals and per-order components. The final hedged margin alone is not the cash needed to enter.

Evaluate permitted sequences and their intermediate exposure. Recalculate incremental margin after each confirmed fill and compare available funds plus local reservations. Prefer filling required protective buy legs before opening dependent shorts; a submitted hedge or partial hedge does not protect the full planned quantity. Cap dependent shorts to confirmed protection in the configured ratio. For exit, remove risk-bearing shorts before releasing their hedges unless the user supplied another validated policy.

A basket margin endpoint is a calculator, not atomic multi-leg execution. Define bounded timeouts, residual-leg handling and an authorized rollback policy. If a leg fails, freeze further risk-increasing legs and reconcile actual positions. Never blindly repeat a timed-out leg. Support mixed-success autoslice responses as individual order IDs if slicing is requested.

Deliver `basket_plan.py` and `basket_plan.json` with `legs, entry_sequence, exit_sequence, initial_margin, final_margin, peak_estimate, reserve, intermediate_states, fill_dependencies, failure_actions`.

Example: “Plan entry and exit of this hedged call spread with current positions included.”

Checks: an unfilled hedge blocks its short; final margin below cash cannot override insufficient peak margin; a failed second leg leaves an explicit residual-position report.

Sources (verified 2026-10-13): [Kite margin calculations](https://kite.trade/docs/connect/v3/margins/); [Kite orders](https://kite.trade/docs/connect/v3/orders/).

