# Validation coverage

The backtest-only release replaces the former 130-skill catalogue with fifteen frozen portfolio strategies from the supplied research handoff. Recorded prices end 22 October 2026. There is no generic HR, Content or Algo skills library in the new build.

## Research reproduction

The portable engine was compared against all 60 saved runs: fifteen strategies, two periods, baseline and source stress. All available source report fields matched exactly, including detailed equity/trades/ledger where present. The maximum absolute equity difference was zero. `packages/research/verification.json` records dataset, code and source hashes without copying raw market data.

Seventeen synthetic tests cover hand-reconciled accounting, delayed buys, sale settlement, zero-cost conservation, skipped zero-volume buys, no future-price use in signals, CLI/API agreement, input immutability, invalid candles/dates, warm-up and shared-session filtering. These tests verify the documented model. They do not make its current-universe selection, daily-bar execution assumptions, fractional shares or terminal estimates executable reality.

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

Build validation reconciles saved endpoint returns, drawdowns and trade counts against the catalogue. Package validation checks all fifteen ZIPs and the combined pack, CRCs, file hashes, executable source parity, direct resources and absence of retired catalogue output. Rule diagrams are original SVGs with no visible text; their captions distinguish conceptual inputs/ranking from the actual saved equity curves.

Frontend syntax and a temporary DOM rendering harness exercised twelve strategies across both periods, chart modes, filters, ledger counts and broker prompts. The original release had no browser layout verification because browser automation stopped. On 27 October, browser checks confirmed the fifteen-entry catalogue, all three new strategy detail pages and rule images, the volume strategy’s 2026 result toggle, and the seasonality AI dialog with public instruction/download URLs. The narrow viewport layout was visually reviewed. Live clipboard behaviour and broker authentication remain unverified.

## 27 October additions

Added intermediate-horizon momentum, high-volume premium and calendar-month seasonality from the supplied round-6 handoff. Four additional independent tests verify calendar endpoints, signed intermediate returns, the strictly greater volume percentile with the signal day excluded, same-month seasonal averages with missing-year rejection, and calendar-based warm-up. The future-candle test now covers all fifteen families. All sixty baseline/stress source runs match exactly, including full equity, orders, selections and ledgers where present. This is 15 strategies × 2 periods × 2 execution settings; maximum absolute equity difference is zero. The preceding twelve recorded result series are preserved.
