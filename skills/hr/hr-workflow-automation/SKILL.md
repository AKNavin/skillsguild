---
name: hr-workflow-automation
description: Specify triggers, permissions, state, retries and evidence for a reliable HR automation.
---

# Build a repeatable HR workflow

Turn a proven HR process into a concrete automation specification or implementation for the user's chosen tools. Inputs: trigger, sample event, source-of-truth system, authorised actions, owners, timing rules and acceptance criteria. Use redacted samples.

## Implement
1. Map trigger → validation → work → review → action → reconciliation. Specify exact fields, connector/API capability, credentials mechanism and least required permissions. Verify current official integration docs; never invent endpoints or promise integrations are connected.
2. Use a stable event/request ID and business key. Persist state such as received, blocked, prepared, approved, executing, confirmed and failed. Store timestamps, source version, artifact IDs and error reason. Keep sensitive payloads in the approved system, not general logs.
3. Bind approval to the specific payload version. A changed recipient, amount, effective date or substantive document invalidates stale approval. Existing scoped authorisation need not be requested again.
4. Before retrying a timeout, query the remote result using its identifier. Prevent duplicate letters, tickets, payments or access requests. Retry transient errors with a bounded policy; route validation, permission and uncertain outcomes to an owner.
5. Test locally with synthetic events: duplicate delivery, partial failure, restart, stale policy, changed payload and unavailable connector. Keep employment decisions as human steps; financial transfers and destructive account changes require the applicable action controls.

## Deliver
Runnable workflow when tools are available; otherwise exact node/field mapping, event schema, state ledger, setup gaps and manual fallback. Include a dry-run trace and reconciliation report.

**Check:** replaying the same event causes no second external action; a timeout cannot be labelled success without remote evidence. Do not claim a draft specification is deployed automation.

**Try:** “Automate approved new-joiner tickets in our chosen HRIS and task tool, with duplicate-event protection and an owner for failed steps.”

Sources: [NIST AI Risk Management Framework FAQs](https://www.nist.gov/itl/ai-risk-management-framework/ai-risk-management-framework-faqs). Checked 2026-10-14.
