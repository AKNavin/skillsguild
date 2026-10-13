---
name: backtest-net
description: "Calculate net backtest equity using effective-dated costs and explicit execution friction."
---

# Backtest with charges

## Inputs

Require gross strategy/fill rules, historical dates, exchange, product, account category, quantities, execution friction and a sourced fee schedule applicable on each trade date. Keep broker charges separate from bid/ask spread and slippage to avoid double counting.

## Run

The self-contained demonstration is `python scripts/backtest.py fixtures/bars.csv --mode net --fees fixtures/fees-demo.json --allow-demo --out result.json`. Fixture fees are synthetic, not Zerodha rates; replace them with verified dated rules for research. Input CSV is `timestamp,bar_end,open,high,low,close,target`: one equity's daily session opening/closing timestamps in +05:30, positive OHLC and target 0/1 known at close. Verify session completeness separately. Prior targets fill next open with fixed units, adverse slippage and one fill per order. The helper applies date/side/NSE/CNC rules, Decimal rounding, dependent taxes and cash checks. It omits derivative settlement, partial-order caps, portfolio netting and intraday square-off.

For a production extension aggregate partial executions at order level before applying brokerage caps. Add delivery DP charges at their actual grouping scope, exercise/assignment, financing and broker square-off charges when applicable. Reject uncovered fee dates and unsupported settlement events. Today's Kite virtual contract-note API can cross-check present-day examples, not establish historical rates.

Keep an identical-fill cost attribution report: `net_pnl=gross_pnl-sum(charges)`. Separately report a full cash-constrained rerun if charges prevent some entries, because then gross and net paths may differ. Retain open marked positions instead of inventing terminal liquidation.

## Deliver and check

Save fee components per order, fills, cash/equity and cost-source manifest. Run `python -m unittest discover -s tests`; check effective-date boundaries, buy/sell taxes, cap application and zero-fee equivalence. Example: “Run this strategy net with my dated NSE cash fee schedule, plus 5 bps slippage.” Research only.

## Sources

[Current Zerodha charges](https://zerodha.com/charges/); [Kite margin and virtual contract-note APIs](https://kite.trade/docs/connect/v3/margins/); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/). Accessed 2026-10-13.
