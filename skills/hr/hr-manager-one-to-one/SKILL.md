---
name: hr-manager-one-to-one
description: Prepare focused check-ins and turn meeting notes into owned, dated follow-up actions. Use for managers, one-to-one, follow-up workflows.
---

# Manager one-to-one

## Use
Use before or after a manager–employee check-in. Build a useful conversation and reliable follow-through from supplied notes.

## Inputs
Meeting length, current goals, previous actions, employee topics and recent factual updates. Optional private `hr-context.md` supplies tone and meeting preferences; `role-brief.md` supplies expectations. Do not search private messages or infer mood to fill gaps.

## Do
1. Reconcile previous actions by stable action ID. Carry forward unfinished work with the reason; do not silently mark it complete or duplicate it.
2. Draft a time-boxed agenda starting with the employee's topics, followed by progress, obstacles, feedback and development. Keep status reporting brief when it already exists elsewhere.
3. For each concern, pair the observed example with an open question and possible support. Separate an observation from an interpretation; do not turn a check-in into an unannounced disciplinary script.
4. After notes arrive, extract only explicit decisions and commitments. Label suggestions as proposed, and identify unclear ownership or dates.
5. Prepare a concise recap in the HR's approved style. Sending it or creating calendar/tasks requires the user's existing authorization and named destination; otherwise return drafts.

## Deliver
`agenda.md` with minutes per topic and questions.
`actions.csv`: action_id, action, owner, due_date, source_note, status, blocker, next_check.
`recap.md` with agreed decisions, support and unresolved items.

## Check
Agenda fits the meeting. Each commitment is traceable to a note, and sensitive personal disclosures stay out of broad team updates.

## Example
“Prepare tomorrow's 25-minute check-in from these goals and last week's actions, then update the tracker from my meeting notes.”

Sources: [CIPD performance management](https://www.cipd.org/uk/knowledge/factsheets/performance-factsheet) · [CIPD performance feedback evidence review](https://www.cipd.org/uk/knowledge/evidence-reviews/performance-feedback). Checked 2026-10-14.
