---
name: kite-put-call-ratio
description: "Compute OI and volume PCR for a stated expiry and strike universe without mixing units."
---

# Calculate put-call ratios

## Inputs

Require underlying, exact expiry or an explicit aggregation policy, spot, strike band and quote-age limit. The default demonstration is one expiry and all available strikes; allow a symmetric percentage or strike-count band. Report the chosen universe with the result.

## Compute

Start from the same snapshot for both CE and PE. Validate contract identity, lot size and completeness. Kite OI and volume arrive as units; normalize both sides consistently to lots when contract lot sizes differ. Do not mix units on one side with lots on the other.

Calculate `pcr_oi=sum(put_oi_lots)/sum(call_oi_lots)` and separately `pcr_volume=sum(put_volume_lots)/sum(call_volume_lots)`. Volume is cumulative for the trading session. For intraday-window volume, difference same-contract snapshots only within that session, and flag counter resets. If the denominator is zero, output null with `zero_denominator`; do not substitute a large number.

Publish included and excluded counts and both raw sums. Require a configurable coverage floor before assigning any label. For multiple expiries, provide separate rows first; a pooled ratio must explicitly sum the same normalization units and disclose its expiry coverage. Avoid inferring a bullish or bearish trade directly: put volume includes buyers and sellers, and raw OI does not reveal intent.

## Deliver and check

Write `pcr.csv` with `asof,underlying,expiry,scope,put_oi_lots,call_oi_lots,pcr_oi,put_volume_lots,call_volume_lots,pcr_volume,coverage,status`. Check a hand-calculated pair and that excluding an illiquid strike updates numerator, denominator and coverage together. Example: “Give nearest-expiry NIFTY OI PCR within 5% of spot and its 20-session percentile from my archive.” Do not invent an archive or place orders.

## Sources

[Kite instruments and quotes](https://kite.trade/docs/connect/v3/market-quotes/); [Kite staff clarification: OI is units](https://kite.trade/forum/discussion/9684/open-interest-difference). Accessed 2026-10-13.
