---
name: hr-review-cycle
description: Set up review calendars, evidence prompts, completion tracking and exception follow-ups. Use for reviews, review-cycle, operations workflows.
---

# Performance review cycle

## Use
Use to launch or coordinate a performance-review cycle. Automate preparation and tracking while reviewers remain responsible for assessments and outcomes.

## Inputs
Approved policy and templates, cycle dates, roster, reporting lines, eligibility rules and working calendar. Optional private `hr-context.md` supplies reminder tone, timezone and escalation preferences. Do not invent rating definitions when the policy has none.

## Do
1. Validate employee IDs, managers, duplicate records and eligibility as of the cycle's cutoff. Place ambiguous or missing assignments in an exception queue.
2. Work backward from completion to self-review, feedback collection, manager review, calibration and discussion milestones, using only applicable stages.
3. Prepare role-relevant evidence prompts covering the whole period. Include changed goals, resources, results and employee comments so recency alone does not drive the review.
4. Create a tracker with stable review IDs. A submitted form, completed discussion and employee acknowledgement are separate events; acknowledgement is not agreement.
5. Draft reminders only for outstanding actions, deduplicated by review ID and stage. Show recipients and content before any unapproved send; retain delivery results when sending is authorized.
6. Produce an exceptions summary and the next operational step. Do not automatically finalize ratings or alter HRIS records.

## Deliver
`review-cycle.csv`: review_id, employee_id, manager_id, stage, owner, due_date, completed_at, blocker, next_action.
Add the schedule, review prompts and reminder drafts.

## Check
Every eligible employee has one owner and complete stage dates. Excluded records have reasons, reminders target only incomplete stages, and confidential review content stays restricted.

## Example
“Set up our November review cycle for this roster, flag missing managers and draft next week's overdue reminders.”

Sources: [CIPD performance reviews](https://www.cipd.org/uk/knowledge/factsheets/appraisals-factsheet/). Checked 2026-10-14.
