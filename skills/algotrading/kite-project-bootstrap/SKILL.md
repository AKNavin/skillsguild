---
name: kite-project-bootstrap
description: Build a minimal Kite project and check its data, session and execution capabilities.
---

# Kite Project Bootstrap

Implement a small Python project that another strategy can import without triggering network calls or orders at import time.

Inputs: project directory, required exchanges/data, and requested mode. Use the user's existing authorized connection. Default to paper mode if live execution scope is absent; do not collect account passwords, TOTP seeds or tokens in chat.

Create `pyproject.toml`, a tested dependency lock, `config.example.toml`, `broker.py`, `capabilities.py` and `tests/test_capabilities.py`. Separate configuration, secret lookup, market data and order adapters. Configuration stores environment-variable names or secret references, never values. Add a paper adapter implementing the same interface.

Use the official `kiteconnect` package; inspect the installed version and signatures for required methods, including `market_protection` if requested. Keep HTTP credentials on the backend. Call `profile()` only through an authorized connection and record enabled exchanges/products rather than trusting documentation examples.

Produce `capabilities.json` with `checked_at, sdk_version, mode, session_valid, market_data, historical_data, allowed_exchanges, allowed_products, execution_ready, blockers[]`. Distinguish market-data entitlement from authentication: a valid trading session does not prove access to streaming/history. Verify configured static egress against the owner's developer-console configuration for execution; do not send a test order to discover it. A capability with no evidence is `unknown`.

Example: “Build a paper-first Python Kite skeleton for NSE scanners and NFO execution, with a capability report.”

Checks: importing modules makes zero network calls; absent secrets produces a clear configuration error without values; a mocked data-entitlement failure leaves paper operation usable and execution disabled.

Sources (verified 2026-10-13): [Kite Connect introduction](https://kite.trade/docs/connect/v3/); [Official Python SDK](https://github.com/zerodha/pykiteconnect); [Kite Connect capabilities](https://www.zerodha.com/products/api/); [Zerodha static IP requirements](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip).

