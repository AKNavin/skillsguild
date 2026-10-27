# How to read these backtests

The current release contains fifteen paper-inspired Indian cash-equity portfolio studies supplied in the [research handoff](https://app.notion.com/p/4025c39e2b32816b9004f4510464b0ee). The [27 October supplement](https://app.notion.com/p/4065c39e2b3281bab21ecdf5df401d96) adds intermediate-horizon momentum, high-volume premium and calendar-month seasonality. Price cutoff: 22 October 2026. Results are exploratory simulations, not live performance. The site preserves saved figures rather than generating a promotional equity curve.

## Periods and selection

169 predefined configurations across six rounds were evaluated. Each family was selected by the largest minimum Calmar score across independently restarted 2018–2022 development and 2023–2025 validation windows, with the documented tie-breaks. Consequently the full 2018–2025 headline period influenced selection. The separate 2026 comparison has been viewed repeatedly and is not an untouched holdout. Both displayed periods restart in cash; 2026 does not inherit the prior portfolio. Annual returns within 2018–2025 use continuous holdings.

## Universe and prices

The study starts from a current Nifty500-derived snapshot, maps 500 stocks and excludes nine retrospectively flagged series, leaving 491. Historical constituent exits and failures are absent. Industry labels are current rather than point-in-time. Provider-adjusted prices are not an independently reconstructed corporate-action ledger. Sparse shared-calendar sessions were removed under the original panel rule. These choices can materially overstate investable outcomes.

The website publishes normalized derived equity, aggregate metrics and trade-return summaries. It does not distribute the raw broker cache. Local reproductions require authorised data and a declared universe. Cross-broker history may differ in coverage, corrections and adjustment treatment; exact replication requires the same snapshot.

## Portfolio accounting

Each test starts at equity 100, fractional adjusted shares, no leverage and zero cash interest. Rankings use a completed session before the review. Removed stocks sell at the next available open; additions buy at signal + three sessions, including the initial all-cash allocation. Sale proceeds remain unsettled for two sessions. New-position budgets use signal equity divided by the configured basket size; retained holdings are not resized. Unavailable buys are skipped and unavailable sells retry. No intramonth stops or replacements are added. Remaining holdings receive estimated terminal-close liquidation with costs, explicitly identified in trade summaries.

## Fees and execution assumptions

The saved baseline applies 0.1187406% buy charges and 0.1037406% sell charges to slipped notional, plus 0.05% adverse slippage per side. This is a current proportional delivery-fee model applied uniformly across history. It omits fixed DP/account charges, historical tariff changes, personal income taxes, dividends and delisting proceeds. It does not reconstruct circuit availability, depth, impact or account-size constraints. The reference model is not an exact Zerodha historical contract note and should not be relabelled as a Dhan or FYERS tariff when using their data.

## Reading the statistics

Total return is compounded growth from 100. CAGR annualizes by elapsed calendar time. Drawdown includes starting equity 100 and compares each value with its preceding peak. Sharpe uses daily observations, zero cash return and 252-session annualization. Completed positions include estimated terminal exits; they are not the number of orders. Trade contributions are normalized equity points, not rupees or results from rerunning without that stock. Large concentration effects must be considered alongside aggregate return.

Round 1's source stress doubles slippage; later rounds also restrict one-price candles. Fill restrictions can change the portfolio path, so the stressed result is not guaranteed to be a lower bound. Daily-open feasibility uses whole-day volume and, in those stress tests, the day's high/low: this is ex-post information, not information available at the open. Parameter perturbations and a genuinely new future period provide additional evidence; they cannot remove current-universe bias.

## Local authentication and broker history

The downloaded helper opens a local browser form. Keys and secrets stay out of the AI chat and normal command output; sessions live in the helper process. The helper exposes history access, not order placement. An unrestricted process on the same machine can still inspect other local processes/files, so this is a privacy-conscious workflow rather than a guarantee against a hostile local agent. Broker access tokens themselves are sensitive.

Rate limits and coverage are broker- and plan-specific. See the bundled broker README for the checked limits and enforced pacing. Zerodha's [historical API](https://kite.trade/docs/connect/v3/historical/) and [rate limits](https://kite.trade/docs/connect/v3/exceptions/), [Dhan documentation](https://dhanhq.co/docs/v2/), and [FYERS plans](https://fyers.in/api-docs/v3/getting-started/plans-and-limits/) are the primary references. Personal data access is distinct from public distribution rights; see the [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy).

## Additional signal conventions

Intermediate-horizon momentum uses calendar month-ends twelve and six months before the signal; the recent six months are excluded. High-volume premium uses the previous 100 sessions, excluding the signal day, and requires current share volume strictly above its historical 90th percentile before ranking the current/prior-mean ratio. Calendar-month seasonality averages the next holding month’s returns from up to five prior years, with at least two complete valid observations. These units are calendar months, sessions and calendar years respectively.

The new batch preserves the 22 October 2026 cutoff and adds 18 configurations; the preceding twelve results are unchanged. Intermediate momentum’s 2018–2025 return falls from 1209.07% to 904.25% when slippage doubles and one-price-bar fills are rejected, including a questionable TTML entry. Share-volume corporate-action adjustments are not independently reconstructed. Early seasonality estimates use particularly few years: January 2018 has at most two usable prior January returns.
