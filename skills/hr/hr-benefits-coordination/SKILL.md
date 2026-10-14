---
name: hr-benefits-coordination
description: Prepare benefit change requests and reconcile their status across HRIS, provider and payroll records.
---

# Benefits enrollment coordination

Coordinate an approved benefits request through its operational checkpoints without choosing coverage for an employee.

## Inputs

Use the employee's requested change, approved plan documents, applicable jurisdiction, event/effective dates, authorized eligibility decision, submission window and HRIS/provider/payroll snapshots. Optional private `hr-context.md` supplies tone and owner routing. Keep dependent identities and health evidence out of general trackers.

## Workflow

1. Separate the employee's request, eligibility confirmation, enrollment submission, provider acceptance and payroll deduction start. They are distinct states; one does not prove the next.
2. Check required fields and documentary references against the current plan version. Verify deadline and timezone with the plan administrator; do not infer eligibility, coverage, tax treatment or entitlement from age, job title or a past plan.
3. Compare current and scheduled-future records separately using `employee_id + plan_id + effective_date + request_id`. BambooHR can omit future records when access is restricted; missing data must not be interpreted as absence of coverage.
4. Prepare an exception queue for unmatched plans, dates, enrollment status or supplied contribution amounts. Do not auto-select a plan, change beneficiaries or alter deductions. Draft a concise explanation of the next required action in the HR team's style.
5. Reconcile the approved request against provider acknowledgment and payroll's confirmed deduction schedule. Record as-of times and evidence for each state; reuse the same request key on reruns and investigate ambiguous submission outcomes before any repeat attempt.

## Deliver

`benefit-cases.csv`: request_key, plan_reference, event_date, effective_date, deadline, eligibility_owner, enrollment_state, provider_reference, payroll_state, exception, next_owner. Include private draft correspondence and missing-information list.

## Check

“Submitted” is never reported as “covered.” No personal dependent or medical details enter public artefacts or broad team summaries.

## Try it

“Reconcile these approved benefit changes against our HRIS and provider report. Show unconfirmed coverage dates and payroll handoff gaps.”

Sources checked 2026-10-14: [BambooHR employee benefits API](https://documentation.bamboohr.com/reference/list-employee-benefits). Recheck applicable rules and provider documentation when used.
