---
name: mad
description: Reproduce the Indian Moving-average distance trend portfolio backtest with user-authorised broker history and the frozen research rules.
---

# Moving-average distance trend

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/mad.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy mad --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/mad
```

The selected configuration is `mad-L50-N30-M3`. At the review close, compute the mean of the latest 50 closes and the mean of the latest 200 closes, both including that close. Score = 50-session mean / 200-session mean; rank highest first. This is a ranked distance, not a fresh crossover signal. Choose up to 30 stocks and review quarterly. There is no additional requirement that the ratio exceed one.

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source](https://onlinelibrary.wiley.com/doi/10.1002/rfe.1118) · [Recorded result](../../results/mad.json)
