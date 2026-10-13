---
name: trading-fee-ledger
description: "Calculate auditable trading costs from orders with dated rules and correct charge bases."
---

# Build a trading fee ledger

## Inputs

Accept executions with `trade_time,order_id,exchange,segment,product,symbol,side,quantity,price,account_type,event_type`. Event type distinguishes ordinary trade, exercise, assignment, physical settlement and broker square-off. Include contract-note date and instrument lot size when reconciling derivatives.

## Implement

Build a versioned rules table: `effective_from,effective_to,exchange,segment,product,account_type,side,event_type,component,basis,rate,fixed,min,max,rounding,source_url`. Store rates as decimal fractions, rupees and quantity units explicitly. No open-ended reuse of a current tax rate for historical dates. Re-read the official charges page and dated exchange/regulatory notices before filling production rates; the page was checked on 2026-10-13, not certified indefinitely.

Aggregate fills by executed order before capped brokerage. Calculate each applicable component on its specified base: share/futures turnover, option premium turnover or exercise intrinsic value. Apply side-specific STT/CTT and stamp duty, exchange fees, SEBI fees, IPFT and GST on the stated taxable components. Add delivery DP, financing and special-event charges with their proper grouping and rounding; do not apply a per-scrip charge to every partial fill.

Use `POST /charges/orders` (`kite.get_virtual_contract_note(params)` in the official Python SDK) to cross-check current ordinary-order examples. The API returns a virtual contract note, not a historical tax-rate archive, and does not replace the broker's final ledger. Flag unsupported events or rule overlaps instead of silently charging zero.

## Deliver and check

Produce `fee-ledger.csv`: order/group key, component, basis value, rule ID, raw amount, rounded amount and source; reconcile totals against sample contract notes and report residuals. Test both sides, a split execution hitting a brokerage cap and a fee-change boundary. Example: “Explain every charge in these fills using rates effective on their trade dates.” No broker mutation is required.

## Sources

[Current Zerodha charges](https://zerodha.com/charges/); [Kite margin and virtual contract-note APIs](https://kite.trade/docs/connect/v3/margins/). Accessed 2026-10-13.
