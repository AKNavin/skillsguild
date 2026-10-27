# SkillsGuild — Indian strategy research

Compare fifteen paper-inspired portfolio backtests, inspect the rules, and reproduce them with AI in your own environment. The library is open source under MIT; broker data has separate access and usage terms.

## Use

Open a strategy, select a broker and copy its AI instructions or download its ZIP. The AI asks about broker and period, launches the local login form, downloads authorised daily data with rate limits, and runs the frozen Python implementation. Read [AI-GUIDE.md](AI-GUIDE.md), [METHODOLOGY.md](METHODOLOGY.md), and the package README files before running.

The website is static and does not receive credentials. The fifteen saved results are exploratory current-universe cash-equity simulations. They use fractional adjusted shares, simplified fees and terminal estimates. 2026 has already been inspected. No historical result is a promise of executable profit.

## Develop

Node.js 22+ builds the static site; Python 3.11+ runs the research package and tests. Install `packages/research/requirements.txt` in a virtual environment.

```sh
npm run validate
npm run build
python -B scripts/check_packages.py
npm run dev
```

Research source is in `packages/research`; local broker tooling is in `packages/broker`. Each `strategies/<id>` contains a frozen manifest and concise AI instructions. Derived saved outputs live in `research/results`; the original broker cache is excluded. `scripts/import_research.py` explicitly imports the user's original research artifacts when provided their location; normal builds need no private files or credentials.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [VALIDATION.md](VALIDATION.md). Retired generic skills remain recoverable through Git history.
