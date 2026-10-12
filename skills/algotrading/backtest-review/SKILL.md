---
name: backtest-review
description: Review a supplied trading backtest, its code or methodology for data leakage, execution assumptions, costs and robustness. Use for research-quality review, not live trade selection or execution.
---

# Backtest review

Produce a research review grounded in the supplied implementation and results. Distinguish observed faults, plausible concerns, and evidence that is missing.

## Inputs

Use the strategy rules, data coverage and frequency, backtest code or execution description, performance results, and fee/slippage assumptions. If these are incomplete, proceed with the available evidence and identify which conclusions remain unresolved.

## Review

- Trace when each signal input becomes available relative to the trade. Check look-ahead, future-adjusted features, and whether close-price signals assume fills at that same close.
- Check universe construction, delisted instruments, corporate actions, timezone alignment, missing bars, and point-in-time availability.
- Trace position sizing, overlapping trades, cash or leverage constraints, transaction costs, spread, slippage, rejected orders and liquidity assumptions.
- Separate development, validation and untouched evaluation periods. Identify repeated tuning against the purported test set.
- Inspect dependence on a small number of trades, instruments or market periods. Propose sensitivity checks whose parameters have an economic rationale.
- Reconcile reported returns, turnover, drawdown and benchmark treatment with the underlying results. Do not manufacture metrics from incomplete data.

## Output

Create a short conclusion followed by a table of finding, evidence, impact and next check. Include reproduction steps for demonstrated bugs and a prioritised research checklist. When execution is available and authorised, run bounded checks against the supplied data; report checks actually performed separately from proposed experiments.

Do not treat an attractive backtest as evidence of future returns. This skill evaluates research methodology and does not authorise broker access, account changes or order placement.
