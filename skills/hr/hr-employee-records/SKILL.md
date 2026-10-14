---
name: hr-employee-records
description: Find missing, conflicting and stale employee fields and prepare an evidence-backed correction queue.
---

# Employee records review

Prepare a precise correction queue without silently rewriting employee history.

## Inputs

Use an authorized minimum-field export, stable employee IDs, schema, field owners, effective-date rules, source documents and approved retention/access policy. Optional private `hr-context.md` supplies terminology and workflow owners. Keep records in the approved private workspace; output IDs and evidence references instead of unnecessary personal details.

## Workflow

1. Record export time, system, jurisdiction, policy version and requested field list. Match by immutable system ID, not name or editable employee number. For BambooHR, a missing requested field can reflect permissions: never treat it as an empty value to overwrite.
2. Check required-field completeness, duplicate identifiers, invalid dates, unknown department/manager references and incompatible employment dates. Separate current values from future-effective changes.
3. Compare each disputed field with its authoritative source. Preserve both values, effective dates and source priority; leave unresolved conflicts open. Do not infer gender, disability, marital status or other sensitive attributes.
4. Prepare the smallest proposed correction with `employee_id + field + effective_date` as its key. Exclude unchanged fields, make explicit the distinction between absent, blank and intentional clearing, and route each change to its owner.
5. Apply the supplied retention schedule only as a review queue, including legal-hold status. Do not delete records or invent retention periods. Reconcile any separately authorized correction against a fresh read before marking complete.

## Deliver

`record-exceptions.csv`: change_key, employee_id, field, observed_value_reference, proposed_value_reference, effective_date, source, issue, owner, status. Include field-level completeness totals and unresolved access gaps.

## Check

Every proposed change has evidence; permission-limited fields are not classified as missing data. No live HRIS changes are implied by this report.

## Try it

“Audit this private roster for missing managers and conflicting start dates. Prepare corrections with evidence, keeping future transfers separate.”

Sources checked 2026-10-14: [BambooHR employee records API](https://documentation.bamboohr.com/reference/get-employee) · [ICO employment records guidance (UK)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/). Recheck applicable rules and provider documentation when used.
