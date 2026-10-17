# Loom script

| t | screen | say |
|---|---|---|
| 0:00 | Slack, #targets-tara | An IR team goes to an event with 80 attendees. Who matters for which product, who covers them, what was said, what happens next. The agent does the clerical part; every decision stays with a person. |
| 0:30 | Dataleap, Skills list | One Dataleap agent, five skills, four integrations: Attio, Slack, LinkedIn enrichment, web search. |
| 0:45 | GitHub, config/workspace.yaml | Everything that changes for a second team is in this file. |
| 1:00 | Slack, #targets-tara digest | One message per DRI per event. Marker, name, company, role, tiers, one sentence of background, interests, Attio link. Tiers are priority, not eligibility. Three products scored separately. Routing: product focus, then vertical, then whoever attends. |
| 1:45 | Slack, #targets-mara, #targets-leonie | Six people here, three there. Nothing else in these channels. |
| 2:00 | Slack, voice clip + transcript | After the event the DRI talks. The agent transcribes, corrects product and attendee names with a glossary, shows what it changed, and waits. Point at "Jinka": that was "Gen Cap". Nothing reaches the CRM from an unconfirmed transcript. |
| 3:00 | Slack, "Attio changes for Testperson 4" | Proposal in plain language. The DRI approves by reaction or by reply. Approval is bound to that DRI's Slack identity. |
| 3:30 | Slack, "Done for Testperson 4" → Attio opportunity, tasks, note | Entity, opportunity with owner and contact, two tasks, note with the raw transcript. Every write read back. |
| 4:30 | Slack, follow-up draft | The agent drafts, the human sends. "Sent" closes the task. "Change the second sentence" gives v2. |
| 5:00 | Slack, #targets-mara, Testperson 11 | Rejection: to-do only, "no", nothing changed, note stays. |
| 5:30 | GitHub, evals output | Tier function total, routing deterministic, normalizer never touches negations. |
| 5:50 | Dataleap, status | Exactly-once events, per-entry locks, checkpoints, daily run budget, skill versions, zero dead letters. |
| 6:20 | Slack | Limits: public channels because the shared Slack connection can't see private ones; synthetic attendees, so photos and research show on real profiles only; Gmail drafts once a mailbox is connected; one event. Next: Luma API, template refactor, German debriefs. |
| 6:50 | — | Stop. |
