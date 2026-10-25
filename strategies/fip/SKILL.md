---
name: fip
description: Reproduce the Indian Continuous-information momentum portfolio backtest with user-authorised broker history and the frozen research rules.
---

# Continuous-information momentum

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/fip.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy fip --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/fip
```

The selected configuration is `fip-L126-N10-M1`. Calculate the 126-session return ending 21 sessions before the signal. Rank eligible stocks and retain the top 20%, rounded up; keep only positive returns. In that same formation window, count fractions of up and down days. ID = sign(formation return) × (fraction down − fraction up). Zero-return days remain in the denominator. Rank lowest ID first, then highest formation return, then symbol. Choose up to 10 stocks and review monthly.

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source](https://www3.nd.edu/~zda/Frog.pdf) · [Recorded result](../../results/fip.json)
