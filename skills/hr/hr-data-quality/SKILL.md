---
name: hr-data-quality
description: Find duplicate IDs, inconsistent dates and missing fields before importing or reporting on HR data.
---

# Check HR data quality

Audit a permitted HR export without silently rewriting it. Inputs: CSV/table, field dictionary, effective date, unique-key definition and validation rules. Use the minimum fields needed; keep originals in the approved private workspace.

## Check
1. Record file hash, source, extraction time, reporting scope and row count. Confirm whether each row represents a person, assignment, event or pay period; employee ID alone may not be a unique key.
2. Validate required columns, explicit types, whitespace, encodings and date/time/currency units. Treat identifiers as strings so leading zeroes survive. Separate blank, zero, unknown and not applicable.
3. Detect duplicate business keys, impossible date sequences, broken manager references, inconsistent entity/currency and out-of-scope statuses. Check effective-dated overlaps only where the data model forbids them.
4. Classify issues as blocking or warnings with the approved rule, affected row IDs and proposed fix. Never fill missing pay or join dates from guesses. Keep legitimate rehires and concurrent assignments distinct.
5. Produce a proposed correction file only when requested, preserving a reversible row-level change log. Formula-like values must be neutralised in spreadsheet-facing exports while original evidence is retained separately.

## Output
`row_key | field | observed_issue | rule | severity | proposed_fix | owner`, plus counts by rule, blocked downstream uses and reconciled input/output totals. Minimise the displayed values so the issue report does not become a second personnel database.

**Check:** all input rows are accounted for; duplicate resolution is explicit; nothing is silently dropped or cast. Rerun checks on corrected data and leave unresolved issues visible.

**Try:** “Check this redacted employee export against our schema before import; show blockers and a separate proposed correction log.”

Sources: [CIPD People analytics](https://www.cipd.org/en/topics/people-analytics/) · [ICO collecting and keeping employment records (UK)](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/collecting-and-keeping-employment-records/). Checked 2026-10-14.
