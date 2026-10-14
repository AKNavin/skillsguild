# HR with SkillsGuild

Give your AI this guide and a concrete task. The library covers 64 focused HR workflows, from workforce planning through exits. Each skill defines useful inputs, steps, an output and a completion check. Download one skill or the HR pack; read only what the task needs. A direct SKILL.md link does not embed supporting scripts or templates—follow its relative links or download its ZIP.

## Start with your way of working

Use [Build your HR context](library/hr/hr-context-profile/SKILL.md) to capture your HR remit, company, priorities, policies, systems and decision owners in a private `hr-context.md` file. Use [Learn your HR writing style](library/hr/hr-style-guide/SKILL.md) to turn approved samples and corrections into `hr-style.md`. For role-specific work, use [Understand a role and its team](library/hr/hr-role-context/SKILL.md) to create `role-brief.md`.

These files give the next task reusable working context. Explicit preferences remain distinct from tentative patterns; each update is versioned. They do not retrain the model or guarantee memory across chats. Save them in your approved private workspace and supply only the relevant files next time. Simple tasks can start immediately without a setup interview.

**First prompt:** “Use the relevant HR skills in this guide. My role is [HR responsibility], my company operates in [locations], and I need [specific output] by [date]. Use the policies and examples I provide. Ask only for blocking inputs, complete the authorised work, and show finished artifacts plus anything awaiting an owner.”

## Choose the outcome

| Need | Suggested sequence | Useful result |
| --- | --- | --- |
| Plan capacity | Workforce plan → workforce cost → hiring intake | Demand/capacity gaps, scenarios and approval packet |
| Recruit for a role | Role context → role scorecard → job description → sourcing plan → outreach | Reusable role evidence, advert and authorised outreach drafts |
| Run interviews | Application evidence → interview kit/work sample → scheduling → debrief | Consistent evidence packets, agenda, calendar plan and decision questions |
| Close a hire | Recorded human decision → offer preparation → candidate communications | Reconciled terms, offer approval pack and status messages |
| Bring someone in | Preboarding → onboarding plan | Owner-assigned readiness tasks and a role-specific 30–60–90 plan |
| Run people operations | HR helpdesk → policy answer / employee records / HRIS import / letters | Sourced responses, validated change files and completion evidence |
| Close monthly payroll | Attendance exceptions → leave coordination → payroll handoff → reconciliation | Approved inputs and a line-level variance queue |
| Manage performance | Goal setting → one-to-one → feedback synthesis → review cycle → calibration | Evidence-backed goals, check-ins and review packs for accountable reviewers |
| Develop capability | Learning needs → development plan → learning program → career framework | Targeted practice, resources and observable capability checks |
| Review pay and benefits | Compensation review / benefits coordination | Calculations, exceptions and an approval-ready decision pack |
| Improve employee experience | Engagement survey → engagement actions → wellbeing / recognition | Private aggregate findings and owned, measurable actions |
| Handle sensitive concerns | Relations intake → investigation plan / accommodation coordination | Restricted chronology, evidence register and process-owner handoff |
| Change the organisation | Organisation design → employee consultation → change communications | Options, genuine feedback log and approved rollout drafts |
| Handle specialist arrangements | Global mobility / contingent workforce / internal transfer | Dependencies, expiry checks and ownership across teams |
| Close employment | Offboarding → exit insights → retention review | Handover and clearance evidence, aggregate themes and review queue |
| Report and automate | Data quality → people dashboard → workflow automation | Reconciled metrics and a tested, resumable workflow specification or implementation |

If the right sequence is unclear, use [Plan an HR request](library/hr/hr-workflow-router/SKILL.md). Each skill in the index below has a direct link and a focused example prompt.

## What “automate” means here

With your AI and authorised tools, these skills can produce documents, extract structured records, reconcile files, maintain task queues and carry out scoped operations. Live HRIS, ATS, email or calendar work needs the user's connected tools and permissions. Without a connection, the output is a draft, import file or precise handoff—not a claim that a live system changed. The website itself does not process personnel records or connect to company systems.

Ask for the finished artifact, any run command, exception log and completion evidence. Employment selection, individual pay awards, discipline, accommodation eligibility and other consequential decisions remain with authorised people. Style adaptation changes wording, not evidence standards or policy. Preparing a message does not authorise sending it; existing specific authorisation should be respected without needless repeated approval.

The payroll variance skill includes a runnable, standard-library Python helper and synthetic fixtures. Its arithmetic comparison does not calculate tax, determine entitlement or authorise payment. Other skills are actionable instructions for your agent, not preinstalled integrations or a claim that every workflow has been tested in your systems.

## Keep context and rules current

Use dated company policies, the applicable location and employment arrangement. Verify changing legal, payroll, immigration and contractual rules with current primary sources and the responsible specialist. US and UK sources are labelled examples, not worldwide requirements; India-specific EPFO/ESIC references do not cover every Indian employment obligation. Never invent a statutory rate, deadline or retention period.

Keep personnel, compensation, medical and case data in approved private systems. Public contributions contain only original instructions, synthetic examples and reusable code. Store minimal task-specific context, attribute evidence, preserve unknowns and use aggregate reporting with appropriate suppression.

Coverage follows the employee lifecycle and operational handoffs described by [CIPD's People practice map](https://www.cipd.org/uk/the-people-profession/the-profession-map/explore-the-profession-map/core-knowledge/people-practice/). Individual skills link their relevant primary sources. Research checked 2026-10-14. This is a broad workflow library; unusual sector, union, jurisdiction or company processes still need their specific context.
