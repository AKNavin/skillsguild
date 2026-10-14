---
name: hr-contingent-workforce
description: Track approved contractor and agency engagements from scope and onboarding to renewal and exit.
---

# Coordinate contingent workers

Coordinate contractor, agency or fixed-term engagement administration from approved records. Do not determine legal worker classification from a label or automate hiring, renewal or termination decisions.

## Inputs and work
Use the approved engagement, supplier, statement of work, entity, location, dates, rate/unit, budget owner and applicable process. Optional private HR context provides systems and routing.

1. Record engagement ID separately from worker and supplier IDs. Distinguish approved classification from unresolved classification; route uncertainty to the responsible specialist before using employee-only rules.
2. Extract deliverables, milestone acceptance, spend limit, access sponsor and end date. Separate hourly/daily rates from fixed-price milestones and state currency and tax assumptions as supplied.
3. Produce onboarding tasks for procurement, HR, security and manager with dependencies. A signed agreement or access request is not evidence that checks or provisioning completed.
4. Reconcile approved time/deliverables with invoices and purchase-order scope. Flag duplicates, changed rates, dates outside the engagement and unsupported charges; do not approve payment.
5. Build an expiry/renewal queue with owner and lead time from policy. Renewal requires an authorised decision; access must not be extended silently. Plan handover and access review on closure.

## Deliver and check
`engagement_id | supplier | scope | start | end | rate_basis | currency | budget | owner | next_action | due | evidence`. Include exception and renewal queues. Verify distinct engagements are not merged, spend units agree and closure is backed by handoff evidence.

**Try:** “Turn these approved agency engagements into onboarding, invoice-exception and renewal trackers.”

Source: [CIPD workforce planning](https://www.cipd.org/uk/knowledge/factsheets/workforce-planning-factsheet). Checked 2026-10-14; jurisdiction-specific guidance is not a universal legal rule.
