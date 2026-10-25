"""Export only derived research results from the user's supplied study.

Run explicitly with --source pointing at the original research directory.
The normal site build does not access that private directory.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = dict(high52='Momentum', residual='Momentum', absolute='Momentum',
                lowvol='Defensive', riskmom='Momentum', industry='Momentum',
                fip='Momentum', reversal='Mean reversion', lowbeta='Defensive',
                lowmax='Defensive', mad='Trend', smad='Mean reversion')
LIMITS = [
    'Current Nifty 500-derived universe, not historical constituents: survivorship and selection bias.',
    '2018–2025 influenced parameter selection. The 2026 comparison has been inspected repeatedly; it is not an untouched holdout.',
    'Fractional adjusted shares and normalized starting equity 100; no account-size, market-impact or whole-share constraint.',
    'Current proportional delivery fees applied to all history; fixed DP fees, dividends, delisting proceeds and historical fee changes omitted.',
    'Provider adjustments, retrospective exclusions and terminal-close estimates limit executable interpretation.',
]
ASSUMPTIONS = [
    'Start each period separately in cash at normalized equity 100; cash earns zero.',
    'Rank on a completed session. Sell removals at the next tradable open; buy additions at signal + 3 sessions.',
    'New-position budget is signal equity / configured basket size, including entry fees; unfilled slots remain cash. Retained holdings drift.',
    'Long-only, unlevered; no intramonth stops. Unavailable sells retry; unavailable buys are skipped.',
    'Buy charge 0.1187406%, sell charge 0.1037406%, plus adverse slippage 0.05% per side.',
    'Remaining holdings are closed at estimated terminal adjusted closes with costs.',
]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n', encoding='utf-8')


def export_period(p):
    if len(p['dates']) != len(p['equity']):
        raise ValueError('Mismatched equity dates')
    peak = 100.0
    curve = []
    for d, e in zip(p['dates'], p['equity']):
        peak = max(peak, e)
        curve.append(dict(date=d, equity=e, drawdownPct=100*(e/peak-1)))
    year_ends = {}
    for d, e in zip(p['dates'], p['equity']):
        year_ends[d[:4]] = e
    prior = 100.0
    annual = []
    for year, e in year_ends.items():
        annual.append(dict(year=int(year), returnPct=100*(e/prior-1)))
        prior = e
    # Publish normalized performance and dates, never raw broker-price rows,
    # provider instrument tokens, account records, or absolute research paths.
    trades = [dict(symbol=t['symbol'], entry_date=t['entry_date'], exit_date=t['exit_date'],
                   net_pnl=t['net_pnl'], returnPct=100*t['net_pnl']/t['entry_cost'],
                   exit_reason=t['exit_reason']) for t in p['trades']]
    return dict(start=p['dates'][0], end=p['dates'][-1], equity=curve,
                metrics=dict(returnPct=p['return_pct'], cagrPct=p['cagr_pct'],
                             maxDrawdownPct=p['max_drawdown_pct'], sharpe=p['sharpe_zero_cash'],
                             completedTrades=p['closed_positions'], orderCount=p['turnover_orders'],
                             winRatePct=p['win_rate_pct'], exposurePct=p['average_exposure_pct'],
                             feesEquityPoints=p['fees_equity_points'], slippageEquityPoints=p['slippage_equity_points']),
                annualReturns=annual, trades=trades, assumptions=ASSUMPTIONS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    manifest_path = source/'papers-round5-2026-10-23/All-12-strategies.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    catalogue = []
    hashes = {}
    for s in manifest['strategies']:
        sid = s['id']
        p = source/s['folder']/f'Result-{sid}.json'
        hashes[sid] = hashlib.sha256(p.read_bytes()).hexdigest()
        data = json.loads(p.read_text(encoding='utf-8'))
        results = {period: export_period(data[period]) for period in ['training', 'ytd2026']}
        for period in ['training', 'ytd2026']:
            if abs(results[period]['metrics']['returnPct']-s[period]['return_pct']) > 1e-9:
                raise ValueError(f'Result mismatch: {sid}')
        results.update(dict(id=sid, dataCutoff=manifest['data_cutoff'], sourceSha256=hashes[sid],
                            evidence='Exploratory historical simulation', limitations=LIMITS))
        write(ROOT/'research/results'/f'{sid}.json', results)
        cfg = s['configuration']
        item = dict(id=sid, number=s['number'], title=s['name'], summary=s['steps'][1],
                    family=FAMILIES[sid], rebalance={1:'Monthly',3:'Quarterly',6:'Six-monthly'}[cfg['months']],
                    universe='Indian cash equities · current Nifty 500-derived panel', parameters=cfg,
                    configuration=cfg, rules=dict(entry=' '.join(s['steps']),
                    exit='Sell when removed at a review. No stop-loss or take-profit. Estimate terminal liquidation at final close.',
                    sizing=f"Up to {cfg['n']} stocks. Signal equity / {cfg['n']} per new position; fractional shares; retained positions are not resized.",
                    execution=ASSUMPTIONS[1]), limitations=[s['adaptation']]+LIMITS,
                    source=s['source'], download=f'downloads/{sid}.zip',
                    instruction_url=f'strategies/{sid}/SKILL.md', result_url=f'results/{sid}.json',
                    manifest_url=f'strategies/{sid}/strategy.json',
                    summary_metrics={k:results[k]['metrics'] for k in ['training','ytd2026']},
                    stress={k:s[k+'_stress'] for k in ['training','ytd2026']},
                    contributions2026=s['contributions_2026'][:3], dataCutoff=manifest['data_cutoff'])
        catalogue.append(item)
        write(ROOT/'strategies'/sid/'strategy.json', item)
        instructions = f'''---
name: {sid}
description: Reproduce the Indian {s['name']} portfolio backtest with user-authorised broker history and the frozen research rules.
---

# {s['name']}

Ask which broker the user uses: Zerodha, Dhan or FYERS, and which historical window to test. Ask FYERS users their plan. Explain missing history/entitlements before downloading. Do not request credentials in chat.

Download the complete [package](../../downloads/{sid}.zip). A SKILL.md link alone does not contain the executable files. Use Python 3.11+ and install `research/requirements.txt` into a local virtual environment. Read `broker/README.md` for current login and download commands.

Launch `python broker/broker_login.py`. The user enters credentials directly in its local browser form. Do not inspect, screenshot, log or read credential fields, browser storage, process memory or credential responses. Keep the helper alive. Pass its opaque session reference to the downloader; do not print access tokens. This avoids putting credentials in normal AI context, but is not isolation from a process with unrestricted local access.

Use an explicitly approved instrument mapping, including benchmark indices and industry labels when required. Download daily bars with the broker helper and its rate limits; retain the data manifest and quarantine. Never replace missing sessions or unavailable pre-listing history with fabricated prices. A refreshed current universe differs from the original study.

Run the frozen strategy:

```sh
python research/runner.py --strategy {sid} --data-dir YOUR_DATA --start 2018-01-01 --end 2025-12-31 --output results/{sid}
```

The selected configuration is `{cfg['id']}`. {' '.join(s['steps'])}

Read `research/README.md` for the shared settlement, sizing and cost rules. Preserve the reference defaults before experimenting. Deliver the run manifest, equity, trades, fees and differences from the saved result. A different broker snapshot is a replication, not an exact rerun.

The study uses today's universe, fractional shares and simplified charges. 2018–2025 influenced selection; 2026 has already been inspected. Do not call either an untouched holdout or imply live profits. This package downloads history and simulates trades; it does not place orders.

[Research source]({s['source']}) · [Recorded result](../../results/{sid}.json)
'''
        (ROOT/'strategies'/sid/'SKILL.md').write_text(instructions, encoding='utf-8')
    write(ROOT/'research/catalogue.json', catalogue)
    write(ROOT/'research/provenance.json', dict(dataCutoff=manifest['data_cutoff'],
          importedFrom='User-supplied 12-strategy research handoff',
          source='https://app.notion.com/p/4025c39e2b32816b9004f4510464b0ee',
          manifestSha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          resultSha256=hashes, parameterCombinations=sum(manifest['grids'].values()),
          publishedFields='Derived normalized equity, aggregate metrics, date/symbol/return trade summaries; no raw market-data cache.'))
    print(f'Imported {len(catalogue)} strategy records and derived result series.')


if __name__ == '__main__':
    main()
