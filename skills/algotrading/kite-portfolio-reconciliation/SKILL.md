---
name: kite-portfolio-reconciliation
description: Reconcile holdings, positions, trades and strategy exposure without double-counting.
---

# Portfolio & P&L Reconciliation

Implement a read-only reconciliation job using the existing authorized account connection or supplied snapshots. Fetch `holdings()`, `positions()`, `orders()`, `trades()` and funds with capture timestamps; note the collection span because the snapshots are not atomic.

Retain raw holdings and both positions.net and positions.day. Do not sum day and net positions: they are different views. Key positions by exchange, tradingsymbol and product; retain ISIN for holdings spanning exchanges. Keep T1, used, collateral, short and authorized quantities distinct. Do not blindly add holdings.quantity to CNC net quantity, which can double-count or misinterpret delivery transitions.

Rebuild strategy-owned expected exposure from a documented opening baseline plus unique signed fills, product conversions and explicitly recorded corporate-action adjustments. Compare to broker views using segment-specific semantics. Report external/manual trades and unexplained deltas; never silently adopt them into strategy ownership. Freeze new strategy exposure when the discrepancy exceeds the configured tolerance.

Compute an independently marked P&L ledger from fills, opening cost basis and timestamped marks. Keep realized/unrealized, gross/net-of-estimated-fees, and broker-reported P&L separate. Retain contract multiplier and valuation currency. Stale marks produce unknown current risk rather than a confident zero.

Deliver `reconcile_portfolio.py`, `portfolio_snapshot.json` and `reconciliation.csv` with `identity,product,expected_quantity,broker_quantity,delta,mark,mark_time,broker_pnl,ledger_pnl,ownership,reason`. Include unresolved items and a readiness gate; remediation is a proposed action unless execution is already authorized.

Example: “Reconcile my strategy ledger with Kite after manual trades and a restart.”

Checks: one trade ID is counted once; day/net views are not added together; an external position is reported without automatically being closed.

Sources (verified 2026-10-13): [Kite portfolio APIs](https://kite.trade/docs/connect/v3/portfolio/); [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Kite login and user APIs](https://kite.trade/docs/connect/v3/user/).

