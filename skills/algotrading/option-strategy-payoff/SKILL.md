---
name: option-strategy-payoff
description: "Calculate expiry payoff, breakevens and tail risk for a specified option spread."
---

# Calculate multi-leg option payoff

## Inputs

Accept each leg as `{type:CE|PE,strike,premium,signed_quantity,expiry,underlying}`. Quantity is underlying units, positive long and negative short; optionally accept lots and convert once using each contract's lot size. Require the same underlying and expiry for a single expiry-payoff curve. Multi-expiry calendars require valuation of unexpired legs and cannot use all legs' intrinsic values at the first expiry.

## Compute

At terminal spot `x>=0`, calculate `sum(q*(max(x-K,0)-premium))` for calls and `sum(q*(max(K-x,0)-premium))` for puts. Include any stock leg as `q_stock*(x-entry_price)`. Deduct the explicitly supplied fee ledger; distinguish known entry fees from modelled exercise/exit costs.

Evaluate payoff at zero, every strike and a high reference spot, then solve linear roots within each strike interval for exact breakevens. Inspect the slope of the final unbounded interval to identify unlimited upside loss/profit; a finite chart range must not be labelled maximum loss. Calculate bounded maxima/minima from piecewise-linear endpoints. Keep gross and net curves distinct.

For physically settled stock options, add a table of shares/cash owed or received by terminal region. Payoff equality does not remove settlement funding needs. Before-expiry mark-to-market is a separate model with IV/time assumptions; do not present expiry payoff as today's executable P&L.

## Deliver and check

Save `payoff.csv` (`spot,gross_pnl,estimated_costs,net_pnl`) and `payoff-summary.json` containing legs, net premium, breakevens, bounded/unbounded extrema and settlement obligations. Check a long call, a bounded vertical and a naked short call. Example: “Plot this 100/110 call debit spread for one verified lot with my entry fills.” Analysis only.

## Sources

[NSE individual-security derivatives specifications](https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities); [Zerodha option calculator and model inputs](https://zerodha.com/z-connect/general/how-to-use-the-option-calculator). Accessed 2026-10-13.
