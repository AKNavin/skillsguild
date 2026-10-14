---
name: hr-attendance-exceptions
description: Find missing punches, overlapping entries and schedule mismatches for factual review before payroll.
---

# Attendance exception review

Produce a factual attendance exception queue, keeping payroll and conduct decisions with their owners.

## Inputs

Use minimum-field time entries, stable employee/entry IDs, cutoff time, work schedules/timezones, approved leave and the applicable break, rounding and overtime rules. Optional private `hr-context.md` supplies terminology and reviewer routing. A schedule gap alone is not evidence of misconduct.

## Workflow

1. Preserve raw entries and export timestamps. Convert timezone-aware instants consistently; handle overnight shifts and daylight-saving changes without splitting or duplicating time. Mark ambiguous local timestamps for clarification.
2. Check missing clock-out/in, overlapping entries, duplicate entry IDs, reversed intervals and entries beyond the export cutoff. Separate open current shifts from genuinely incomplete historical records.
3. Compare with scheduled work, approved leave and holidays. Apply only supplied rounding/break rules, recording the rule version. Flag apparent overtime for review; do not decide overtime eligibility, wage deductions or attendance penalties.
4. Deduplicate the queue using `employee_id + entry_id + exception_type`. Record observed facts, expected data, owner and the smallest correction request. Never fabricate a punch to make totals agree.
5. Prepare proposed corrections with before/after values and evidence; retain original records. Draft employee/manager clarification messages without sending. Reconcile reviewed changes against a fresh export before handing totals to payroll.

## Deliver

`attendance-exceptions.csv`: exception_key, employee_id, entry_id, local_work_date, timezone, issue, observed_duration, rule_reference, evidence, owner, status. Include totals by confirmed, unresolved and out-of-scope hours; keep sensitive leave details separate.

## Check

No overlap is counted twice; overnight work stays attributable to the correct shift. Unknown hours are visible, not silently zeroed.

## Try it

“Review these October timesheets before payroll cutoff. Our support team works overnight shifts; show missing punches and overlaps with correction requests.”

Sources checked 2026-10-14: [BambooHR time tracking API](https://documentation.bamboohr.com/reference/time-tracking). Recheck applicable rules and provider documentation when used.
