# Submission text (step 2, Dataleap application)

Paste into the application form or email. Adjust the Loom link.

---

**Event Coverage & Opportunity Agent for a VC investor-relations team**

Loom (7 min): <link>
Repository: https://github.com/MaraPasenau/ir-event-coverage-agent

What it does: before an event, it turns an attendee export into researched, tiered and routed briefings, one per DRI in their own Slack channel. After the event, a DRI talks or types in that channel; the agent transcribes and corrects, asks for confirmation, writes the conversation note, proposes the CRM changes in plain language, and on the DRI's yes creates the investor entity, opportunity and tasks in Attio, reads everything back, and drafts the follow-up for the DRI to send. CRM corrections from the same channel go through the same approval path.

Built entirely on Dataleap primitives: one agent, five skills, the agent database, event triggers for Slack messages and reactions, LinkedIn enrichment, web search, transcription, GitHub. No separate backend.

What I would point a reviewer at:
- `docs/DECISIONS.md`: 34 decisions with the alternatives I rejected, including the ones I got wrong first (private Slack channels, question-based briefings, emoji-only approvals, a tier function whose B and C were the same predicate).
- `evals/run_evals.py`: the rule set is proven total and deterministic, and the transcript normalizer is proven not to touch negations.
- `status` in the agent: exactly-once Slack events, per-entry locks, checkpoints with resume, a daily run budget, skill versions with content hashes.
- `config/workspace.yaml` and `docs/SETUP.md`: what a second team would change, and the platform facts that cost me time.

Limits I chose: synthetic attendees and a private Attio rebuild (no employer data left company systems), public DRI channels (the shared Slack connection cannot see private ones), Luma via CSV, one event. The agent never contacts an attendee.

---

## First message for a fresh Dataleap agent (used in SETUP.md step 4.2)

```
Set up this agent from my GitHub repository MaraPasenau/ir-event-coverage-agent (branch main). Read config/workspace.yaml, docs/STATUS.md and docs/DECISIONS.md. Confirm the five skills from dataleap/skills/ are imported (report the Version line of each). Then read dataleap/prompts/agent-prompt.md and treat it as your instructions from now on; instance values come from config/workspace.yaml. Run Phase 0 and stop at "go". Do not write to Attio or Slack before Phase 0 is done.
```
