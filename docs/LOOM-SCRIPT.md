# Loom script — 7 minutes, one take

Screen order: Slack (three #targets channels + #event-coverage), Attio (Testperson 4 coverage entry, Müller Family Office opportunity), Dataleap (agent chat, Skills list, Triggers), GitHub (repo root, `rules/`, `evals/`). Speak plainly; every beat ends on something visible.

**0:00 Problem (30 s).** An IR team at a VC goes to an event with 80 attendees. Who matters for which product, who covers them, what was said, what happens next. Today that lives in heads and spreadsheets. The agent does the part that is clerical and leaves every decision with the human.

**0:30 Shape (45 s).** One Dataleap agent. Five skills: Attio contract, product rules, DRI routing, debrief extraction, operator. Four integrations: Attio, Slack, LinkedIn enrichment, web search. Everything instance-specific in one config file. Show Dataleap Skills list, then `config/workspace.yaml` on GitHub.

**1:15 Before the event (90 s).** Show `#targets-tara`: "Tara, your targets for Berlin Capital Signals 2026". Read one block aloud: marker, name, company, role, tiers "Gen Cap A, DI B", one background sentence, Interests line, Attio link. Say: tiers are coverage priority, never eligibility; three products scored independently; routing by product focus, then vertical, then whoever attends; a DRI never gets more than their capacity. Flip to `#targets-mara` (six people) and `#targets-leonie` (three). Say: one message per person per event, in their own channel, nothing else.

**2:45 After the event, voice (90 s).** Show the voice clip in `#targets-tara`, the transcript the agent posted with the confirmation request. Point at "Jinka" in the first German transcript: ASR heard "Gen Cap" as "Jinka". Say: a deterministic glossary normalizer corrects product names and attendee names before the DRI sees it, shows what it changed, and the DRI confirms by saying yes in any form, or corrects a single word. Nothing reaches the CRM from an unconfirmed transcript.

**4:15 Proposal and approval (60 s).** Show "Attio changes for Testperson 4": new investor entity, new Gen Cap opportunity, outcome, open to-do. Say: the DRI approves by reaction or by reply; approval is bound to that DRI's Slack identity. Show "Done for Testperson 4" with the three links. Flip to Attio: the opportunity with route, owner, contact, source note; the two tasks; the conversation note with the raw transcript appended.

**5:15 Follow-up and rejection (45 s).** Show the follow-up draft under the confirmation: first person, the agreed next step, mailto link. Say: the agent drafts, the human sends; "sent" closes the task; "change the second sentence" produces v2. Then show the Mara thread for Testperson 11: proposal with only a to-do, "no", "Nothing changed in Attio. The conversation note stays."

**6:00 What makes it safe to run (45 s).** On GitHub, `evals/run_evals.py` output: the tier function is total over the signal space, routing is deterministic, the normalizer never touches negations. In Dataleap, `status`: exactly-once Slack events, per-entry locks, run checkpoints, a daily run budget, skill versions with hashes, zero open dead letters. Say: Attio holds the business records, the agent DB holds execution state, every write is read back.

**6:45 Limits and next (30 s).** Honest list: public channels because the shared Slack connection cannot see private ones (production: a custom Slack app); synthetic attendees, so photos and web research only show on real profiles; Gmail drafts once the DRI's mailbox is connected; one event. Next: Luma API when available, the config refactor into a template, German debriefs as a first-class path.

Stop. Do not scroll back. Total 7:15.
