---
name: hr-engagement-actions
description: Turn aggregate employee feedback into a few owned actions and a progress update people can use. Use for engagement, action-plan, survey-results workflows.
---

# Survey-to-action plan

## Use
Use after an employee survey to turn findings into a focused action plan. Work with approved aggregate results; do not profile individual employees.

## Inputs
Question-level counts and scores, response denominator, prior comparable results, permitted comments, reporting threshold and business context. Optional private `hr-context.md` provides voice and update cadence.

## Do
1. Reconcile counts, scales, missing answers and response rates. Enforce the approved minimum group size and check whether combined breakdowns or comments reveal individuals.
2. Distinguish a result from a hypothesis about its cause. Flag changes in sample, question wording or scale before comparing periods. Low participation limits interpretation; it does not prove satisfaction or disengagement.
3. Identify a small number of themes using size, business relevance and feasibility, explaining the choice. Preserve contrary evidence and avoid untested claims that one score caused turnover.
4. Propose a validation conversation where the cause is unclear, using neutral prompts. Do not expose raw comments to managers if access rules prohibit it.
5. Turn selected themes into bounded actions with one owner, first step, resources, date and an observable outcome. Limit the plan to what can be delivered.
6. Produce a “You said / We will / By when” update and a progress log. Compare follow-up evidence without claiming an experiment proved causality.

## Deliver
`engagement-actions.csv`: theme, aggregate_evidence, limitation, hypothesis, validation_step, action, owner, due_date, success_measure, status.
Add the employee update and leadership decision requests.

## Check
Each action has evidence and an owner; suppressed groups remain suppressed, and unfinished previous commitments are visible.

## Example
“Turn these pulse results into three feasible actions and a plain-language employee update, preserving the small-team reporting threshold.”

Sources: [OPM understanding employee survey results](https://www.opm.gov/fevs/reports/understanding-results/). Checked 2026-10-14.
