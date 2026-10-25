# Reproduce the twelve Indian equity studies

This package contains the frozen signal formulas and accounting engine from the supplied five-round research handoff, dated 23 October 2026. It does not select new parameters. It runs locally against your own authorised Zerodha daily-history panel and cannot place orders.

Requires Python 3.11+ and the pinned NumPy dependency. From this folder:

```sh
python -m pip install -r requirements.txt
python runner.py --strategy high52 --data-dir /private/kite-panel --start 2026-01-01 --end 2026-10-22 --output /private/results/high52-2026
python -m unittest discover -s tests -v
```

On Windows, use quoted absolute Windows paths in place of the example paths. `python runner.py --help` lists every option. Strategy IDs are `high52`, `residual`, `absolute`, `lowvol`, `riskmom`, `industry`, `fip`, `reversal`, `lowbeta`, `lowmax`, `mad`, and `smad`. The frozen settings are in `strategies.json`.

## Input data contract

Keep this folder outside your public repository. A dataset directory contains:

```text
kite-panel/
  Universe.json
  Data-quality-quarantine.json
  data/
    NIFTY_500.json
    NIFTY_50.json
    RELIANCE.json
    ...one file for every non-quarantined stock...
```

`Universe.json` has an `items` object keyed by trading symbol. Every selected stock has `kind: "stock"` and a nonempty `industry` string. Additional instrument metadata is permitted. `Data-quality-quarantine.json` has a `symbols` array. Use the handoff's universe, industry labels and quarantine to reproduce its results; substituting today's constituents changes the experiment.

Each instrument file is an ascending array of unique date-only daily candles:

```json
[{"date":"2026-01-01","open":100,"high":103,"low":99,"close":102,"volume":10000}]
```

The example is synthetic. Prices must be finite and positive, volume finite and nonnegative, and OHLC internally consistent. All stock files are required, although their histories may start after listings. The Nifty 500 calendar defines shared sessions. The original filter removes sessions with fewer than 100 eligible-stock candles; Nifty 50 must cover every retained session. Missing stock observations remain missing for scoring and execution, while last known closes may be carried only for valuation.

Download sufficient warm-up before the requested start: the residual signal needs at least 505 retained sessions before the run's first session. The other signals require their frozen lookback windows. The original panel starts before 2018. The runner rejects missing warm-up, invalid dates, future requested end dates, malformed candles and a data folder used as its output folder. The loader never writes to the input dataset. `--quarantine /path/to/Data-quality-quarantine.json` supports an explicitly separate original quarantine file.

## Outputs and comparison

`results.json` contains summary metrics, dated equity, cash ledger, individual orders, closed trades, signals, skipped events and price-index benchmarks. `equity.csv`, `orders.csv` and `trades.csv` support your own audit. `panel-audit.json` lists coverage and omitted shared sessions. `run-manifest.json` records the code hashes, every consumed input-file hash, a combined dataset fingerprint, runtime versions and all selected run options. Credentials and absolute source paths are not recorded. Results include individual trade prices; keep them private unless your data agreement permits publication.

To reproduce the published periods, run `2018-01-01` through `2025-12-31` and, separately, `2026-01-01` through `2026-10-22`. Each run restarts at normalized equity 100. Reproducing the original results requires the original dataset bytes and frozen settings. Fresh downloads can revise history; matching provider names alone does not establish identical data.

The default execution uses 5 basis points of one-way slippage and the source's percentage charges. A gross sensitivity run requires both `--no-costs --slippage-bps 0`. For round 1's source stress use `--slippage-bps 10`; for rounds 2–5's source stress use `--slippage-bps 10 --avoid-locked`. These variants are reruns with their own quantities, not a subtraction of fees from the original equity curve.

## Exact accounting conventions and limits

- Rankings use completed signal-session history. High-proximity uses the signal session's daily high as part of its 252-session window. These are portfolio ranking studies, not intraday or fresh-breakout orders.
- At the run start, rank using the prior retained session. Subsequently rank before the first retained session of the selected calendar rebalance month. Sell outgoing names at the next eligible daily open. Buy incoming names three retained sessions after the signal. Rebalance sales settle two retained sessions after the sale. These are the original conservative research delays, not a claim about current settlement rules.
- Slot budget is equity at the signal divided by the configured portfolio size. Retained holdings are not resized. Quantities are fractional; cash earns zero interest. No leverage or short positions.
- Buy charges are `0.001 + 0.00015 + (0.0000307 + 0.000001) * 1.18`; sell charges are `0.001 + (0.0000307 + 0.000001) * 1.18`, applied to slipped notionals. These are the study's current percentage assumptions used throughout history. Historical tariffs, DP charges, per-order rounding and all real-account frictions are not reconstructed.
- Fills require a finite open and positive **whole-day** volume. The stress variant also requires whole-day high above low. Those are ex-post daily-bar feasibility assumptions; the full day's volume and range were not known at its open.
- Final holdings receive a hypothetical final-close sale, including slippage and sell fees, even when the close is a stale valuation. Orders label these `terminal_estimate`; they are not observed executions. The cash ledger must reconcile, and the engine checks final equity against summed closed-position P&L.
- CAGR uses inclusive calendar days divided by 365.25. Daily Sharpe uses 252 sessions and zero cash return. The original zero-variance Sharpe convention is zero; it is not statistical evidence of a risk-free strategy. Comparators are price indices rather than investable total-return series, and do not model the strategy's entry delay or costs.
- Current universe membership, current industry labels and a whole-history quarantine introduce survivorship and retrospective selection. Corporate actions, dividends, delistings and renamed instruments are not fully reconstructed. 2026 has already been viewed in previous research; it is not a pristine holdout.

`engine.py` preserves the original `metrics`, `run` and `benchmark` function bodies; `signals.py` preserves the five rounds' scoring bodies. Only portable loading, dispatch, validation and reporting are new. `source-provenance.json` identifies original source hashes. The tests use synthetic data and verify causality of score functions, hand-computed fees, delayed fills, settlement, conservation of cash, invalid input rejection and CLI/API parity. These checks establish implementation behaviour, not future profitability.
