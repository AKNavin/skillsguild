---
name: hr-succession-planning
description: Map critical-role coverage, documented capability gaps and development actions without predicting departures. Use for succession, continuity, critical-roles workflows.
---

# Succession coverage plan

## Use
Use to prepare a business-continuity and talent-development discussion for critical roles. Do not predict individual departures, rank “potential” or choose successors.

## Inputs
Critical-role list, responsibilities, continuity requirements, authorized capability evidence and employee-stated career interests. Optional private `hr-context.md` supplies planning rules; `role-brief.md` supplies target scope. Human reviewers define criticality and any approved readiness labels.

## Do
1. Map roles to the work that would be interrupted by a vacancy. Identify essential knowledge, access, approvals and near-term coverage requirements.
2. Separate emergency coverage from longer-term development. A backup who can cover a process is not automatically ready for the full role.
3. For the approved talent pool, organize factual evidence against published role requirements. Mark missing evidence and record interest only when explicitly supplied.
4. Preserve human-assessed readiness with assessor and date; never generate individual readiness or flight-risk scores. Do not infer willingness to move from family circumstances or other protected attributes.
5. Propose cross-training, documentation, shadowing and stretch assignments tied to specific capability gaps. Record capacity, access boundaries and sponsors.
6. Create a quarterly review agenda and a restricted decision log. Keep succession discussion distinct from any promise of appointment or pay.

## Deliver
`coverage-map.csv`: role_id, critical_work, vacancy_impact, emergency_coverage, knowledge_dependency, coverage_gap, owner.
Restricted `development-actions.csv`: person_id, role_id, stated_interest, evidence_refs, human_readiness, assessor, assessed_at, gap, action, sponsor, due_date.

## Check
Every critical role has coverage or an explicit gap. Individual statements have sources; no speculative retention or promotion recommendation appears.

## Example
“Map continuity gaps for these five critical roles and propose development assignments for our approved talent pool.”

Sources: [CIPD succession planning](https://www.cipd.org/en/knowledge/factsheets/succession-planning-factsheet/) · [CIPD competence and competency frameworks](https://www.cipd.org/en/knowledge/factsheets/competency-factsheet). Checked 2026-10-14.
