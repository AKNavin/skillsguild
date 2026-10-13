---
name: kite-paper-broker
description: Test order logic with simulated fills, partial execution, rejection and cash accounting.
---

# Kite-compatible Paper Broker

Implement a local paper adapter with the same strategy-facing methods as the Kite adapter: place, modify, cancel, orders, trades, positions and margins. It must never forward mutations to a real broker. If optional live quotes are authorized, keep their read client structurally separate from simulated execution.

Accept starting cash, instrument metadata, fees, latency, slippage, participation cap and event fixtures. Assign synthetic order/trade IDs clearly prefixed PAPER. Emit the same local normalized states used by the strategy, including partial fill, rejection, cancellation and submission ambiguity for recovery tests.

For quote replay, buy from available ask and sell to available bid subject to volume/depth caps and configured slippage. Do not fill at a stale LTP merely because it exists. A limit order cannot fill worse than its limit. Do not claim exchange queue position from top-of-book data.

For candle replay, execute new close-based signals no earlier than the next eligible bar. If both stop and target occur within one OHLC bar, use a disclosed conservative ordering or report ambiguity; do not choose the profitable path. Record the fill model and data granularity with every run.

Maintain signed positions, reserved cash, realized/unrealized P&L and fees. Reject invalid lot/tick sizes and unavailable buying power. Simulated margin is a declared model, not a promise of broker acceptance. Allow deterministic seeds for failures and latency.

Deliver `paper_broker.py`, `paper_config.json`, `paper_trades.csv` and `paper_report.json` with model assumptions, rejected intents, final equity and event trace.

Example: “Run my Kite strategy offline with partial fills and a cancel/fill race.”

Checks: no mutation reaches the real adapter; duplicate cancel is harmless; identical inputs and seed produce identical fills and equity.

Sources (verified 2026-10-13): [Kite orders](https://kite.trade/docs/connect/v3/orders/); [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/).

