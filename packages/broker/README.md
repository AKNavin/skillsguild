# Local broker connection and historical data

This package connects **your own Indian broker account** and downloads daily cash-market history for the research runner. Python 3.10+ is sufficient; no packages need installing. The helper exposes historical candles only and contains no order route.

## Connect

Your AI should first ask which broker you use: **Zerodha, Dhan or FYERS**. Then run, from the extracted strategy package:

```text
python broker/broker_login.py
```

A browser window opens at `127.0.0.1`. If it cannot open automatically, use the printed local login link; `--no-browser` prints that link without opening a window. Enter credentials **in that window, never in chat, command arguments, environment files or the repository**.

- **Zerodha:** use the API key, API secret and fresh `request_token` from your normal Kite Connect login. The helper performs the SHA-256 token exchange. Alternatively use your API key and an existing access token. Historical access requires the appropriate Kite data entitlement. The broker login still happens on Zerodha's own page; the helper does not collect passwords or OTPs.
- **Dhan:** generate an access token in Dhan Web → My Profile → Access DhanHQ APIs. Enter that token and its client ID locally. This package uses the official existing-token method, not PIN/TOTP or the separate consent-app flow. Data API access is separate from free trading API access.
- **FYERS:** use your individual app ID, secret and fresh `auth_code` from the registered redirect URL, or the app ID and existing access token. Choose Standard or Prime to match your actual subscription. Complete broker login on FYERS; this helper exchanges the resulting code.

The helper verifies the session and displays an **opaque local session URL**. Give that URL to your AI. It is a temporary capability for historical downloads, not your broker access token. Keep the helper running. It retains the access token and required app/client identifier **in process memory only**; closing it, disconnecting, or its 12-hour lifetime discards them. There is no token file or restart persistence. Broker-side expiry can occur earlier, and closing the helper does not revoke a token at the broker.

Credentials are not put in logs, files, the website or responses. The window uses no external resources; the server validates Host, Origin, CSRF and request sizes, and does not enable CORS. This keeps credentials out of ordinary agent messages, **not out of reach of another program or AI with the same operating-system permissions**. Python cannot promise forensic erasure from memory or OS swap. Treat the session URL as private until the helper closes.

## Prepare the instrument map

Copy `broker/instruments-template.csv` to a private directory. Fill broker identifiers from your broker's current instrument master and add the intended stock universe. Do not guess benchmark IDs.

Required columns are `symbol,kind,industry`; include the identifier column for your broker:

| Broker | Mapping columns |
|---|---|
| Zerodha | `zerodha_token` |
| Dhan | `dhan_security_id`, `dhan_exchange_segment` (`NSE_EQ`, `BSE_EQ`, or `IDX_I`) |
| FYERS | `fyers_symbol`, for example the broker's complete `NSE:...-EQ` or index symbol |

Use local symbols `NIFTY_500` and `NIFTY_50` for the two mandatory index rows, with `kind=index`. Stocks use `kind=stock` and a nonempty industry. The portfolio runner needs at least **100 stock histories per retained session**; the two-row template alone cannot run it. ETF rows (`kind=etf`) may be downloaded but the current 12 stock-portfolio strategies select stocks. Futures, options and MCX contracts are intentionally unsupported by this cash-equity downloader.

Current instrument mappings are not historical universe membership. Save the universe selection date and independently establish point-in-time eligibility for stronger research claims.

## Download and resume

```text
python broker/download.py --session http://127.0.0.1:PORT/session/REFERENCE --instruments /private/instruments.csv --from 2015-01-01 --to 2026-10-22 --output /private/skillsguild-data
```

Replace the paths and reference with your local values. On Windows, a directory under your user-local application-data folder is suitable; keep the downloaded data out of public repositories and shared folders. The script refuses an output directory inside its source Git repository.

`--from` and `--to` are inclusive, **Asia/Kolkata** daily dates. End before the current local day: today's potentially incomplete candle is never used. Include several years of warmup before the first backtest date—2015 for the published 2018-start research. FYERS Standard cannot supply that full range: its daily-data window currently starts in 2021 and moves annually. Use an entitled plan/provider or a shorter independent test, and do not present it as an exact reproduction.

Requests use at most 365 calendar days per chunk. Completed chunks are cached with SHA-256 hashes; rerunning the same command resumes. Broker, map and date range must match the directory's existing request. A different range or provider needs a new directory. The helper paces below documented limits and retries rate-limit/server failures at most three times after the first attempt. Authentication and bad-input errors stop immediately. Close other downloaders or slow this one further if they share the same account's quota.

Output matches the runner's input contract:

```text
Universe.json
Data-quality-quarantine.json
data/NIFTY_500.json
data/NIFTY_50.json
data/<SYMBOL>.json
data-manifest.json
download-request.json
.cache/<request-hash>.json
```

Every candle is `{date,open,high,low,close,volume}`. The manifest records provider, plan, requested/returned range, hashes, unverified adjustments and coverage warnings. Empty histories and daily jumps above 40% place stocks in the quarantine file for review. The downloader then applies the research runner's shared-calendar rule: a session needs at least 100 eligible stock bars. Index-only and sparse sessions are reported as omitted, without quarantining stocks merely because those dates are absent. Internal gaps on the retained shared calendar are quarantined; all missing dates remain visible in the coverage audit. Original broker rows are retained and values are never filled or repaired automatically. Holidays, listings, suspensions, dividends, corporate actions and historical eligibility still require independent verification. Provider request success does not certify a complete dataset. Broker data is private under its applicable licence, not included in the open-source redistribution permission.

Run `python research/runner.py --help` for the research command. Your downloaded provider panel is an **independent replication**; exact agreement requires the original dataset, universe, quarantine, code and assumptions.

## Verified API references and tests

Documentation checked 24 October 2026:

- [Kite authentication](https://kite.trade/docs/connect/v3/user/), [daily history](https://kite.trade/docs/connect/v3/historical/), [3 requests/second history limit](https://kite.trade/docs/connect/v3/exceptions/).
- [Dhan authentication and profile verification](https://dhanhq.co/docs/v2/authentication/), [history, including exclusive `toDate`](https://dhanhq.co/docs/v2/historical-data/), [5 data requests/second and 100,000/day](https://dhanhq.co/docs/v2/).
- [FYERS individual authentication](https://fyers.in/api-docs/v3/api/authentication/individual-app/), [history](https://fyers.in/api-docs/v3/api/data-api/), [Standard/Prime limits and history coverage](https://fyers.in/api-docs/v3/getting-started/plans-and-limits/). Standard: 5/second, 50/minute, 5,000/day; Prime: 10/second, 500/minute, 500,000/day. Helper budgets are slightly lower and per-process; they cannot observe other applications' requests.

```text
python -B broker/test_broker.py
```

Tests use fake credentials, mocked broker responses and local-only HTTP. They verify authentication request construction, redaction, session disposal, HTTP boundaries, limits/retries, date/price validation, deterministic manifests and cache resumption. A synthetic 100-stock integration fixture downloads a panel containing an index-only special session and runs the packaged research CLI; it requires the research package's NumPy dependency. Tests do not establish that a live account has data entitlement or that current broker history exactly matches published results.
