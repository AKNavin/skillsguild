# Validation coverage

The backtest-only release replaces the former 130-skill catalogue with twelve frozen portfolio strategies from the supplied research handoff. Recorded prices end 22 October 2026. There is no generic HR, Content or Algo skills library in the new build.

## Research reproduction

The portable engine was compared against all 48 saved runs: twelve strategies, two periods, baseline and source stress. All available source report fields matched exactly, including detailed equity/trades/ledger where present. The maximum absolute equity difference was zero. `packages/research/verification.json` records dataset, code and source hashes without copying raw market data.

Thirteen synthetic tests cover hand-reconciled accounting, delayed buys, sale settlement, zero-cost conservation, skipped zero-volume buys, no future-price use in signals, CLI/API agreement, input immutability, invalid candles/dates, warm-up and shared-session filtering. These tests verify the documented model. They do not make its current-universe selection, daily-bar execution assumptions, fractional shares or terminal estimates executable reality.

## Broker tooling

Thirty-one mocked/local tests cover Zerodha and FYERS token exchanges, Dhan identity checks, credential/error redaction, Host/Origin/CSRF/cookie checks, request-size bounds, history-only routes, session disposal, pacing, retry limits, invalid candles, resume hashes and manifests. A synthetic 100-stock download-to-runner integration verifies that an index-only special session is removed from the shared calendar before per-stock quarantine and that the resulting accounting reconciles.

No fresh live broker login or data entitlement was tested for this release. Users authenticate locally in the packaged form. There is no guarantee against memory inspection by another process with the same operating-system permissions. Tokens remain sensitive and broker-side permissions may exceed the limited helper interface.

## Build and delivery checks

```sh
python -B -m unittest discover -s packages/research/tests -v
python -B packages/broker/test_broker.py
npm run validate
npm run build
python -B scripts/check_packages.py
```

Build validation reconciles saved endpoint returns, drawdowns and trade counts against the catalogue. Package validation checks all twelve ZIPs and the combined pack, CRCs, file hashes, executable source parity, direct resources and absence of retired catalogue output. Rule diagrams are original SVGs with no visible text; their captions distinguish conceptual inputs/ranking from the actual saved equity curves.

Frontend syntax and a temporary DOM rendering harness exercised twelve strategies across both periods, chart modes, filters, ledger counts and broker prompts. Browser automation stopped because the computer-use runtime could not reliably identify the active browser URL. Browser layout and live clipboard behaviour therefore remain unverified; the static and rendering checks passed.
