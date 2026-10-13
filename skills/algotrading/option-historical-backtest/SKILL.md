---
name: option-historical-backtest
description: "Backtest options from a validated archive with point-in-time contracts and realistic multi-leg fills."
---

# Backtest historical options

## Inputs

Require strategy rules, date range, historical underlying prices, option quotes/trades or OHLC, dated instrument masters, fees and execution model. Specify data license and provenance. Kite does not provide expired-options historical data; its continuous-history facility is for daily futures. Saving tokens alone does not make expired option data retrievable. Use an existing permitted archive or collect data prospectively.

## Implement

Create a coverage matrix by session, expiry, strike and option type. At each simulated decision time, choose the expiry and strike from contracts listed then, using only then-available spot and features. Preserve historical lot changes and settlement rules. Never construct old chains using today's instruments or implied volatility.

Fill buys at the next available ask and sells at bid with stated delay and size limits. If only OHLC exists, label a bar-based approximation and use next-bar fills plus a conservative slippage model. When stop and target both fall inside one bar, require lower-frequency evidence or report pessimistic and optimistic bounds; do not pick a favourable ordering.

Model individual leg fills, rejected/missing legs, margin/cash, rolls and expiry exercise/assignment. Report physically settled obligations explicitly. Missing quotes produce skipped trades or bounded uncertainty under a declared policy, never interpolated zero-price fills. Derive historical Greeks only from contemporaneous inputs with labelled model assumptions.

## Deliver and check

Write `coverage.csv`, `fills.csv`, `positions.csv`, `equity.csv` and `backtest-manifest.json` with dataset/version hashes, time convention and cost assumptions. Test an unavailable strike, a partial spread fill and a contract lot-size change. Example: “Backtest my monthly debit spread on this licensed archive and stop if chain coverage is below 95%.” This is research, not live trading.

## Sources

[Zerodha: expired option history unavailable](https://support.zerodha.com/category/trading-and-markets/charts-and-orders/charts/articles/historical-data-for-expired-f-o-contract); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE individual-security derivatives specifications](https://www.nseindia.com/static/products-services/equity-derivatives-individual-securities). Accessed 2026-10-13.
