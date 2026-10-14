---
name: hr-engagement-survey
description: Design a short survey with clear purpose, privacy rules and a usable analysis plan. Use for survey, employee-voice, pulse workflows.
---

# Employee pulse survey

## Use
Use to design a short employee pulse or climate survey that informs a defined action. This creates the instrument and runbook, not an unapproved survey launch.

## Inputs
Decision to inform, audience, collection platform, previous questions, planned reporting groups and approved privacy rules. Read private `hr-context.md` for tone. Establish who can access raw responses, retention and minimum reporting group size before launch.

## Do
1. Select a few dimensions relevant to the decision, such as clarity, tools, manager support or workload. Ask one thing per item, with a stated recall period.
2. Draft neutral questions using a consistent scale, labeled endpoints and a not-applicable option. Add at most a small number of optional free-text prompts.
3. For trend measurement, preserve prior wording and scale; mark changed items as non-comparable. Adapted questions are not automatically a validated instrument.
4. Explain purpose, voluntary participation, data use and actual confidentiality limits. Do not promise anonymity if identifiers, small groups or comments can reveal a person.
5. Specify aggregation, missing-answer treatment, reporting suppression and response-rate denominators. Avoid unnecessary demographics and combining breakdowns that could identify individuals.
6. Create invitation, reminder and results-sharing drafts with owners and dates. Suppression thresholds need privacy-owner approval; do not invent a universal safe number.

## Deliver
`survey.csv`: item_id, dimension, question, response_scale, optional, recall_period, trend_comparable.
`survey-runbook.md`: audience, dates, privacy notice, access, retention, suppression, analysis and communication plan.

## Check
Each question informs an action; no double-barreled items, unsupported anonymity claim or identifiable small-group output remains.

## Example
“Draft a six-question workload pulse for our operations team, plus the privacy notice and reporting plan.”

Sources: [OPM FEVS organizational climate framework](https://www.opm.gov/fevs/about/) · [ICO keeping employment records](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/). Checked 2026-10-14.
