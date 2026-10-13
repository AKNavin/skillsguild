---
name: kite-position-sizing
description: Turn a stop-based risk budget into valid share or lot quantities and margin checks.
---

# Cash & Risk Position Sizing

Implement a deterministic sizing function for NSE shares, equity futures, bought options or explicitly bounded option spreads. Inputs are account risk capital, remaining strategy/day risk, entry, stop, slippage allowance, fee allowance, lot size and notional cap. This calculator emits an intent only; use authorized read connections for current margin estimates, otherwise fixtures.

For shares or linear contracts, calculate unit stop risk = abs(entry-stop) * price_multiplier + slippage_per_unit + fee_allowance_per_unit. Use multiplier one for ordinary NSE shares/equity-derivative quoted units; require explicit verified metadata for other markets. Set budget to the minimum of per-trade allocation and remaining portfolio/day allocation. Floor quantity to the instrument's whole lot: floor(budget / unit_risk / lot_size) * lot_size. Never round up.

For a bought option, offer either a specified premium stop or full premium-at-risk sizing, and label the selected model. For a defined-risk spread, compute worst-case expiry payoff loss plus costs per complete spread and size whole spread units. Do not apply underlying stop distance as an option's loss or use this bounded-loss formula for naked short options.

Apply cash/notional/concentration caps, then request current order/basket margins for the candidate. Decrease by whole lots until all gates pass; zero is a valid decision. A stop is an execution plan, not a guaranteed maximum loss; include a user-defined gap stress result.

Deliver `position_size.py` and `size_decision.json` with `quantity,lots,risk_budget,planned_stop_risk,stress_loss,notional,margin_required,binding_constraint,reasons`.

Example: “Size this equity breakout with a ₹2,000 planned risk and ₹50,000 notional cap.”

Checks: no candidate exceeds the budget after flooring; equal entry/stop is rejected; insufficient funds returns zero, never a fractional lot.

Sources (verified 2026-10-13): [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite margin calculations](https://kite.trade/docs/connect/v3/margins/).

