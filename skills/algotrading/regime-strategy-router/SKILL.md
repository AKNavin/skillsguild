---
name: regime-strategy-router
description: "Apply a versioned policy that enables research strategies only when regime and data conditions match."
---

# Route strategies by regime

## Inputs

Accept regime records with `available_at,valid_until,trend,volatility,breadth,quality`, named strategy definitions, allowed combinations and a user-specified risk budget. Every mapping is an explicit policy to validate, not a claim that a certain strategy always suits a regime. Default examples may route trend strategies to confirmed trends and pause on missing data; do not invent production sizing.

## Implement

At decision time join only labels already available and not expired. Evaluate quality and risk constraints before the regime mapping. Unknown/stale input yields `blocked_data`; a breached risk limit yields `blocked_risk`. When several strategies qualify, use a declared priority or budget allocation and ensure combined exposure respects the portfolio limit.

Persist `policy_version,previous_state,new_state,effective_time,reason,input_versions`. Make processing idempotent by `(policy_version,decision_timestamp,strategy_id)`. Apply configurable confirmation/cooldown to avoid frequent switching. On restart replay state before considering new decisions.

Distinguish permission for new entries from treatment of existing positions. A regime change must not implicitly close positions, cancel orders or release hedges. Require an explicit existing-position policy and keep protective exits functioning. Backtest policy transitions, costs and allocation together using chronological out-of-sample regimes; computing labels over the entire future sample leaks information.

## Deliver and check

Write `routing-decisions.jsonl` containing strategy, state, allowed research weight, reasons and source timestamps; output proposed changes separately from execution. Test stale labels, competing strategies, restart replay and a regime flip with an existing protected position. Example: “Route my two paper strategies using these trend/volatility labels and this fixed 50/50 budget policy.” This skill produces decisions for simulation or review; live broker actions require separate authorization.

## Sources

[Bailey et al.: Backtest Overfitting in Financial Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/). Accessed 2026-10-13.
