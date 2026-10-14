---
name: hr-hr-helpdesk
description: Turn incoming HR requests into a prioritized case queue with sourced draft replies and clear owners.
---

# HR helpdesk triage

Convert a shared HR inbox or ticket export into an actionable queue while keeping confidential cases restricted.

## Inputs

Use authorized requests, existing case IDs, current policies, routing matrix, service standards, business calendar and timezone. Optional private `hr-context.md` supplies tone, response patterns and ownership rules. Request only information needed to resolve each case; sensitive records stay in restricted storage.

## Workflow

1. Identify the requested outcome and classify the case: policy question, record correction, leave, payroll, benefits, lifecycle task or sensitive employee relations. Match existing case IDs before creating new work; group duplicates without losing each requester's context.
2. Extract facts, dates and missing evidence. Calculate response targets only from the supplied service standard, working hours and timezone. Separate urgency stated by the requester from a verified deadline.
3. Route payroll discrepancies to payroll, policy exceptions to the policy owner and grievances, harassment, health or safety concerns to the designated restricted channel. Do not assess credibility, investigate or decide employment consequences.
4. Draft a direct reply in the HR team's approved style: answer supported by policy section/version, next action, owner and confirmed timeline. If information conflicts or is missing, state the gap and the single most useful clarification.
5. Update the queue using case ID and last-seen timestamp. Prepare drafts and escalation notes; do not send messages, disclose one employee's records to another, or close a case without resolution evidence.

## Deliver

`hr-queue.csv`: case_id, category, requested_outcome, owner, priority_reason, respond_by, policy_reference, next_action, status. Provide separately access-controlled reply drafts and restricted-case pointers.

## Check

Every request has one accountable owner; no unsupported deadline or public sensitive summary. Resolved cases include evidence, not merely a drafted reply.

## Try it

“Triage this week's HR inbox using our routing table and response standards. Draft concise replies and show which cases need payroll or confidential handling.”

Sources checked 2026-10-14: [ICO employment records guidance (UK)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/). Recheck applicable rules and provider documentation when used.
