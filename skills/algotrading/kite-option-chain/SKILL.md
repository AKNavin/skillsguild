---
name: kite-option-chain
description: "Build a timestamped option chain from Kite instruments and quotes, with explicit missing-data flags."
---

# Build a live option chain

## Inputs

Accept `underlying`, exact `expiry`, `asof`, spot `exchange:tradingsymbol`, and a freshness limit in seconds. Require an authenticated client supplied by the caller; never print credentials. Use Asia/Kolkata for exchange sessions and timezone-aware timestamps.

## Build

1. Read the current instrument master with `kite.instruments("NFO")`. Select `segment=NFO-OPT`, CE/PE, requested underlying and expiry. Resolve the underlying using a checked mapping; do not rely on a substring search of trading symbols. Retain symbol, token, strike, expiry, lot size and tick size.
2. Fetch `kite.quote()` for selected `NFO:tradingsymbol` keys and spot. Batch within the documented 500-instrument limit and respect the account/API request limit. Kite has no documented option-chain or Greeks endpoint; assemble the chain locally.
3. Join calls and puts by underlying, expiry and strike. Keep absent quotes as missing rows. Record quote timestamp, last-trade time, bid/ask and quantities, last price, volume and raw `oi`. Use quote depth, not instrument-master `last_price`, for current liquidity.
4. Kite OI is individual units: store `oi_units`; derive `oi_lots=oi_units/lot_size` using that contract's lot size. Record snapshot start/end times; a multi-request chain is not an atomic snapshot.

## Deliver

Write `chain.csv` with `asof,underlying,spot,expiry,strike,type,symbol,lot_size,bid,ask,ltp,oi_units,oi_lots,volume_units,quote_time,last_trade_time,status`; `status` is fresh, stale or missing. Also save the instrument-master date and batch skew.

Check duplicate contract keys and reject crossed/zero-sided quotes from midpoint calculations. Verify one lot conversion against a known contract. Example: “Build the nearest listed RELIANCE expiry chain with a 30-second freshness limit.” This produces analytics, not orders.

## Sources

[Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite staff clarification: OI is units](https://kite.trade/forum/discussion/9684/open-interest-difference). Accessed 2026-10-13.
