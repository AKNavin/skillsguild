---
name: kite-option-contract-validation
description: "Validate expiry, lot size, tick size and settlement obligations before an options workflow."
---

# Validate option contracts

## Inputs

Accept underlying, exchange, requested expiry/strike/type, as-of timestamp, proposed signed quantity, price and whether the workflow can hold through expiry. Resolve the exact contract from today's instrument master; require an explicit match instead of constructing a symbol from a remembered expiry convention.

## Validate

Store `exchange,symbol,token,underlying,expiry,strike,type,lot_size,tick_size,master_date`. Confirm CE/PE, positive lot/tick size, quantity as an integer lot multiple and price on the tick grid. Check expiry against current NSE contract specifications and exchange calendar, including holiday adjustments. Never hard-code weekday, weekly availability or lot sizes across dates.

Enrich settlement mode and expiry timestamp from official exchange rules; these are not fully described by a Kite symbol. NSE individual-stock options are European and physically settled. Treat index and stock settlement separately, and verify current broker expiry restrictions, delivery margins and exercise/assignment treatment before allowing a hold-through-expiry plan.

If settlement requires delivery, report the resulting stock/cash obligation for each ITM long/short call/put scenario and whether holdings/funds can satisfy it. Do not assume a bought option's maximum premium loss captures operational delivery obligations. Preserve raw source/version dates; fail with `specification_unverified` when current rules cannot be confirmed.

## Deliver and check

Write `contract-check.json` with resolved contract, specification sources, proposed quantity/price, settlement scenarios and `valid_for_workflow` plus reasons. Tests: a non-lot quantity fails; a reused token cannot match an old contract; a holiday-shifted expiry resolves from listed instruments. Example: “Validate these stock-option legs for next monthly expiry and show physical-settlement obligations.” Validation is not permission to place orders.

## Sources

[NSE individual-security derivatives specifications](https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities); [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/). Accessed 2026-10-13.
