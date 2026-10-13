---
name: kite-rate-limit-retries
description: Coordinate API requests and retries without duplicating ambiguous trading actions.
---

# Kite Rate Limits & Retries

Implement one account/app-wide scheduler shared by data workers and execution adapters. Use fixtures by default; live calls inherit only the existing authorized connection and scope.

Configure verified ceilings as upper bounds: quote one request/second, historical three/second, other endpoints ten/second; order placement additionally ten/second, 400/minute and 5000/day. Track per-order modification count against the documented 25 limit. Count attempts conservatively, not just successful responses; reserve operational headroom and schedule modifications/cancellations alongside execution traffic. Multiple processes must not each receive the full account budget.

Classify calls by semantics. Safe reads may retry transient network/5xx failures with bounded exponential backoff and jitter. Margin-calculation POSTs are read-like calculations. Authentication failures stop retries and require a new interactive session. Bad inputs and insufficient margins need correction, not repeated calls. For 429, pause the shared queue, honor Retry-After when present, then resume below the ceiling within the caller's deadline.

Order submission, cancellation, modification and GTT creation need reconciliation after timeout or ambiguous failure. Do not infer that an absent response means the request failed. Route these to a pending-reconciliation state; never blindly replay them. Persist daily counters and queued intent identities across restarts. Report unknown prior-day counts if history is unavailable rather than claiming a fresh allowance.

Deliver `request_scheduler.py`, `rate_policy.json` and metrics `endpoint, queued, attempted, retried, throttled, deadline_expired, next_allowed_at`. Policy values are dated and configurable for later broker changes.

Example: “Add a shared limiter to my scanner and order worker without duplicate orders.”

Checks: two workers stay within aggregate limits; a timed-out order is reconciled rather than retried; a token error suspends the queue without a retry storm.

Sources (verified 2026-10-13): [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/); [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Zerodha API execution rules, effective April 2026](https://kite.trade/forum/discussion/15912/preparing-to-comply-with-sebis-retail-algo-rules-static-ip-ratelimits-order-types).

