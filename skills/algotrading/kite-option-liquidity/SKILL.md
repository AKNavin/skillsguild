---
name: kite-option-liquidity
description: "Reject stale or costly option quotes using spreads, depth, volume and order-size coverage."
---

# Filter option liquidity

## Inputs

Accept timestamped depth, instrument lot/tick sizes, intended buy or sell side, order quantity in units and configurable limits. Demonstration limits may be quote age 10 seconds, relative spread 2%, at least two lots on the relevant best level and 100 traded lots; these are research settings, not universal execution standards.

## Compute

Reject absent, zero-sided, crossed or stale quotes before calculating `mid=(bid+ask)/2`, `spread=ask-bid`, `spread_pct=100*spread/mid`. Retain absolute spread in rupees because percentage spread is unstable for tiny premiums. Verify quantity is a positive lot multiple and prices are tick-aligned within rounding tolerance.

For a buy, walk available ask levels; for a sell, walk bids. Calculate visible-depth weighted average fill only for the covered quantity. If depth is insufficient, output `uncovered_quantity`; do not extrapolate a fill price beyond the visible book. Mark the calculation as a snapshot estimate, since displayed liquidity may disappear. Include both quote timestamp and last-trade timestamp: a current depth snapshot can coexist with an old last trade.

Use OI and session volume as supplementary activity filters, not guarantees of executable size. Convert their units consistently using contract lot size. Evaluate every leg of a proposed spread separately; liquid net premium does not compensate for an untradeable leg.

## Deliver

Write `option-liquidity.csv`: contract, side, quantity, bid, ask, spread, quote age, visible covered quantity, estimated VWAP and pass/fail reasons. Check zero midpoint, an order larger than depth, and asymmetric buy/sell depth. Example: “Screen this chain for a three-lot buy using my spread and freshness limits.” Return a shortlist only; this skill does not send orders.

## Sources

[Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/). Accessed 2026-10-13.
