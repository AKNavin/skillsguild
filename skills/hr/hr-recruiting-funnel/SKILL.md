---
name: hr-recruiting-funnel
description: Analyse an ATS export or stage-event log to explain recruitment throughput, delays and process bottlenecks. Use for aggregate operations reporting, not candidate selection.
---

# Recruiting funnel & bottlenecks

## Inputs
Use authorised ATS exports, report dates, timezone, stage definitions and a reporting cutoff. Read optional private `hr-context.md` for metrics conventions and relevant `role-brief.md` for role-specific stages. Prefer pseudonymous application IDs.

## Workflow
1. Define a cohort and unit of analysis: an application to one role, not a unique person across all roles. Deduplicate events; log invalid timestamps, unknown stages and missing IDs.
2. Distinguish period activity, current pipeline stock and cohort conversion. Do not divide outcomes from one cohort by entrants from another.
3. Reconstruct actual stage visits. Specify treatment of skips, re-entry, withdrawals and merged applications. Some ATS reports infer skipped stages; disclose that difference when reconciling exports.
4. Report entrants, progressed, withdrawn, closed and still-open applications. For resolved conversion use progressed / resolved stage exits; for cohort-to-date conversion use progressed / entrants and label it incomplete. Report zero denominators as unavailable.
5. Measure median/p75 elapsed time for completed stage visits separately from age of still-open visits at cutoff. Define time-to-fill, time-to-hire and offer acceptance using explicit start/end events rather than assumed universal definitions.
6. Identify process bottlenecks and assign actions with owners and review dates. Do not infer applicant quality or recommend employment decisions from speed, source or missing data.

## Deliver
A metric dictionary, reconciled funnel table, open-age queue, data-quality log and three evidence-backed process actions. Use role/source aggregates only when cohort sizes support interpretation; restrict row-level details to authorised users.

## Check
Counts reconcile to distinct applications and stage transitions. Pending offers are not counted as rejected; open durations are not silently dropped from the delay story.

Example: "Analyse this quarterly ATS export and show where candidates wait longest, with formulas and a recruiter action list."

Sources: [Greenhouse pipeline history and pass-through rates](https://support.greenhouse.io/hc/en-us/articles/204636795-Pipeline-history-and-pass-through-rates-report).

