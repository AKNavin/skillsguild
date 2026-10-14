# Validation coverage

Checked 13 October 2026. The catalogue has 68 skills: 64 Algo Trading, two HR and two Content. The 62 new Algo Trading skills are implementation recipes with primary sources, explicit inputs and outputs, and checks. Five packages include executable offline reference helpers. This is bounded validation, not a certification that every recipe or future live integration is correct.

## Reproduce the public checks

Use Node.js 22+ and Python 3.10+; no third-party packages are needed for the reference helpers.

```sh
python -B scripts/test_skills.py
npm run validate
npm run build
python -B scripts/check_packages.py
```

GitHub Actions runs the offline suites, builds the site and validates packages before publishing. The package check compares ZIP contents with source, verifies CRCs and direct resources, and checks the AI indexes and combined download.

## Executable examples

| Package | Cases | What is exercised |
| --- | ---: | --- |
| `kite-52-week-breakout` | 9 | Prior windows, near-high boundaries and rank, configurable buffer, current/future-bar exclusion, missing sessions, duplicates, zero volume, audit fields |
| `backtest-gross` | 13 | Next-open fills, adverse slippage, cash/equity identity, terminal marking, no invented leverage, fee configuration and date boundaries |
| `backtest-net` | 13 | Same reference engine packaged independently; component charges, caps, dependent taxes, zero-cost equivalence and covered fee dates |
| `kite-oi-walls` | 9 | Maximum eligible OI and distance tie-breaks, unit/lot conversion, expiry isolation, expiry-time gating, stale spot/quotes, missing sides, spread and band exclusions |
| `kite-order-state-machine` | 11 | SQLite persistence, duplicate/late updates, ambiguous submission, restart blocking, reconciliation, partial-fill cancellation races and conflicting evidence |

All five suites passed: 55 test executions, including the same 13 backtest cases in two self-contained downloads. The backtester is one long-only cash equity with fixed units and next-bar-open execution. The order-state helper is a simulator without a network adapter. OI-wall fixtures are synthetic snapshots. See each skill for its exact scope and run command.

Independent forward checks used a separate author's raw six-symbol, 252-session fixture: 11 assertions passed for near-high/breakout boundaries, missing history, unfinished bars and future invariance. This revealed missing output audit fields, which were added and retested. A separate author also ran five gross/net forward tests with manually reconciled dated costs and cash-constrained paths. Three additional fresh-fixture signal tests passed. These isolated evaluation artifacts are separate from the public packages.

## Authorized read-only Kite checks

The interactive session-token exchange succeeded. Profile, funds/margins, positions and orderbook reads returned expected response shapes; the account values were not published. Instrument downloads contained 10,343 NSE rows and 38,055 NFO rows. A six-instrument equity/index quote request succeeded.

Historical retrieval returned 524 daily candles for each of INFY, RELIANCE, TCS, SBIN, HDFCBANK and NIFTY 50, spanning 2 September 2024–12 October 2026: 3,144 candles total. The five equities were replayed through the daily signal baseline and a deliberately simple diagnostic target rule, producing 285 simulated fills. OHLC checks, prefix invariance, prior-high isolation, nonnegative cash, zero-fee equivalence and synthetic-fee attribution passed.

The diagnostic strategy is a plumbing check, not a researched trading recommendation. The replay used observed benchmark dates as a coverage cross-check and simplified daily session times. Corporate-action adjustment, point-in-time universe membership and actual historical charges were not verified. Synthetic fee attribution does not validate real Zerodha historical tariffs. Raw downloaded market data and all credentials remain outside the public repository and packages.

## Remaining limits

Additional live requests were blocked by the tool's approval policy after the successful reads above. Live intraday collection, WebSocket recovery, option-chain snapshots, broker margin calculators and virtual contract-note comparisons were therefore not verified against this account. No orders, cancellations, position changes or GTT changes were made.

The other catalogue skills specify actionable implementations and checks; they have not all been implemented and run end to end. There is no tested full-market scanner, multi-leg execution service, derivative settlement engine or historical options database bundled here. Broker entitlements, margin availability, fees, exchange schedules and contract rules must be rechecked for each real deployment.

Website checks covered business/topic filtering, multiword search, instruction dialogs, copying AI links and ZIP/resource integrity. The 14 October 2026 layout update was checked at 1280, 1024, 820, 600, 390 and 320 pixels: eight, six, four, three, two and one card per row respectively, without horizontal overflow. Cards provide direct Copy link and Download actions. Skill images are text-free original vector illustrations; the six existing illustrated cards and SG tab logo are preserved.
