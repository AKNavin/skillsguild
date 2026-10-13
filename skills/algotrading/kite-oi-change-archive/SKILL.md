---
name: kite-oi-change-archive
description: "Archive option OI snapshots and calculate honest intraday or previous-close changes."
---

# Archive OI and detect changes

## Inputs

Accept contracts, cadence, market calendar, baseline mode (`previous_session_close` or a named intraday snapshot) and maximum timestamp skew. Use an append-only store with unique key `(exchange,symbol,expiry,strike,type,exchange_timestamp)`. Keep the original payload separately from calculated fields.

## Build

Save daily instrument masters and full quotes containing `oi`, volume, last price and exchange/receipt timestamps. Persist Kite OI as units, together with the contemporaneous lot size. Derive lots only after validating the mapping. A token alone is not a permanent contract identity.

For each same-contract pair calculate `delta_oi_units=current_oi-baseline_oi` and `delta_oi_pct=100*delta_oi_units/baseline_oi`; report percentage as null when the baseline is zero. Record baseline timestamp and age. For previous close, require a genuine archived closing observation from the last trading session; `oi_day_high`, `oi_day_low` and price `net_change` do not supply yesterday's OI. An unavailable baseline produces `baseline_missing`.

OI changes need not accompany every price tick. Never synthesize changes from unchanged observations. Comparing different expiries or a reused token produces meaningless differences; separate expiry rolls and corporate-action adjustments. Price-up/OI-up may be labelled a descriptive combination, not verified new long positioning.

## Deliver

Write immutable snapshots plus `oi-changes.csv`: contract key, baseline/current timestamps, OI units/lots, deltas, price change and quality flags. Summarise missing coverage before ranking movers. Test restart idempotency, zero-baseline handling and a reused-token fixture. Example: “Archive my RELIANCE chain each minute and compare OI with yesterday's stored close.” This archives data and computes analytics only.

## Sources

[Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite staff clarification: OI is units](https://kite.trade/forum/discussion/9684/open-interest-difference); [Zerodha: expired option history unavailable](https://support.zerodha.com/category/trading-and-markets/charts-and-orders/charts/articles/historical-data-for-expired-f-o-contract). Accessed 2026-10-13.
