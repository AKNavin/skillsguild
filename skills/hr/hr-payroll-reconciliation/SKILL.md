---
name: hr-payroll-reconciliation
description: Compare approved payroll lines with a processed register and explain missing, changed and unexpected amounts.
---

# Payroll variance check

Reconcile approved inputs against a payroll register before an authorized payroll owner acts.

## Inputs

Use expected and actual extracts from the same entity/pay period, code mapping, currency, approved adjustments and explicit monetary tolerance. Optional private `hr-context.md` supplies owner routing and report style. Work locally with minimal employee IDs; no names, bank details or tax identifiers are needed.

## Workflow

1. Freeze both snapshots with source hashes and export times. Normalize each to the schema in [references/csv-format.md](references/csv-format.md). Validate period, currency, signed-amount convention and component codes. Never aggregate away duplicate keys.
2. Run `python -B scripts/reconcile.py expected.csv actual.csv --tolerance 0.00 > reconciliation.json` from this skill folder. The stdlib-only helper reads files and writes JSON to stdout; it does not contact payroll or move money.
3. Review missing, unexpected and changed rows by employee and component, then compare totals per entity/period/currency. A matching grand total does not clear offsetting employee errors. Missing lines remain exceptions even when their value is zero.
4. Trace each difference to its approval, effective date, rounding rule or source gap. Distinguish planned adjustments from unverified explanations. Do not change rates, calculate legal entitlement or decide deductions from a variance report.
5. Assign owners, retain original evidence and rerun after a fresh corrected export. Use the source hashes as the reconciliation run identity; do not mark resolved because a draft correction exists.

## Deliver

The JSON reconciliation plus an exception table: line_key, status, expected, actual, delta, explanation_reference, owner, resolution_status. Summarize unresolved counts and currency-specific control totals.

## Check

Zero unresolved variances is an arithmetic result, not payment approval or statutory compliance. Verify jurisdiction-specific filing rules separately with the payroll owner.

## Try it

“Compare these approved and processed October payroll CSVs using zero tolerance. Explain exceptions and prepare an owner-assigned correction queue without changing payroll.”

Sources checked 2026-10-14: [EPFO official employer portal (India)](https://unifiedportal-emp.epfindia.gov.in/epfo/) · [ESIC monthly contribution workflow (India)](https://portal.esic.gov.in/InsuranceGlobalWebV4/ESICInsurancePortal/Documents/consolidated_mc_%26_edit_mc_helpfile.pdf). Recheck applicable rules and provider documentation when used.
