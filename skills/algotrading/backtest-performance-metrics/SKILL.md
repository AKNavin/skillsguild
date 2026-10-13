---
name: backtest-performance-metrics
description: "Reconcile equity and calculate comparable returns, drawdowns, exposure and benchmark results."
---

# Measure backtest performance

## Inputs

Require timezone-aware equity marked at a stated frequency, external deposits/withdrawals, fills, initial capital and a benchmark on the same dates. Use net liquidation value including open positions, not only closed-trade P&L. Choose gross/net cost basis explicitly and include non-trading days only under a stated convention.

## Compute

With no external flows, period return is `E_t/E_previous-1`. With flows, use correctly timed subperiod time-weighted returns; if only coarse flow timing is available, disclose the approximation. Calculate total compounded return and `CAGR=(E_end/E_start)^(365.25/calendar_days)-1` only for positive equity and a valid interval.

Set running peak including initial capital; `drawdown_t=E_t/peak_t-1`. Report minimum drawdown, peak/trough/recovery timestamps and unrecovered duration. For daily returns, report annualized volatility using a stated trading-day factor, and Sharpe from excess daily returns divided by their sample standard deviation times its square root. Zero volatility or insufficient observations yields null, not infinity. State the risk-free conversion and avoid annualizing trade-level returns as daily returns.

Report turnover, time and capital exposure, trade count, win rate, average win/loss and profit factor. Zero losses make profit factor undefined. Compare with a total-return benchmark and matching dates/currency; price-only benchmarks exclude dividends and must be labelled. Include flat periods and open losses.

## Deliver and check

Write `metrics.json`, daily returns and drawdown series with explicit units and assumptions. Reconcile `cash + marked_positions = equity` and manually verify a path with an initial loss and unrecovered drawdown. Example: “Compare my net daily equity with NIFTY TRI and show drawdown duration.” These metrics describe the supplied sample, not a forecast.

## Sources

[Bailey et al.: Backtest Overfitting in Financial Markets](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/). Accessed 2026-10-13.
