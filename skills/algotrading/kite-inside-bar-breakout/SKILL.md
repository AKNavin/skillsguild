---
name: kite-inside-bar-breakout
description: Detect a closed inside bar and the following close breaking a clearly selected range. Use when building or running this specific Kite-compatible stock screener.
---

# Inside-bar breakout

Build candidate signals and alerts, never implicit orders. All numerical defaults below are configurable examples, not profitability recommendations.

## Inputs

Closed OHLCV, interval, as-of timestamp, strict containment=true, and breakout boundary=mother bar by default. Resolve symbols through the current Kite instrument master, or accept a supplied CSV with documented identifiers and provenance.

## Calculate

At t-1, identify an inside bar relative to its mother t-2: high[t-1]<high[t-2] and low[t-1]>low[t-2]. If non-strict mode is chosen, use <= and >= and record that choice. Evaluate t only after it closes. Default bullish break is close[t]>high[t-2]; bearish is close[t]<low[t-2]. An optional inside-bar boundary uses t-1 levels and must be named explicitly. The pattern expires after that next bar in this minimal rule; multi-bar persistence requires a separate configured expiry. A bar's high/low touching both sides is not enough to infer event order.

Use Asia/Kolkata timestamps and the applicable exchange calendar, including holidays and session overrides. Evaluate completed bars only; record as-of time and reject missing required history rather than filling it with invented candles. Declare corporate-action adjustment and universe-selection policies; Kite OHLCV alone does not establish adjusted data or survivorship-free coverage.

## Deliver

Produce a runnable Python script, example configuration, exact run command, and CSV plus JSON output. Include exchange, symbol, signal timestamp, parameters, data-quality status and these fields: `mother_timestamp,inside_timestamp,mother_high,mother_low,inside_high,inside_low,boundary_mode,direction`. Retain excluded symbols with reasons. State the earliest time each signal was available. Keep secrets outside code and output.

## Check

Equal highs fail strict containment. A close beyond only the inside bar does not pass mother-boundary mode. Three needed bars must be complete and contiguous for the chosen trading calendar.

Example request: "Scan daily NSE candles for strict inside bars followed by a close beyond the mother bar's range."

Sources: [Kite Connect historical candles](https://kite.trade/docs/connect/v3/historical/); [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays). Verified 2026-10-13. The rules above are explicit implementation definitions; the sources document data semantics and background, not expected returns.

