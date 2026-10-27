"""Compare portable runs with the user's original study files, without copying prices.

Optional local audit: python tests/replay_handoff.py --study-dir PATH --output PATH
The supplied original handoff and private daily panel must already be available.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import engine
from panel import load_panel, validate_window
from runner import frozen_strategies, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    study = args.study_dir.resolve()
    folders = ['papers-momentum-2026-10-22', 'papers-round2-2026-10-23', 'papers-round3-2026-10-23', 'papers-round4-2026-10-23', 'papers-round5-2026-10-23', 'papers-round6-2026-10-27']
    p, audit, data = load_panel(study / folders[0], study / 'rl-breakout-2026-10-17' / 'Data-quality-quarantine.json')
    comparisons = []
    for key, definition in frozen_strategies().items():
        config = definition['configuration']
        expected_file = study / folders[definition['round'] - 1] / ('Result-' + key + '.json')
        expected = json.loads(expected_file.read_text(encoding='utf-8'))
        for label, start, end in [('training', '2018-01-01', '2025-12-31'), ('ytd2026', '2026-01-01', '2026-10-22')]:
            validate_window(p, config, start, end)
            for stress in [False, True]:
                suffix = ('_double_slippage' if definition['round'] == 1 else '_stress') if stress else ''
                original = expected[label + suffix]
                actual = engine.run(p, {}, config, start, end, slip=.001 if stress else .0005,
                                    avoid_locked=stress and definition['round'] > 1, detail=True)
                failed = [field for field, value in original.items() if actual.get(field) != value]
                equity_diff = max((abs(a - b) for a, b in zip(actual['equity'], original.get('equity', actual['equity']))), default=0)
                row = {'strategy': key, 'period': label, 'stress': stress,
                       'source_report_sha256': hashlib.sha256(expected_file.read_bytes()).hexdigest(),
                       'compared_fields': list(original), 'exact_match': not failed, 'mismatched_fields': failed,
                       'maximum_absolute_equity_difference': equity_diff,
                       'accounting_residual': actual['accounting_residual']}
                comparisons.append(row)
                print(f"{key} {label}{suffix}: {'PASS' if not failed else 'FAIL ' + ','.join(failed)}", flush=True)
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'runs': len(comparisons),
              'passed': sum(row['exact_match'] for row in comparisons),
              'dataset_sha256': data['sha256'], 'stocks': audit['stocks'],
              'calendar_first': audit['calendar_first'], 'calendar_last': audit['calendar_last'],
              'note': 'Exact parity against supplied historical reports verifies portability, not data quality, unbiased research or future performance.',
              'comparisons': comparisons}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, report)
    return 0 if report['passed'] == report['runs'] else 1


if __name__ == '__main__':
    sys.exit(main())
