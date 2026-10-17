# IR Event Coverage Agent (Dataleap)

One Dataleap agent for a VC investor-relations team. Pre-event: attendee export → event record → identity match in Attio → research → product fit and tier (Gen Cap / Fund / DI) → DRI assignment → Slack briefing. Post-event: DRI debrief in the Slack thread → conversation note → proposal → approval by Slack reaction → Attio writes → read-back.

Built as a demo for Dataleap (application task). The agent runs inside Dataleap; this repo holds everything needed to rebuild, extend or audit it.

## Rules as code

`rules/tier.py` and `rules/route.py` implement the tier function and routing rules exactly as written in the skills; `python3 -I evals/run_evals.py` proves totality and determinism. The Dataleap agent applies the skill text; the code is the oracle for T16/T17.

## Layout

```
dataleap/
  prompts/agent-prompt.md        the prompt pasted into the Dataleap agent chat (current)
  prompts/build-spec-v2-full.md  the long form of the same spec, before skills were split out
  skills/                        four skills imported into Dataleap (Skills → Import)
  exports/                       exports from Dataleap: skills ZIP, agent DB CSVs, run summaries
fixtures/                        test attendee CSVs
attio/                           schema snapshot of the Attio workspace "b2v" (read-only reference)
docs/                            status, decisions, run log, Loom script
handover/codex/                  the earlier Codex handover package (zip + extracted files)
```

## Systems

| System | Role | Identifier |
|---|---|---|
| Dataleap | agent runtime, skills, agent DB, triggers | workspace "Mara's Workspace", agent "IR-Coverage" |
| Attio | CRM, private test workspace | slug `b2v` |
| Slack | briefings and debriefs, test workspace | team `T0C9LBW0N3G`, channel `#event-coverage` = `C0C9WQFS78A` |
| LinkedIn (via Dataleap) | profile enrichment for supplied URLs | read-only |
| Web Search (Dataleap built-in) | organisation-scoped research | — |

## How to continue

1. Read `docs/STATUS.md` for where the build stopped and why.
2. Read `docs/DECISIONS.md` before changing any rule; the reasons are there.
3. Skills are the rule base. Change a skill file, re-import it into Dataleap, do not edit rules inside the agent chat.
4. The agent prompt is the control flow. Change it only for new steps or tool boundaries.
5. Run order after any change: Phase 0 (read-only) → `go` → `run 6.1` (plan mode, then `write`) → `run 6.2–6.5` → `send briefings` → debrief → reaction.

## Security

Only synthetic people and the three test DRIs (Testperson 1–3) are used. No real investor data. The Attio workspace is a private rebuild, not the employer's CRM. The agent never emails anyone.
