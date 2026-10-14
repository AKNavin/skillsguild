---
name: hr-workflow-router
description: Turn an HR request into the smallest useful sequence of skills, inputs, owners and finished outputs.
---

# Plan an HR request

Convert an HR request into an executable plan. Read the request and any available private `hr-context.md`, `hr-style.md` and `role-brief.md`. Do not require setup files for a simple task that already has enough context.

## Route
1. Identify the trigger, business outcome, deadline, jurisdiction where relevant and affected systems. Distinguish producing an artifact from changing a live record or contacting someone.
2. Inspect the available skill catalogue. Select only skills required for this outcome; verify each path and its required inputs. If unavailable, describe the needed capability rather than inventing a tool.
3. Sequence work by dependencies. Reuse approved context and existing artifacts. Ask once for the smallest set of blocking inputs; start independent work immediately.
4. For each step record owner, inputs, output, completion test and execution permission. Human employment decisions remain explicit decision steps; do not recast evidence preparation as selection authority.
5. Complete the authorised steps using the selected skills. Maintain `step_id | status | artifact | dependency | next_action`. A missing integration produces an export or handoff, not a claim that the HRIS was updated.

## Deliver
A short plan followed by completed artifacts and a precise outstanding queue. Link each output to the next step. For example, an approved hiring request can produce role brief → JD → interview kit → scheduling plan, with an approval-dependent offer step later.

**Check:** every promised output exists, every unfinished step has one concrete blocker or next owner, and no optional skill expanded the user's scope. Report what ran, what was drafted and what remains pending.

**Try:** “Help me hire and onboard two support associates next month. Use the available HR skills and start with the inputs I have already supplied.”

Sources: [CIPD People practice](https://www.cipd.org/uk/the-people-profession/the-profession-map/explore-the-profession-map/core-knowledge/people-practice/) · [NIST AI Risk Management Framework FAQs](https://www.nist.gov/itl/ai-risk-management-framework/ai-risk-management-framework-faqs). Checked 2026-10-14.
