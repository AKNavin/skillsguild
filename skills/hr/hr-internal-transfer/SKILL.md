---
name: hr-internal-transfer
description: Coordinate an approved role move across managers, HRIS, payroll and access with one effective-date plan.
---

# Internal transfer handoff

Turn an already approved transfer into a coordinated transition, preserving employment history and clear ownership.

## Inputs

Use the authorized transfer request, stable employee ID, effective date/timezone, current and destination role/team/location, agreed pay changes, managers and system owners. Optional private `role-brief.md` defines the destination outcomes; `hr-context.md` supplies style and operating cadence. Do not decide promotion, pay or transfer eligibility.

## Workflow

1. Reconcile the effective date across approval, manager plans, payroll cutoff and HRIS. Separate role, reporting line, cost centre, location and pay components; each may have a different authorized date or owner.
2. Map work to hand over: responsibilities, open commitments, documents, client/team contacts and acceptance criteria. Assign both outgoing and incoming owners; do not assume the move ends existing access or employment.
3. Prepare field-level HRIS change requests with before/after values and source references. Preserve historical rows and distinguish scheduled future changes from currently effective records.
4. Prepare access review and destination onboarding tasks. Request only the role permissions actually required, with temporary overlap expiry where supplied. Do not grant/revoke access, change compensation or send announcements automatically.
5. Track tasks using `employee_id + transfer_id + task_type`. Reconcile owner confirmations after the effective date; leave mismatches open. Draft a concise employee/manager handoff in the approved HR style, sharing only relevant operational details.

## Deliver

`transfer-plan.csv`: task_key, change_or_handover, before_reference, after_reference, effective_at, owner, dependency, evidence, status. Add destination first-week priorities and an exception list for inconsistent system dates.

## Check

Every responsibility has a receiving owner. Future changes do not overwrite current records early, and approvals exist for each pay or contract change.

## Try it

“Coordinate this approved support-to-product transfer. Reconcile the manager, payroll and HRIS dates and create a handover plus role-specific first-week plan.”

Sources checked 2026-10-14: [BambooHR employee records API](https://documentation.bamboohr.com/reference/get-employee) · [CIPD employee induction](https://prod.cipd.org/en/knowledge/guides/employee-induction/). Recheck applicable rules and provider documentation when used.
