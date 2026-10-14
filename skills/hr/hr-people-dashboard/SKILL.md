---
name: hr-people-dashboard
description: Create reconciled headcount, hiring and turnover metrics with clear denominators and privacy limits.
---

# Build an HR metrics dashboard

Produce a decision-focused dashboard from authorised HR exports. Inputs: question, reporting dates, roster/events, data dictionary and optional `hr-context.md`. Use aggregated metrics; do not produce individual flight-risk or performance scores.

## Calculate
1. Fix definitions before calculating: person versus assignment, employee versus contractor, active status, join/exit effective-day convention, entity and time zone. Retain the extraction timestamp and filters.
2. Count opening and closing headcount from snapshots under the stated convention. Reconcile opening + joins − exits ± scope transfers/corrections = closing. Show unexplained differences rather than adjusting them away.
3. Compute turnover using a disclosed denominator (for example period exits / mean opening and closing headcount); split voluntary/involuntary only when source-coded. Zero denominators return unavailable. Do not annualise silently or compare unequal periods as equivalent.
4. For hiring, distinguish applications, unique candidates and requisitions; calculate time-to-fill from the agreed start/end events. Unfilled roles remain open/censored instead of receiving zero duration.
5. Apply an organisation-approved minimum group size and complementary suppression so totals cannot reveal suppressed cells. Avoid identifiable free text and intersecting filters; if no sharing policy exists, keep the detailed view private for review.

## Deliver
A small dashboard and metric dictionary: `metric | period | numerator | denominator | filters | value | prior-comparable-value | caveat`. Add reconciliation, source completeness and two or three questions the evidence supports. Label hypotheses separately from findings; correlation is not a cause.

**Check:** reproduce every displayed figure from the supplied data and explain reconciliations, exclusions and missing values.

**Try:** “Build a monthly headcount and turnover dashboard from these snapshots and events; reconcile it and suppress small-team results.”

Sources: [CIPD People analytics](https://www.cipd.org/en/topics/people-analytics/) · [ICO collecting and keeping employment records (UK)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/collecting-and-keeping-employment-records/). Checked 2026-10-14.
