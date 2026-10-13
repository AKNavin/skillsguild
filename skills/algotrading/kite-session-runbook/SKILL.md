---
name: kite-session-runbook
description: Coordinate startup, reconciliation, entry cutoffs and shutdown with recoverable state.
---

# Daily Trading Session Runbook

Implement a daily orchestrator for a supplied strategy without inventing its entry/exit rules. Use the existing authorized connection; default to paper operation until live scope and risk limits are configured.

Drive the lifecycle from a versioned exchange/segment calendar in Asia/Kolkata. Use configured entry cutoff, flatten deadline when authorized, and closeout grace period. Do not hardcode broker square-off times from memory or assume weekends can never have special sessions.

Startup states are `AUTH_CHECK, MASTER_READY, DATA_WARMUP, RECONCILING, RISK_READY, RUNNING`. Validate the account/session, obtain today's instrument mapping, recover the durable journal, reconcile orders/positions, obtain sufficient closed-bar history, and confirm feed freshness and configured execution readiness. New entries remain disabled until all gates pass. A failed gate produces a specific blocker and bounded retry policy rather than bypassing startup.

At the entry cutoff, stop creating new risk while continuing order and position management. At the configured shutdown, follow the user's overnight policy: retain permitted holdings, or reduce only the intended strategy exposure when already authorized. Never flatten unrelated holdings or assume MIS will be safely handled by broker auto-square-off. Reconcile late fills and unknown orders before declaring completion.

Write final order/trade/position/funds snapshots, persist counters and halt state, stop owned data workers and release the process lease. Report unresolved exposure prominently; a process that exited is not evidence of a flat account.

Deliver `session_runner.py`, `session_policy.json` and `session_report.json` with `session_date,mode,states,gate_results,open_orders,residual_positions,unresolved_intents,shutdown_status`.

Example: “Run the breakout scanner daily, stop entries at my cutoff and preserve authorized overnight CNC holdings.”

Checks: restart resumes reconciliation before signals; a holiday creates no session; unknown orders prevent a clean-close status.

Sources (verified 2026-10-13): [Kite login and user APIs](https://kite.trade/docs/connect/v3/user/); [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite portfolio APIs](https://kite.trade/docs/connect/v3/portfolio/); [NSE trading holidays](https://www.nseindia.com/resources/exchange-communication-holidays).

