---
name: hr-compensation-review
description: Reconcile salary data, approved bands and budgets into a private decision pack for reviewers. Use for compensation, salary-bands, pay-review workflows.
---

# Pay review preparation

## Use
Use to prepare a compensation-review pack from approved rules and proposals. Calculate and flag exceptions; do not choose individual awards, invent market rates or submit payroll changes.

## Inputs
Restricted pay roster, effective date, currency, pay frequency, FTE, approved band table, eligibility, budget and human-proposed changes. Optional private `hr-context.md` supplies review format. Require stable employee IDs and a stated definition of base versus variable pay.

## Do
1. Validate IDs, units, currency and effective dates. Align salary and band to the same annualized, FTE basis using supplied rules. Never combine currencies without an approved exchange-rate date.
2. Calculate compa-ratio as normalized base divided by band midpoint; range position as (base − minimum)/(maximum − minimum). Flag invalid or zero-width bands and missing mappings instead of dividing blindly.
3. Cost supplied proposals: base change, annualized cost and in-period cost using the approved proration convention. Apply employer on-costs only when rates and scope are supplied.
4. Reconcile totals to the authorized budget and flag ineligible, out-of-band or incomplete proposals. Do not optimize employee awards or use inferred protected traits.
5. Prepare reviewer questions and an audit trail of inputs, formulas and assumptions. Any pay-equity review requires its separately authorized data and method.
6. Record human-approved decisions in a separate output; keep proposals, approvals and payroll handoff distinct.

## Deliver
Restricted `pay-review.csv`: employee_id, currency, normalized_base, band_id, minimum, midpoint, maximum, compa_ratio, range_position, proposed_change, annual_cost, period_cost, exception, approver, decision_status.
Add reconciliation and the decision queue.

## Check
Detail sums to totals; sample formulas reconcile; missing units block affected rows. The pack contains no AI-generated award or payment instruction.

## Example
“Prepare our annual pay-review pack from these approved bands and manager proposals, showing the budget gap and exceptions.”

Sources: [CIPD pay structures and pay progression](https://www.cipd.org/uk/knowledge/factsheets/pay-structures-factsheet/) · [CIPD reward introduction](https://www.cipd.org/uk/knowledge/factsheets/reward-factsheet/). Checked 2026-10-14.
