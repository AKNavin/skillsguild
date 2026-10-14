---
name: hr-relations-intake
description: Capture a concern neutrally, preserve evidence and route the case to an authorized owner. Use for employee-relations, case-intake, grievance workflows.
---

# Employee relations intake

## Use
Use to organize an employee concern for the appropriate HR or investigator. This is intake and routing, not a finding, legal conclusion or disciplinary recommendation.

## Inputs
Report, dates, workplace jurisdiction, applicable policy, reporting channels and authorized case owner. Use a restricted workspace; private `hr-context.md` may supply acknowledgement style, but never store case facts in shared style memory.

## Do
1. Assign a case ID and separate the reporter's exact allegations from confirmed facts, documents and unknowns. Capture only necessary identifying information.
2. Ask concise neutral questions for missing event dates, locations, involved people, available evidence, requested support and desired contact method. Do not demand proof before accepting a report.
3. Flag reported immediate safety threats, retaliation, evidence-loss risk or conflicts involving the normal case owner for prompt human handling through the applicable channel. Do not autonomously investigate or contact the subject.
4. Preserve original evidence location, received time and access owner. Propose retention or legal-hold review; do not delete records or copy material outside permitted systems.
5. Draft an acknowledgement explaining next contact and realistic confidentiality limits. Do not promise secrecy, a particular outcome or a legal deadline not verified for the jurisdiction.
6. Route with a neutral summary and open questions. An authorized human determines process, interim measures and notifications under local policy and law.

## Deliver
Restricted `case-intake.md`: case_id, allegation_summary, chronology, reported_impact, requested_support, unknowns, routing_reason, owner, next_contact.
`evidence-register.csv`: evidence_id, source_location, received_at, description, custodian, access_scope, preservation_question.

## Check
Allegations remain attributed, access is limited, safety concerns are visible, and no credibility score or guilt determination appears.

## Example
“Turn this complaint into a confidential intake and acknowledgement draft, highlighting the right case owner and missing facts.”

Sources: [EEOC harassment policy tips](https://www.eeoc.gov/employers/small-business/harassment-policy-tips) · [Acas preparing a workplace investigation](https://www.acas.org.uk/investigations-for-discipline-and-grievance-step-by-step/step-2-preparing-for-an-investigation) · [ICO keeping employment records](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/employment/employment-practices-and-data-protection-keeping-employment-records/). Checked 2026-10-14.
