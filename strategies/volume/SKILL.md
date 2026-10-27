---
name: volume
description: Reproduce the Indian High-volume premium portfolio backtest with user-authorised broker history and the frozen research rules.
---

# High-volume premium

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/volume.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy volume --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/volume
```

The selected configuration is `volume-L100-N30-M1`. At each completed month-end compare current share volume with its preceding 100 sessions, excluding the signal day. Qualify only when current volume is strictly above the prior 90th percentile; rank current volume / prior mean volume highest first. Require finite nonnegative past volume, positive mean/current volume and complete close history. Select up to 30 stocks monthly; unfilled slots remain cash. No price-momentum or earnings filter.

Long-only high-volume-premium adaptation. Uses historical raw share-volume percentiles and ratio ranking, not shares-outstanding turnover or the paper’s long/short portfolio. Share-volume corporate-action changes are not independently reconstructed; splits and similar events can affect this signal.

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source](https://doi.org/10.1111/0022-1082.00349) · [Recorded result](../../results/volume.json)
