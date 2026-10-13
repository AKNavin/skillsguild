---
name: kite-oi-walls
description: "Rank F&O stocks by distance to same-expiry call and put open-interest concentrations."
---

# Nearest call and put OI walls

## Inputs

Accept stock universe, a common as-of timestamp, expiry rule, strike-distance band, minimum OI/liquidity and maximum quote age. A demonstration configuration is nearest non-expired listed monthly expiry, strikes within 10% of spot and OI of at least 100 lots; expose every threshold. If users ask for the closest wall, distinguish distance to a defined concentration from simply choosing the nearest strike.

## Compute

For each stock, choose one expiry before ranking strikes. From the instrument master and timestamped full quotes retain eligible calls with `strike >= spot` and puts with `strike <= spot`. Convert Kite `oi` units to lots using each dated lot size; use a consistent unit throughout.

Define the call wall as the eligible call strike with maximum OI and put wall as the eligible put strike with maximum OI. Break OI ties by smaller distance to spot, then strike. Keep both sides from the same expiry. Calculate `call_distance_pct=100*(call_strike-spot)/spot` and `put_distance_pct=100*(spot-put_strike)/spot`. Rank separate ascending call-distance and put-distance lists; a missing side remains null, never zero.

Report total eligible OI, wall share of that side's eligible OI, spread, quote age, expiry and excluded-contract count. A wall is a reproducible OI-concentration heuristic, not proof of support/resistance, dealer positioning or gamma exposure. Do not infer who is long or short from aggregate OI.

## Deliver and check

The standalone helper consumes CSV columns `underlying,expiry,type,strike,spot,spot_timestamp,quote_time,bid,ask,oi_units,lot_size,volume_units`. Supply a complete selected-expiry snapshot; the helper cannot discover absent contracts. Run `python scripts/oi_walls.py fixtures/chain.csv --expiry 2026-10-27 --asof 2026-10-13T11:00:10+05:30 --out oi-walls.json`. The synthetic fixture is not market data. Thresholds have CLI flags; run `--help` for names. On expiry day supply the verified --expiry-at contract timestamp; post-expiry snapshots are rejected.

Output includes nullable call/put walls, distances, concentration shares, exclusions, freshness and separate rankings. Export `stocks` to CSV if requested. Run `python -m unittest discover -s tests`; check cross-expiry invariance, OI unit conversion and stale/missing-side nulls. Example: “Rank my F&O universe within 1% of its nearest-expiry call wall.” Analytics only; no order placement.

## Sources

[Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite staff clarification: OI is units](https://kite.trade/forum/discussion/9684/open-interest-difference). Accessed 2026-10-13.
