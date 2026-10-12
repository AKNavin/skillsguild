---
name: strategy-research-brief
description: Turn a trading research idea into an explicit hypothesis, point-in-time data requirements and an evaluation plan. Use before implementation or backtesting, not for recommending investments.
---

# Strategy research brief

Turn the supplied idea into a research specification another person could reproduce. Label assumptions rather than silently deciding material trading rules.

## Establish the idea

Capture the proposed mechanism, instrument universe, data frequency, decision timestamp and holding horizon. Ask only for missing details that prevent a coherent specification. For optional choices, present a provisional default and its rationale.

## Make it testable

- Write the hypothesis and an explicit result that would weaken it.
- Define entry, exit, sizing and conflict rules without using information unavailable at the decision time.
- List required data fields, their availability timestamps, adjustments and quality checks.
- Specify the simplest useful baseline and a chronological development/evaluation split.
- Describe fee, spread, slippage, liquidity and capacity assumptions to measure, rather than inventing precise values.
- Predefine primary metrics, uncertainty checks and a small set of justified sensitivity experiments. Track explored variations so selection effects remain visible.

## Deliverable

Provide a research brief with hypothesis, rule specification, data contract, experiment plan, failure criteria and unresolved decisions. Include a compact pseudocode sketch when it removes ambiguity. Keep hypothetical examples visibly hypothetical. Do not fabricate historical results, imply profitable performance, or initiate live trading.
