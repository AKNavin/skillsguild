---
name: walk-forward-validation
description: "Evaluate a strategy on chronological unseen periods while checking feature and label leakage."
---

# Validate with walk-forward splits

## Inputs

Accept data range, strategy, parameter candidates, training/validation/test lengths, maximum label or holding horizon and optimization objective. A demonstration is 24 training months, 3 validation months, 3 test months, advancing 3 months; adapt to sample size and keep all windows chronological.

## Implement

Record each observation's `event_time,available_at,label_end`. Fit parameters, scalers, universes and thresholds on training data only. Select configuration on validation; freeze it before each unseen test. Purge training/validation observations whose future labels overlap the later evaluation interval and add an explicit embargo where dependent features/labels require it. Historical feature warm-up may precede the test but cannot use future values or fitted test statistics.

Declare boundary-position policy: either enter each test flat and exclude signals awaiting execution across the boundary, or carry positions using rules frozen before the boundary. Apply the same policy in all windows. Stitch only non-overlapping test equity periods; overlapping test predictions must not be counted twice. Never choose the best test window or retune after seeing a test and still call it untouched.

Create availability assertions `available_at <= decision_time < fill_time` for close-based signals. Perturb future rows and confirm earlier decisions are unchanged. Check point-in-time universe membership, delisted stocks, corporate actions and option contract availability separately; chronological splitting alone cannot repair those leaks.

## Deliver and check

Write `splits.csv`, selected configuration per window, held-out fills/equity and a leakage report with observed evidence. Include every tried configuration and test-window performance, plus an untouched final holdout if provided. Example: “Walk-forward validate this breakout strategy with my three parameter values and one-month test windows.” This evaluates research and does not deploy a strategy.

## Sources

[Bailey et al.: Backtest Overfitting in Financial Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/). Accessed 2026-10-13.
