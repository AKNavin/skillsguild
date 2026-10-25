# Reproduce a SkillsGuild backtest

Ask the user which broker they use (Zerodha, Dhan or FYERS), which strategy and dates they want, and whether they want the frozen research rules or a separately labelled experiment. FYERS users must identify their plan because historical coverage and rate limits differ.

Download and extract the complete strategy ZIP. Use a Python 3.11+ virtual environment and install `research/requirements.txt`. Read the bundled `broker/README.md` and `research/README.md` for commands, data schema and prerequisites. The combined ZIP has these same folders at its root.

Launch `python broker/broker_login.py` and ask the user to complete its local browser form. Never ask for keys, secrets, request tokens or access tokens in chat. Do not inspect credential fields, take login screenshots, read browser storage, or print authentication responses. The helper retains the session in memory and exposes a limited session reference; stopping it clears that session. Same-computer process access is not cryptographic isolation from an unrestricted coding agent.

Use an approved instrument mapping and the broker downloader to produce `Universe.json`, `Data-quality-quarantine.json` and daily `data/SYMBOL.json` files. The twelve reference studies use a large Nifty500-derived stock universe and benchmark histories, not one symbol. Industry strategies need the saved industry mapping. The local broker README documents identifiers, limits, caching and resume behaviour. Download warm-up history before the requested test start. Missing entitlements or truncated history must be reported, not silently filled or replaced with synthetic data.

Run the chosen frozen configuration:

```sh
python research/runner.py --strategy high52 --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/high52
```

Use `--help` for supported options. Do not run parameter selection or retune on 2026 to reproduce the saved study. Preserve source and data hashes. Return metrics, equity and trade files, cost/accounting checks and a comparison with the saved result. The same code against another broker or newer dataset may differ; explain the mismatch instead of forcing agreement.

The reference model starts at normalized equity 100 with fractional adjusted shares, delayed purchases, drifting retained holdings, simplified delivery charges and estimated terminal liquidation. A rupee-sized, whole-share account is a different experiment. Current constituents and retrospective exclusions introduce bias. 2018–2025 influenced selection and 2026 has already been inspected. Read the methodology before interpreting returns.

The package provides historical data access and simulation only. Credentials and raw data stay local; the public site needs neither. Broker data plans and licensing are separate from this MIT-licensed code.
