---
name: kite-instrument-resolver
description: Resolve stock, future and option symbols using dated Kite instrument snapshots.
---

# Instrument & Contract Resolver

Implement `resolve_instrument(query, as_of)` using a dated Kite instrument master. Use the existing authorized connection or a supplied CSV; offline fixtures must work without credentials.

Fetch `GET /instruments` or `kite.instruments(exchange)` once per trading day, cache the raw snapshot with retrieval time and checksum, then parse types explicitly. Retain `exchange, tradingsymbol, instrument_token, name, instrument_type, segment, expiry, strike, tick_size, lot_size`. Treat the dump's last_price as stale reference data.

For cash shares, resolve exact exchange and tradingsymbol. For derivatives, filter exchange/segment, underlying, FUT/CE/PE, expiry and strike. Return all candidates on ambiguity; do not guess from a symbol string. For “nearest expiry”, select the earliest still-valid expiry in the snapshot after applying the user's rollover cutoff. Read actual expiries and lot sizes rather than hardcoding weekdays or historical quantities.

Use exchange + tradingsymbol + snapshot date as a durable contract mapping; instrument tokens may be reused after expiry. Archive expired mappings already collected. Missing expired option data must return `unavailable`, not a replacement current contract.

Write `instruments/<date>.csv`, `instrument_manifest.json` and `resolved_contracts.json`. Each resolution contains `query, as_of, snapshot_date, status, candidates[], selected, reason`; selected includes the fields above. Expose tick rounding and whole-lot validation from the same metadata.

Example: “Resolve the nearest valid monthly NIFTY future and its ATM call/put pair from today's master.”

Checks: identical strikes on two expiries remain distinct; a reused token cannot overwrite an archived contract; an ambiguous underlying produces candidates instead of a fabricated symbol.

Sources (verified 2026-10-13): [Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite historical candles](https://kite.trade/docs/connect/v3/historical/).

