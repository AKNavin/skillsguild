---
name: absolute
description: Reproduce the Indian Absolute + relative momentum portfolio backtest with user-authorised broker history and the frozen research rules.
---

# Absolute + relative momentum

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/absolute.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy absolute --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/absolute
```

The selected configuration is `absolute-L126-N30-M3`. Measure current close / close 126 sessions earlier − 1 using complete close history. Keep only stocks with positive returns, then rank those returns highest first. Choose up to 30 stocks and review quarterly. Unfilled slots remain in cash; no skipped month.

Positive signal-day volume required. Zero-return hurdle and cross-sectional stocks replace the original Treasury-bill comparison; cash earns zero.

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source](https://naaim.org/wp-content/uploads/2013/10/00D_Absolute-Momentum_gary_antonacci.pdf) · [Recorded result](../../results/absolute.json)
