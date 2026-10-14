---
name: hr-hris-import
description: Map and validate an employee import, separating safe updates from duplicates and unresolved conflicts.
---

# HRIS import preparation

Create a reviewable import file and a reconciliation plan, not a blind bulk upload.

## Inputs

Use the source export, current target snapshot, exact destination schema/API version, immutable ID mapping, allowed values, field owners and effective-date rules. Optional private `hr-context.md` supplies system conventions. Use pseudonymous IDs during development; keep production files and credentials in approved private storage.

## Workflow

1. Build a field map: source, target, type, allowed values, conversion, required status and source authority. Resolve date formats, timezone, currency, decimal precision and character encoding explicitly.
2. Classify rows as insert, update, unchanged or blocked by stable identity. Never match automatically on names alone. Flag duplicate IDs/emails, unknown references, impossible dates and ambiguous blanks; do not silently deduplicate or clear destination data.
3. Stage dependencies such as departments and managers. Distinguish future-effective rows from current records; show before/after values and omit unchanged fields. Provider-specific omitted fields may reflect permissions.
4. Create a manifest with source hashes, schema version, batch key and row keys. A rerun must reuse the manifest and reconcile target state rather than blindly resubmit. After an ambiguous timeout, read target state before retrying; stop on identity conflicts or unauthorized fields.
5. Produce a small representative dry-run sample, expected counts and rollback/recovery instructions consistent with the target's actual capabilities. Keep upload and employment-record changes outside this preparation task.

## Deliver

Validated import CSV, `field-map.csv`, `exceptions.csv` and a manifest: batch_key, source_hash, target_snapshot_at, inserts, updates, unchanged, blocked, reviewer. Provide expected post-import counts and sample checks.

## Check

Every input row appears in exactly one disposition. Row keys are unique, dependencies resolve and no destructive blank is implicit.

## Try it

“Map this roster to our BambooHR import schema. Show only changed fields, separate duplicates and give me a dry-run sample and reconciliation checklist.”

Sources checked 2026-10-14: [BambooHR employee records API](https://documentation.bamboohr.com/reference/get-employee) · [BambooHR API technical overview](https://documentation.bamboohr.com/docs/api-details). Recheck applicable rules and provider documentation when used.
