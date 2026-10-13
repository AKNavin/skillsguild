---
name: kite-risk-guardrails
description: Enforce exposure, loss and freshness limits with a durable halt state.
---

# Risk Limits & Kill Switch

Implement an independent pre-trade and continuous risk gate. Inputs include per-order notional, gross/net exposure, per-symbol concentration, maximum open orders, daily loss, drawdown, margin reserve and stale-data limits. Use the existing authorized connection only within its scope; default action is halt new entries and produce a report.

Compute exposure from reconciled positions plus worst-case pending entry fills and unresolved submissions. Unknown order outcomes retain reservations. Include external account positions in account-level risk while preserving strategy ownership. Mark positions using fresh executable-side prices where available, and report uncertainty during stale feeds. Define daily P&L baseline, fee treatment and session reset explicitly; do not reset losses on process restart.

Evaluate limits before accepting an intent and periodically thereafter. Persist a latched state `RUNNING, HALT_ENTRIES, CANCEL_ENTRIES, REDUCE_ONLY, STOPPED`. State transition reasons and timestamps belong in the journal. Only an explicit configured reset after reconciliation may clear a halt.

Cancellation and flattening are separate user-authorized actions, not consequences automatically implied by monitoring. If permitted, cancel only identified risk-increasing strategy orders first, confirm outcomes, then generate quantity-capped reducing orders from current exposure. A late fill or manual position change must trigger recalculation so an exit cannot reverse the position. Keep protective orders where appropriate; broker acceptance/fills still require reconciliation.

Deliver `risk_gate.py`, `risk_policy.json` and `risk_state.json` with `state,limits,measurements,violations,as_of,authorized_actions,unresolved_orders,reset_required`. Never describe this local application gate as disabling the entire broker account.

Example: “Stop new entries after ₹5,000 daily loss and alert me about residual exposure.”

Checks: restarting retains a halt; unknown fills consume risk; a permitted flatten sequence cannot submit more than the current owned exposure.

Sources (verified 2026-10-13): [Kite portfolio APIs](https://kite.trade/docs/connect/v3/portfolio/); [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Kite margin calculations](https://kite.trade/docs/connect/v3/margins/).

