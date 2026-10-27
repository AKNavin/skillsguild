---
name: intermediate
description: Reproduce the Indian Intermediate-horizon momentum portfolio backtest with user-authorised broker history and the frozen research rules.
---

# Intermediate-horizon momentum

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/intermediate.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy intermediate --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/intermediate
```

The selected configuration is `intermediate-L12-N10-M3`. At the completed review close, measure the return between calendar month-ends twelve and six months earlier; January 2018 uses December 2016 to June 2017. Rank that older six-month return highest first; no positive-return filter. Require complete formation prices, a finite current close and positive current volume. Select up to 10 stocks and review quarterly in January, April, July and October.

Long-only Indian adaptation of intermediate-horizon momentum. Calendar-month endpoints, not twelve trading sessions; the most recent six months do not enter the return score. Execution stress: double slippage and reject one-price-bar fills. 2018–2025 return falls from 1209.07% to 904.25%; the baseline includes a questionable TTML entry on 5 October 2021. CUPID contributes +20.557 normalized equity points in 2026 while the whole portfolio returns +8.34%; this is contributor accounting, not a portfolio rerun excluding CUPID.

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source](https://doi.org/10.1016/j.jfineco.2011.05.003) · [Recorded result](../../results/intermediate.json)
