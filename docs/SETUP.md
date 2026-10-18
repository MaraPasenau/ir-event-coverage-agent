# Setup — from an empty workspace to a running Event Coverage Agent

One page. Order matters. Everything instance-specific goes into `config/workspace.yaml`; prompt and skills are not edited per workspace.

## 0. What you need
- Attio workspace with API access (the custom objects below), Slack workspace where you can create public channels and add the Dataleap app, Dataleap workspace with Attio, Slack, LinkedIn enrichment, Web Search and Transcription connected, GitHub connected to this repository.
- One Slack user per DRI. A DRI without a Slack user ID is not routable.

## 1. Attio schema
Objects: `ir_coverage_events`, `ir_investor_entities` (required `name`, `investor_type`), `ir_opportunities` (required `name`, `route`, `investor_entity`; `responsible_dri` select must contain the DRI codes; `responsible_workspace_member` actor-ref).
Lists on People: `ir_event_coverage` (fields per `dataleap/skills/ir-attio-contract.md`), `ir_dri_people` (`dri_code`, `profile_status`, `product_focus`, `vertical_expertise`, `slack_user_id`, `slack_channel_id`, `attending_events`, `workspace_member`, `coverage_capacity`, `relationship_people`).
`attio/schema-snapshot.md` is the reference; the Attio MCP cannot create attributes, so this step is done in the Attio UI or with the REST API. Phase 0 reports any missing attribute by name.

## 2. Slack
- Create `#event-coverage` (public, team summary) and one public channel per DRI named `#targets-<firstname>`. Private channels do not work: the shared Dataleap Slack connection cannot read, post or trigger in them, even when the bot is a member.
- In each channel: mention `@Dataleap` → "Add them". Add the DRI.
- Note the channel IDs (channel details, bottom) and each DRI's user ID (profile → ⋯ → Copy member ID).

## 3. DRI profiles in Attio
One `ir_dri_people` entry per DRI: `profile_status = Confirmed`, `product_focus`, `vertical_expertise`, `slack_user_id`, `slack_channel_id`, `coverage_capacity`, `attending_events` for the current event. Put the same values into `config/workspace.yaml` → `dris`.

## 4. Dataleap
1. Skills → import the five files from `dataleap/skills/` (each has a `Version …` line under its heading; the import strips front matter). Re-importing creates new skill IDs: the agent must load skills by name, never by saved ID.
2. New agent chat → paste the first message from `docs/SUBMISSION.md` ("set up from repository …"). The agent pulls `dataleap/prompts/agent-prompt.md` and `config/workspace.yaml`, runs Phase 0 and stops at `go`.
3. Check the Phase 0 report: five skill versions, channel IDs resolved, bot membership, `rules_version demo-v2`, agent DB tables created.
4. `go`. For a new event: attach the CSV (agent format or Luma guest export) and write `import <event name>, <date>`; the agent runs import → research → tiers → assignment → briefings and reports once. For an existing event: `run 6.4–6.6 <event>`.
5. Triggers: the agent configures two per DRI channel (new message, reaction added), each filtered to that DRI's user ID; approve enabling them when it asks. Six triggers for three DRIs.

## 5. First debrief
Post a voice or text message in a DRI channel naming an attendee. Expected: transcript with a `Changed:` line if the normalizer corrected a product name → any affirmative reply confirms → "Attio changes for <name>" proposal → any affirmative reply approves → "Done for <name>" with Attio links → follow-up draft (Gmail draft if the DRI's Gmail is connected, otherwise text with a mailto link) → ✅ or "sent" closes the follow-up task.

## Platform facts that cost us time
- Transcription works only as a native tool call, not from a script (HTTP 400 "file-output tools unavailable" via programmatic tool calling). The transcription tool has no vocabulary or prompt parameter; `rules/transcript_normalize.py` is the correction layer.
- Attio `list notes` accepts `limit ≤ 50` and exposes no cursor; the agent stops at a full page rather than risk a duplicate note.
- Attio truncates timestamps to milliseconds and returns `[]` for blank text; read-back treats both as verified with a note.
- Dataleap exposes no per-run cost; the budget guard counts runs (`budget_daily_runs`) instead of dollars.
- Slack trigger definitions are one channel each; three DRIs mean six definitions.
- The agent's durable instructions grow on every reload; after a series of changes ask it to compact them to the current spec.
- Every message in a DRI channel is a paid run. Do not test with "hello".

## Commands the operator uses
`go`, `import <event>, <date>` (with CSV; `import only` stops after 6.1), `run 6.2–6.5 <event>`, `run 6.4–6.6 <event>`, `send briefings <event>`, `attending <event>: <names>`, `add dri <Name>, <email>, <products>, <verticals>`, `list dris`, `status`, `retry dead letters`, `run test T<n>`, `stop`.
