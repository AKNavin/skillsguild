# Algo Trading with SkillsGuild

Give your AI this guide and a concrete task, for example: “Use these skills to build a Kite screener for stocks within 3% of their prior 252-session high, then backtest its entry and exit rules with and without charges.” Read the relevant linked SKILL.md files before implementing. Download the skill ZIP when it contains scripts or fixtures; a single SKILL.md URL does not embed those supporting files.

## Choose a workflow

- **First connection:** project bootstrap → interactive authentication → instrument resolver → quote snapshot or historical download.
- **Stock research:** historical data validation → a focused stock signal → liquidity filter → multi-signal screener. A signal is a candidate; entry, exit, sizing and fill rules are separate decisions.
- **Options research:** dated option chain → liquidity filter → same-expiry OI walls / OI change / put-call ratio / IV and Greeks → contract and payoff checks.
- **Backtesting:** explicit strategy and data manifest → gross backtest → effective-dated fee ledger → net backtest → performance metrics → walk-forward validation and parameter robustness.
- **Regime-aware research:** trend, volatility or breadth classification → lagged regime routing → out-of-sample comparison with an unchanged baseline.
- **Execution engineering:** sizing → order and basket margin checks → risk guardrails → durable intent → order state machine → reconciliation and restart recovery → session runbook and monitoring. Start with the paper broker unless live trading is already explicitly authorized.

## What a skill delivers

Skills are concise implementation instructions with inputs, calculations or API steps, output artifacts and checks. They are not hosted trading bots or a promise of profitable results. Selected downloads include runnable Python reference helpers and synthetic fixtures. The website does not connect to anyone's broker account; each user supplies their own authorized connection in their own environment.

Ask the AI to deliver the executable program, configuration, exact run command, output files and validation results required by the skill. If a prerequisite is unavailable, it should report the missing input rather than invent prices, instruments, positions, charges or fills. Preserve the user's universe, date range, execution permissions and risk limits.

## Data and accounting boundaries

Use Asia/Kolkata timestamps and a verified calendar for the relevant exchange segment. Exclude unfinished bars; use only information available at decision time. The prior 252 sessions approximate 52 trading weeks and are different from a calendar-year window. Declare corporate-action adjustments, point-in-time universe selection, missing data and survivorship limitations.

Kite historical access depends on the account's plan. A free open-source skill does not make broker data free. Expired options history needs a separately licensed archive; Kite does not provide it. OI concentrations are descriptive heuristics, not observed dealer positions or guaranteed support and resistance. Current instrument masters cannot reconstruct past contracts or past lot sizes.

Gross backtests omit broker/exchange/tax charges. They must still declare slippage, spread and fill assumptions. Net backtests require fee schedules valid on each trade date, with correct per-order or per-day grouping. Zero-charge and charged results are directly attributable only when fills are identical. Margin, exercise, physical settlement, corporate actions and financing need explicit models when applicable.

Reference helpers intentionally have narrow scopes. Read their limitations before extending them. Synthetic demo fees are explicitly marked and require opt-in. Never present them as actual broker charges. Test results establish the tested cases, not every future broker or market condition.

## Keep the library open and maintainable

Fork the GitHub repository, add one focused skill, cite primary sources and include a realistic check. Prefer a small self-contained download over duplicated instructions or hidden dependencies. Community pull requests are reviewed before merging; the website rebuilds from merged skill folders. Public contributions must contain no credentials, account information or unlicensed market datasets.

Primary references: [Kite Connect API](https://kite.trade/docs/connect/v3/), [historical candles](https://kite.trade/docs/connect/v3/historical/), [margin and charges APIs](https://kite.trade/docs/connect/v3/margins/), [Zerodha charges](https://zerodha.com/charges/). Sources for individual skills are included in their instructions. Research checked 2026-10-13.
