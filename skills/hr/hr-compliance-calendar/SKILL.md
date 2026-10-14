---
name: hr-compliance-calendar
description: Convert verified HR obligations into an owner-assigned calendar with applicability, sources and evidence requirements.
---

# HR obligations calendar

Build an auditable calendar from verified obligations; do not claim universal legal coverage.

## Inputs

Use legal entities, operating jurisdictions, establishment/worker categories, confirmed applicability facts, current official sources, company policies, reviewer owners and prior filings. Optional private `hr-context.md` supplies reminders and cadence. Treat applicability, rates and deadlines as dated facts requiring evidence, not permanent defaults.

## Workflow

1. Define scope by entity, jurisdiction and period. List candidate payroll, social-insurance, employment-record, policy-review and reporting obligations. Mark each applicable, not applicable or unresolved with the responsible specialist's basis; do not infer coverage from company size alone.
2. Verify each applicable obligation against the issuing authority's current publication or portal. Record title, section, URL, published/effective date and checked-at date. Distinguish a statutory duty from an internal target; retain superseded rules only for historical periods.
3. Calculate due dates using the stated rule and official treatment of holidays/extensions. If ambiguous, leave the statutory date unresolved and assign a reviewer; never substitute a convenient business day. Store timezone and period covered.
4. Work backward to set internal preparation, review and submission milestones. Include dependencies, evidence required and an accountable owner. Use `entity + obligation + covered_period` as the stable key; reconcile with prior acknowledgments to avoid duplicate work.
5. Flag changed sources, overdue unresolved items and missing confirmations. Prepare reminder drafts only. India EPFO/ESIC sources are starting points for their own schemes, not proof of complete India or worldwide compliance.

## Deliver

`obligations.csv`: obligation_key, jurisdiction, applicability_basis, source_version, covered_period, statutory_due_at, internal_due_at, owner, evidence_required, status. Add unresolved applicability questions and source changes.

## Check

Every due date and applicability assertion has evidence. A submitted filing is not “accepted” without acknowledgment; no filing, payment or reminder is sent automatically.

## Try it

“Build next quarter's HR calendar for these confirmed Indian entities from the supplied official notices. Separate statutory dates from internal deadlines and flag unverified applicability.”

Sources checked 2026-10-14: [EPFO official employer portal (India)](https://unifiedportal-emp.epfindia.gov.in/epfo/) · [ESIC monthly contribution workflow (India)](https://portal.esic.gov.in/InsuranceGlobalWebV4/ESICInsurancePortal/Documents/consolidated_mc_%26_edit_mc_helpfile.pdf). Recheck applicable rules and provider documentation when used.
