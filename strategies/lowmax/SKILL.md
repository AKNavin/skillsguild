---
name: lowmax
description: Reproduce the Indian Low MAX / smaller recent price jumps portfolio backtest with user-authorised broker history and the frozen research rules.
---

# Low MAX / smaller recent price jumps

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/lowmax.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy lowmax --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/lowmax
```

The selected configuration is `lowmax_5-L21-N30-M1`. Calculate the latest 21 simple daily returns for each eligible stock. Average the largest five returns. Rank stocks by the lowest such average. Choose up to 30 stocks and review monthly. No positive-momentum requirement.

Complete history, positive volume and nonconstant daily returns. Rolling-session month and long-only selection adapt the MAX anomaly; high-MAX short leg omitted.

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source](https://pages.stern.nyu.edu/~rwhitela/papers/max%20jfe11.pdf) · [Recorded result](../../results/lowmax.json)
