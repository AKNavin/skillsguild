# Payroll line CSV contract

Both files must use this exact UTF-8 header and column order:

```csv
entity,period,employee_id,currency,component,amount
DEMO,2026-10,EMP001,INR,BASIC,50000.00
DEMO,2026-10,EMP001,INR,DEDUCTION,-1200.00
```

All examples and bundled fixtures are fictional. This is an intermediate comparison format, not an EPFO, ESIC, tax, bank or payroll-provider upload format.

- `entity`, `employee_id`, `component`: case-sensitive stable tokens; 1–80 ASCII letters/digits or `._:-`, starting with a letter/digit. No names or sensitive identifiers are required.
- `period`: valid `YYYY-MM`, year 0001–9999. Both files must represent comparable period definitions; the helper cannot detect whether one exporter uses payment month and another earned month.
- `currency`: three uppercase letters. Validate the actual ISO currency against your source schema; this helper checks its shape only. Totals are separated by currency; there is no FX conversion.
- `amount`: signed fixed-point decimal, at most 12 integer digits and two fractional digits. Positive earnings, negative deductions/reversals, zero allowed. No separators, whitespace, exponents, leading plus, NaN or infinity. Normalize source precision and sign conventions using approved rules first. Currencies requiring more than two decimal places are outside this helper's scope.

The unique key is `(entity, period, employee_id, currency, component)`. If a component has multiple approved sub-lines, supply distinct source-supported component tokens. Duplicate keys are rejected; no implicit aggregation or deduplication occurs. Blank cells, extra columns and malformed dates are rejected. An omitted row differs from a zero-valued row.

`delta = actual - expected`. `missing` and `unexpected` remain exceptions regardless of tolerance. `changed` means an absolute delta above tolerance. `within_tolerance` remains visible, distinct from exact `matched`. Both empty files produce `has_records: false`, not proof of a completed payroll. Check the source scope and counts independently.

Run locally:

```sh
python -B scripts/reconcile.py fixtures/expected.csv fixtures/actual.csv --tolerance 0.00
python -B -m unittest discover -s tests
```

Valid input exits 0 even when differences exist; inspect `unresolved_count`. Invalid input exits 2 and emits no partial JSON. JSON includes source SHA-256 hashes, line counts, status counts, per-currency totals and every line. Save it only in approved private storage. The script performs no network calls, external writes, eligibility decisions or money movement. Re-running the same inputs produces identical output.
