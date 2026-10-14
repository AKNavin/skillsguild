---
name: hr-preboarding
description: Turn an accepted offer into an owner-assigned readiness checklist and a clear first-day brief.
---

# New-starter preboarding

Prepare everything a confirmed starter needs before arrival, with visible owners and blockers.

## Inputs

Use the accepted offer, employment type, confirmed start date, working location/timezone, manager, equipment/access requirements, approved checks and existing task tracker. Optional private `hr-context.md` supplies tone, channels and service standards; `role-brief.md` supplies role-specific needs. Do not collect identity, bank or medical documents in the plan; link to approved secure intake.

## Workflow

1. Reconcile the start date and location across the offer and tracker. Mark conflicts as blockers; retain the original source and last-confirmed timestamp.
2. Work backward from arrival using the supplied business calendar. Create only applicable tasks: contract status, required checks, secure records intake, equipment, access, manager/buddy readiness and first-day logistics. Separate employment checks from onboarding convenience tasks.
3. Set an owner, dependency and evidence of completion for every task. Use `starter_id + start_date + task_type` as the request key and merge existing tasks so reruns do not duplicate them.
4. Draft a concise welcome message in the HR team's approved style: when and where to arrive, contact, agenda, accessibility contact and outstanding actions. Never invent portal links or promise unconfirmed equipment.
5. Flag overdue critical dependencies and propose the smallest unblock action. Prepare provisioning requests; do not create accounts or send messages automatically.

## Deliver

`preboarding.csv`: request_key, task, owner, due_at_with_timezone, dependency, status, evidence_link, blocker. Include a first-day brief and a ready/blocked summary.

## Check

No duplicate task keys; every critical task has an owner and verified completion or a named blocker. A pending background check is not a hiring decision.

## Try it

“Prepare preboarding for our remote analyst starting 2 November in Asia/Kolkata. Use the accepted offer and current IT tracker; give me the missing actions and a welcome draft.”

Sources checked 2026-10-14: [CIPD employee induction](https://prod.cipd.org/en/knowledge/guides/employee-induction/). Recheck applicable rules and provider documentation when used.
