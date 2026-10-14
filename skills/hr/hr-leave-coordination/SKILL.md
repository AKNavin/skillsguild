---
name: hr-leave-coordination
description: Check leave-request completeness, date conflicts and coverage needs before the authorized approver reviews it.
---

# Leave request coordination

Prepare a leave request for review and coordinate coverage without deciding entitlement.

## Inputs

Use request IDs, employee IDs, dates, partial-day units, work schedules, holiday calendar, balance as-of time, current policy and approver map. Optional private `hr-context.md` supplies channels and phrasing; `role-brief.md` can identify coverage dependencies. Keep medical explanations out of the shared coverage plan.

## Workflow

1. Normalize dates in the employee's work timezone. Preserve whether duration means hours, scheduled days or calendar days; do not count weekends or holidays without the applicable schedule and rule.
2. Match existing requests by provider request ID. Identify overlapping requests, canceled/superseded entries, missing fields and stale balance snapshots. A retrieved balance is evidence for the approver, not a guarantee of entitlement.
3. Compare the request with the supplied policy version and effective date. Show notice, documentation or balance exceptions as review items. Route statutory/protected leave and policy ambiguities to the designated HR specialist; do not infer medical status.
4. Prepare a coverage checklist from stated team commitments. Show conflicts without automatically favoring one employee, approving leave or changing schedules. Draft a focused request for the missing operational detail.
5. Record the approver's actual decision only when supplied. Re-read request state before proposing any update; stale or already-decided requests require reconciliation, not a duplicate submission. Do not send messages or mutate leave status automatically.

## Deliver

`leave-review.csv`: request_id, period, timezone, units, balance_as_of, policy_reference, exception, coverage_dependency, approver, next_action, status. Include private reply drafts and a separate minimal coverage calendar.

## Check

Requested units reconcile to the actual schedule. Shared outputs reveal availability, not diagnosis or confidential leave reasons.

## Try it

“Prepare next week's pending leave requests for review. Check overlaps against our shifts and holiday calendar; show coverage gaps without approving anything.”

Sources checked 2026-10-14: [BambooHR time off request API](https://documentation.bamboohr.com/reference/get-time-off-request). Recheck applicable rules and provider documentation when used.
