---
name: kite-authentication
description: Implement interactive Kite login, secure token storage and predictable session expiry.
---

# Kite Authentication & Sessions

Implement a session manager for the user's existing Kite app. Preserve the user's authorized account and scope; use fixtures until that connection is available. The owner completes Kite's interactive login. Never automate account passwords or TOTP entry.

Use `KiteConnect.login_url()` to begin login and receive the one-use `request_token` at the registered redirect URL. Bind the callback to the initiating local/browser session and validate expected callback parameters. Exchange it promptly with `generate_session(request_token, api_secret=...)` on the backend. The REST equivalent is `POST /session/token` with SHA-256 of api_key + request_token + api_secret. Do not implement an invented OAuth refresh grant.

Validate the returned `user_id` against the configured owner before installing the token with `set_access_token()`. Store the access token in the existing secret store or an owner-only local file excluded from version control. Redact callback query strings, headers and token responses from logs.

Track `authenticated_at` and the next 06:00 Asia/Kolkata expiry boundary. Treat expiry, master logout and `TokenException` as session loss: disable new execution, stop reconnect storms, mark session `login_required`, and expose an interactive login link. Revalidate with `profile()` after restart. Invalidate an existing session only when logout was requested.

Deliver `session_manager.py`, `session_status.json` containing only `user_id, state, authenticated_at, expected_expiry, checked_at`, and callback tests.

Example: “Add daily Kite login to my scanner using the existing app credentials.”

Checks: replaying a consumed callback cannot create a second session; a wrong user ID is rejected; simulated token expiry blocks new orders without erasing the order journal.

Sources (verified 2026-10-13): [Kite login and user APIs](https://kite.trade/docs/connect/v3/user/); [Kite errors and rate limits](https://kite.trade/docs/connect/v3/exceptions/); [Official Python SDK](https://github.com/zerodha/pykiteconnect).

