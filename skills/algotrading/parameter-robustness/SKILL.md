---
name: parameter-robustness
description: "Test whether performance survives nearby settings, execution costs and different market periods."
---

# Check parameter robustness

## Inputs

Require strategy version, baseline parameters, a small economically meaningful neighbourhood, objective and fixed train/validation/test split. Include execution stress ranges, minimum sample requirements and a compute budget. Example neighbours for a 20-bar lookback are 15, 20 and 25, not thousands of arbitrary decimals.

## Run

Evaluate all candidates on the same permitted data and execution assumptions. Save failed runs and every attempted configuration. Rank by the predeclared validation objective, but report the neighbourhood distribution and worst supported case, not just its best value. Prefer evidence of a broad plateau to a single isolated optimum; this is an assessment criterion, not a promise of future returns.

Stress slippage/spreads, next-bar latency, missing observations, per-trade size and effective-dated costs one factor at a time before selected combinations. Repeat the fixed candidates across prespecified time and symbol groups. Separate parameter instability from small-sample noise; list trade count and exposure for each group. Do not remove a bad regime after observing it without treating that decision as new model selection.

For uncertainty estimates use contiguous-block resampling or another dependence-aware method, state block length and seed, and never shuffle price bars into an impossible trade path. Record the number of trials; a high Sharpe chosen after many attempts has selection bias. Keep final holdout sealed until the selected specification is frozen.

## Deliver and check

Write `sensitivity.csv` with parameters, costs, period, trade count, return and drawdown; add a compact heatmap and `trial-manifest.json`. Verify baseline reproducibility and that evaluation uses identical data versions. Example: “Stress my 20-day breakout across 15/20/25 days and 5/10/20 bps execution friction.” Research only; do not auto-deploy the winner.

## Sources

[Bailey et al.: Backtest Overfitting in Financial Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886). Accessed 2026-10-13.
