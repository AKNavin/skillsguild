---
name: hr-offboarding
description: Build a timed exit checklist covering handover, assets, access and payroll handoffs with evidence of completion.
---

# Offboarding coordination

Coordinate a confirmed exit without taking termination, access-deletion or final-pay decisions.

## Inputs

Use the authorized exit record, employee ID, last working date, employment end date, access cutoff/timezone, approved policy, jurisdiction, legal-hold instructions and owner list. Optional private `hr-context.md` supplies tone and channels; `role-brief.md` identifies handover scope. Keep exit reasons restricted unless disclosure is authorized.

## Workflow

1. Reconcile the three dates: last work, contractual end and access cutoff. Do not treat them as interchangeable. If dates or approvals conflict, flag the specific dependency before drafting downstream changes.
2. Create handover tasks for responsibilities, open work, files and stakeholder contacts with receiving owners and acceptance evidence. Inventory assets by identifier and return status; do not assume an unreturned item permits a deduction.
3. Prepare access change requests for the authorized IT owner, including service accounts, shared resources and ownership transfer. Sequence business continuity and approved access cutoff explicitly. Never delete accounts or records automatically; preserve legal holds and retention rules.
4. Prepare payroll/benefit notifications from approved facts, separately listing unresolved leave, reimbursement or final-settlement inputs. Do not calculate or approve statutory entitlement, deductions or termination terms without the responsible specialist's rules and authorization.
5. Track `employee_id + exit_id + task_type` so reruns update existing tasks. Draft respectful communications and reconcile each owner's completion evidence after cutoff; a request sent is not task completion.

## Deliver

`exit-checklist.csv`: task_key, task, owner, due_at_with_timezone, dependency, evidence, status, blocker. Add handover summary and restricted payroll/access request drafts.

## Check

No dangling work owner, unverified access completion or undocumented retention action. The report distinguishes pending, requested and verified complete.

## Try it

“Prepare this confirmed employee exit for Friday. Separate last-working and access cutoff times, track assets and give payroll a factual handoff.”

Sources checked 2026-10-14: [ICO employment records guidance (UK)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/) · [BambooHR employee records API](https://documentation.bamboohr.com/reference/get-employee). Recheck applicable rules and provider documentation when used.
