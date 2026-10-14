---
name: hr-interview-scheduling
description: Coordinate interview availability, panel constraints and candidate confirmations. Use to propose or execute specifically authorised scheduling actions.
---

# Interview scheduling coordinator

## Inputs
Use availability, named timezones, meeting duration, buffers, panel roles, stage sequence and date limits. Optional private `hr-context.md` supplies scheduling conventions; `role-brief.md` identifies the interview plan. Calendar access alone is not permission to send invitations.

## Workflow
1. Normalise availability to specific dates and IANA timezones; clarify ambiguous abbreviations. Compute offsets for the actual interview date, including daylight-saving changes.
2. Intersect candidate and required panel availability, working-hour preferences, room/video constraints and buffers. Respect requested adjustments. Offer a small set of feasible options in both candidate and organiser local time.
3. If no option works, identify the blocking constraint and propose an alternative panel member or date window for the owner. Do not silently remove a required interviewer.
4. Prepare a candidate confirmation containing role, duration, stage, named timezone, format/link, preparation and contact. Keep private evaluator notes and other candidate identities out of invitations.
5. With explicit authorization covering recipients and content, recheck availability immediately before creating or changing events. Record event IDs and responses; distinguish a hold, sent invitation and accepted meeting. On retry, reconcile existing IDs before creating duplicates. Without authorization, deliver the plan and drafts.

## Deliver
`interview_id | stage | candidate_id | panel | start_UTC | local times/timezones | duration | location/link | status | event_id`, plus confirmations and an exception queue. For rescheduling, identify the exact event and notify only authorised recipients.

## Check
No overlap, timezone ambiguity or missing required attendee remains. Exported times match invitation text; a failed send is never reported as booked.

Example: "Find three 45-minute slots next week for this candidate in India and this panel in London, and draft the confirmation."

Sources: [Greenhouse scheduling between timezones](https://support.greenhouse.io/hc/en-us/articles/360000157052-Scheduling-between-timezones) · [Greenhouse scheduling for daylight saving time](https://support.greenhouse.io/hc/en-us/articles/360049635452-Scheduling-for-Daylight-Saving-Time).

