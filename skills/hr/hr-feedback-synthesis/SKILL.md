---
name: hr-feedback-synthesis
description: Organize multi-source feedback into supported themes, examples and questions for a human review. Use for feedback, 360-review, evidence workflows.
---

# Feedback evidence digest

## Use
Use to summarize authorized peer, manager or self-feedback for a development conversation. This skill organizes evidence; it does not score or rank employees.

## Inputs
Feedback text with source IDs and dates, role criteria, review period and permitted audience. Use private `hr-context.md` for writing style and `role-brief.md` for relevant expectations. Confirm the intended anonymity or attribution rules.

## Do
1. Restrict records to the review period and remove duplicates. Keep an access-controlled source map rather than copying all raw comments into the summary.
2. Tag concrete observations by role criterion. Separate behavior, reported impact, opinion and unsupported inference. Preserve material counterexamples.
3. Group repeated observations without treating multiple copies or second-hand retellings as independent corroboration. State how many distinct sources support a theme.
4. Convert useful examples into “observed situation → behavior → reported effect.” If attribution would identify an anonymous respondent, paraphrase or withhold it according to the sharing rule.
5. Present strengths, development questions and disagreements with equal evidence standards. Do not derive personality, health, protected attributes or sentiment scores as performance measures.

## Deliver
`feedback-digest.md` with themes and discussion questions.
Restricted `evidence-map.csv`: theme_id, role_criterion, observation, source_ids, dates, evidence_type, counterevidence, uncertainty, permitted_audience.
Include excluded-item counts and reasons without unnecessary personal detail.

## Check
Each factual summary links to evidence; disagreement is visible; absence of feedback is not negative evidence. The digest contains no automated rating or employment recommendation.

## Example
“Summarize these 360 comments for a product manager's development discussion while preserving conflicting examples and reviewer anonymity.”

Sources: [CIPD performance feedback evidence review](https://www.cipd.org/uk/knowledge/evidence-reviews/performance-feedback) · [CIPD performance reviews](https://www.cipd.org/uk/knowledge/factsheets/appraisals-factsheet/). Checked 2026-10-14.
