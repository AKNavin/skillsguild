---
name: backtest-gross
description: "Run a gross backtest with zero broker charges and explicit fills, slippage and cash accounting."
---

# Backtest without charges

## Inputs

Accept strategy rules, completed bars, exchange calendar, initial cash, quantity, data-adjustment policy and spread/slippage assumptions. Gross means broker/exchange/tax charges are zero; it does not mean free execution. State spread, slippage and delay separately, even if the user explicitly selects zero.

## Run

For a runnable offline baseline use `python scripts/backtest.py fixtures/bars.csv --mode gross --out result.json`. The bundled standard-library helper accepts one equity's daily `timestamp,bar_end,open,high,low,close,target` rows. Timestamp is session open, bar_end is session close, both explicitly +05:30; target 0/1 is determined at that completed close. It fills the prior target at the next row's open, with configurable adverse basis-point slippage, fixed units and a cash check. It retains open positions at the end and marks them to close. It has no shorting, leverage, stops, partial fills, corporate-action engine or intraday square-off logic. Verify session completeness against the market calendar before running.

For wider strategies, preserve the same timing discipline. Prevent future universe membership, adjusted prices and features from leaking into historical decisions. Reject missing bars under a stated policy. A stop/target pair touched within one OHLC bar has unknown order: use lower-resolution data or show pessimistic/optimistic bounds. Gap-through stops fill at available prices, not guaranteed stop levels.

## Deliver and check

Save fill ledger, marked equity and manifest with dataset hash, parameters, timezone, fill timing, slippage and `charges=0`. Confirm cash plus marked positions equals equity; altering future bars must not alter earlier fills. Run `python -m unittest discover -s tests`. Example: “Run my close-based breakout targets gross, with 5 bps adverse slippage and no leverage.” Never infer future profitability or place orders.

## Sources

[Kite historical candles](https://kite.trade/docs/connect/v3/historical/); [Bailey et al.: Backtest Overfitting in Financial Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886). Accessed 2026-10-13.
