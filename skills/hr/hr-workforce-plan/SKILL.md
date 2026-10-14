---
name: hr-workforce-plan
description: Build a workforce capacity and headcount plan from business demand, current staffing and budget. Use for team-level planning, not individual redundancy selection.
---

# Workforce demand & capacity

## Inputs
Use the horizon, demand by period, current FTE, productive hours, planned leave, vacancies, known joiners/leavers, budget and hiring lead time. Read optional private `hr-context.md` and relevant `role-brief.md` for planning conventions. Missing productivity or demand assumptions stay visible; do not invent precision.

## Workflow
1. Separate approved demand from scenarios. Put volume, handling time and capacity in compatible units. For workload planning, calculate required FTE = workload hours / productive hours per FTE; state any service-level buffer separately.
2. Roll forward available capacity by period: opening FTE + confirmed joiners/transfers in - confirmed exits/transfers out. Apply ramp-up and availability once; do not subtract leave twice.
3. Compare baseline, lower-demand and higher-demand scenarios. If inputs are uncertain, show a range and the assumption driving it.
4. For each gap, compare hiring, upskilling, redeployment and process changes by cost, lead time and service impact. Account for recruitment cost and employer costs without equating annualised cost with in-period cash.
5. Work backwards from the required productive date to hiring approval and start dates. Treat suggested automation savings as unverified until measured. Make recommendations at role/team level, not about who should lose employment.

## Deliver
A table: `period | team/role | demand | required FTE | available FTE | gap | scenario | cost | source`; an assumption register; and an action queue with owner, approval dependency, start date and review trigger.

## Check
Totals reconcile to the opening workforce and budget; every gap has an action or explicit unresolved constraint. A vacancy and its incoming replacement never count twice.

Example: "Use our six-month support forecast and capacity sheet to show when we need to hire, train or rebalance work."

Sources: [CIPD workforce planning](https://www.cipd.org/uk/knowledge/factsheets/workforce-planning-factsheet/).

