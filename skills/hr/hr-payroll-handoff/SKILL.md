---
name: hr-payroll-handoff
description: Package approved payroll changes with effective dates, evidence and control totals for the payroll team.
---

# Payroll input handoff

Turn approved HR changes into a controlled payroll input pack, without inventing pay calculations.

## Inputs

Use pay period, legal entity, currency, cutoff with timezone, payroll schema, approved codes, prior batch manifest and authorized joiner/leaver, pay-change, attendance and reimbursement inputs. Optional private `hr-context.md` supplies owners and cutoff conventions. Keep bank, tax and identity data in the restricted payroll system, not the general handoff summary.

## Workflow

1. Freeze source snapshots and separate approved inputs from pending requests. Record approval reference, effective date and the affected pay period for each change. A manager's draft request is not an approved pay change.
2. Map only to supplied earning/deduction codes. Check stable employee IDs, currency, units, duplicate changes, out-of-period dates and missing authorizations. Distinguish arrears, reversals and regular items without assuming their tax treatment.
3. Calculate count and amount control totals per entity/currency/code using decimal arithmetic. Do not combine currencies. Surface attendance uncertainty and proration questions for the payroll owner instead of choosing a rule.
4. Compare request keys with the previous handoff; use `employee_id + change_type + effective_date + approval_id`. Mark already-submitted, changed-after-cutoff and replacement items explicitly so a rerun cannot double count.
5. Produce the accepted input file and a separate exception register. For India statutory items, verify current EPFO/ESIC and tax instructions with the responsible specialist; do not embed assumed contribution rates, deadlines or eligibility.

## Deliver

Handoff CSV plus manifest: batch_id, period, cutoff, source_hashes, record_count, control_totals, approver, unresolved_count. Exceptions include owner and required resolution.

## Check

All exported changes are authorized, schema-valid and accounted for once. Payroll payment, statutory filing and deductions remain outside this preparation task.

## Try it

“Prepare October payroll inputs from these approved changes. Separate late items, prevent duplicates from the prior batch and give payroll control totals.”

Sources checked 2026-10-14: [BambooHR time tracking API](https://documentation.bamboohr.com/reference/time-tracking) · [EPFO official employer portal (India)](https://unifiedportal-emp.epfindia.gov.in/epfo/). Recheck applicable rules and provider documentation when used.
