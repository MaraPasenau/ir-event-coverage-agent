# IR Event Coverage Agent (Dataleap)

One Dataleap agent for a VC investor-relations team.

**Before an event:** attendee export → event record → identity match in Attio → research (LinkedIn enrichment, organisation-scoped web search) → three independent product tiers (Gen Cap / Fund / DI Angel Investment) → DRI assignment → one briefing per DRI in their own Slack channel.
**After the event:** the DRI talks or types in that channel → transcript with deterministic correction → confirmation → conversation note in Attio → "Attio changes for <name>" proposal → approval by reaction or reply → investor entity, opportunity, tasks written and read back → follow-up drafted for the DRI to send. Ad-hoc CRM changes from the same channel go through the same approval path.

Built in October 2026 as the application task for Dataleap. The agent runs inside Dataleap; this repository holds everything needed to audit, rebuild or extend it. Only synthetic attendees and three test DRIs are used; the Attio workspace is a private rebuild, not an employer system.

## Start here

| If you want to… | Read |
|---|---|
| see what it does | `docs/LOOM-SCRIPT.md` (7-minute walkthrough) |
| set it up in a new workspace | `docs/SETUP.md`, then `config/workspace.yaml` |
| understand why a rule is the way it is | `docs/DECISIONS.md` (34 decisions with rejected alternatives) |
| check the rules are well-defined | `python3 -I evals/run_evals.py` (30 checks: tier function total over the signal space, routing deterministic, transcript normalizer guarded) |
| know where the build stands | `docs/STATUS.md` |
| see what was audited and fixed | `docs/RULE-AUDIT.md` |
| see what is still wrong, ranked | `docs/STATUS.md`, section "known issues" |

## Layout

```
config/workspace.yaml            every instance value (Attio IDs, Slack IDs, DRIs, products, budgets); logic lives elsewhere
dataleap/prompts/agent-prompt.md the agent's instruction set: steps 6.1–6.10, tool boundaries, state machine, tests T0–T25
dataleap/skills/                 five skills imported into Dataleap (rule base; each carries a Version line)
  ir-operator.md                 how the agent reads the operator's chat messages (intent first, short answers)
  ir-attio-contract.md           schema, normalization, idempotency keys, agent DB tables, write protocol
  ir-product-rules.md            signals, tier function, rank_products()  (demo-v2)
  ir-dri-routing.md              eligibility, onboarding, R1–R4, approvers
  ir-debrief-extraction.md       transcript correction, intent classification, extraction, proposals, follow-ups
rules/                           reference implementations: tier.py, route.py, transcript_normalize.py, glossary.json
evals/run_evals.py               proofs over the rule set
fixtures/                        synthetic attendee CSV
attio/schema-snapshot.md         the Attio workspace as read via MCP
docs/                            status, decisions, audit, setup, Loom script, submission text
handover/codex/                  the earlier Codex handover (history)
```

## Design in six sentences

Attio holds business records and human decisions; the agent database holds execution state, evidence, proposals and message identity. Rules are text in skills, with code in `rules/` as the oracle; the LLM is used for language (evidence interpretation, debrief extraction, intent of a reply), never for keys, stages or routing ties. Every write is idempotent by a key derived from the record, read back, and logged; a timeout is followed by a lookup, never a replay. Nothing reaches the CRM without a human saying so in their own words, and the agent never contacts an attendee. Slack events are processed exactly once, entries are locked per run, runs checkpoint and resume, and a daily run budget stops the agent before it stops the credit card. Everything that would change for a second team is in one YAML file.

## Systems

| System | Role |
|---|---|
| Dataleap | agent runtime, skills, agent DB, triggers, LinkedIn enrichment (Crustdata), web search, transcription |
| Attio (`b2v`) | CRM: people, companies, coverage list, investor entities, opportunities, notes, tasks |
| Slack (`T0C9LBW0N3G`) | `#event-coverage` summary, `#targets-<firstname>` per DRI |
| GitHub | this repository; the agent pulls prompt, config and rules from it by commit |

## Known limits (deliberate)

Public DRI channels (the shared Dataleap Slack connection cannot operate in private channels; production uses a custom Slack app). Synthetic attendees, so profile photos and web research only appear for real profiles. Gmail drafts require the DRI's mailbox to be connected; until then the follow-up is text with a mailto link. Luma via CSV export, no live API. One event.
