# Status — 2026-10-16

## Where the build stopped

Dataleap weekly budget exhausted ($7.72 / $7.50, resets in 3 days). Step 6.1 is complete and verified; 6.2–6.5 have not started.

## Done and verified in the target systems

| Step | Result | Evidence |
|---|---|---|
| Phase 0 discovery | Tools, schema, Slack channel, LinkedIn enrichment, web search checked read-only | Capability report in Dataleap chat 2026-10-16 |
| Schema fixes from Phase 0 | `investor_type` mapping, `responsible_dri` not written on investor entities, note title with message ts, approver mapping, multi-product convention | `dataleap/skills/ir-attio-contract.md` |
| Attio prep (manual, via Claude) | DRI profiles: `product_focus`, `coverage_capacity`, Testperson 3 → workspace member; "Anna Müller" (variant A) created for T2; coverage list renamed `ir_event_coverage`; three old fixture entries set `suppressed = true` | Attio `b2v` |
| Slack prep | `#event-coverage` created, Dataleap app added | Slack `T0C9LBW0N3G` |
| 6.1 Import | 12 people created, 12 coverage entries, 11 Verified / 1 Conflict (Anna Müller), event reused and updated, 26 writes read back, 1 timestamp-precision mismatch reconciled without replay | Dataleap run `import-6d1edaebf4a6453c83a3f3b762877f39`; Attio list `ir_event_coverage` |

## Not done

- 6.2–6.5 (identity confirmation, research, fit/tier, DRI routing, Slack summary)
- 6.6 briefings, 6.7 debrief, 6.8 proposal/approval/execution
- Tests T0–T14 beyond the 6.1 parts of T0/T2/T4
- Voice chain (T11) — Phase 0: available but inactive, untested
- Second event with the real Insight Forum export (65 rows, needs cleaning)

## Next commands, in order

```
run 6.2–6.5 Berlin Capital Signals 2026 [Synthetic]
Scope: only the entries with luma_attendee_id luma-0001, luma-0004 and luma-0008 (Testperson 4, 7, 11).
Cost mode: read back once per entry at the end of each step; one run-summary row per step; lowest model tier that supports tool calls for 6.3; report only deviations plus the per-entry table.
```
then `send briefings Berlin Capital Signals 2026 [Synthetic]`, then a text debrief in the Testperson 4 thread, then `:+1:` by Testperson 3.

Expected: Testperson 4 → Gen Cap Tier A → Testperson 3 (R2); Testperson 7 → DI → Testperson 1 (R2); Testperson 11 → DI Tier B → Testperson 1; Anna Müller → not routed.

## Known IDs

- Event record: `f0bc9108-2f96-416e-9e42-d09aafb4ae89` (start 2026-10-23, Manual Authorized, no Luma URL)
- Coverage list: `ir_event_coverage` / `8ad90a24-81ed-41da-872b-e50241f13f2a`
- Anna Müller A (pre-existing): `8df22249-7537-4fa6-91e8-30f3233c0808`; Anna Müller B (created, Conflict): `95974988-bde2-4236-ba9a-6f4bb1d40a00`; coverage entry `f878fdb4-4894-4851-a460-add5139d8a8c`
- DRI profile entries (`ir_dri_people`): Testperson 1 `aff9ebda-…`, Testperson 2 `1dd71026-…`, Testperson 3 `c4841e00-…`
- Suppressed fixtures: `37d2de09-…`, `633c10a3-…`, `fa9115b2-…`

## Cost notes

Phase 0 + 6.1 ≈ $7.70, 102 tool calls in 6.1 alone. Drivers: full schema read, per-field read-back, per-call intent logging, scripts written by the agent. The "cost mode" line above halves this for the next steps. Production runs via event triggers are expected at cents per run.

## Update 12:45 — second Dataleap account

The first account's weekly budget ($7.50) is exhausted. A second Dataleap workspace will be set up. Checklist for the new workspace:

1. Connect Attio (workspace b2v), Slack (test workspace T0C9LBW0N3G), LinkedIn; enable Web Search.
2. Add the new workspace's Dataleap app to #event-coverage (Channel details → Integrations → Add apps).
3. Import the four skills from dataleap/skills/.
4. Paste dataleap/prompts/agent-prompt.md (v3: cost mode, short Phase 0, existing-state block).
5. After `go`: `run 6.2–6.5 Berlin Capital Signals 2026 [Synthetic]` with scope luma-0001, luma-0004, luma-0008.

Attio and Slack state carries over unchanged. The old agent DB does not; nothing in it is needed.

## Update 17:40 — third Dataleap account (unlimited budget)

Live state in Attio/Slack, which overrides the snapshot above:
- luma-0001 (Testperson 4): stage Pre-event Brief Ready; Gen Cap A, DI B, Fund Irrelevant; DRI Testperson 3 (R2); briefing Sent; Slack thread ts 1792182075.571519 in C0C9WQFS78A. A voice clip reply from Mara is in that thread, not yet transcribed.
- luma-0002 … luma-0012: stage Imported.
- Event summary message posted in #event-coverage (old layout). New compact layout (6.6) applies from the next card.
- Triggers configured on the second account do not carry over; configure again.

Next: configure triggers, process the voice clip in the Testperson 4 thread (transcript → ✅ → proposal → 👍), then run 6.2–6.6 for the remaining 11 entries, then T3/T7/T9/T14.

## Update 21:00 — rule audit applied (demo-v2)

`docs/RULE-AUDIT.md` lists the findings. All four skills and the prompt were rewritten accordingly; `rules/tier.py` and `rules/route.py` are reference implementations, `evals/run_evals.py` passes 23/23 (totality of the tier function, B/C disjoint, determinism, R2 iteration, capacity, escalation).

Consequences for the live state:
- Tiers currently in Attio were computed under demo-v1 (e.g. Testperson 4 DI = Tier B; demo-v2 gives Tier C for one core signal without booster). Either accept v1 tiers for this event or clear `proposed_overall_tier` on the 12 entries and rerun 6.4 (`run test T17` afterwards).
- Testperson 1 is not eligible until `slack_user_id` is set in Attio; DI attendees route via R3/R4 to Leonie or Tara. The 9 briefings already sent stay as they are.
- Optional Attio attributes `slack_channel_id` (text) and `attending_events` (multi record-ref → ir_coverage_events) on list `ir_dri_people` are not created yet; the agent falls back to `dri_config`.
- The Dataleap workspace must re-import the four skills (IR Product Rules is now "demo-v2") and receive the new prompt before the next run.

## Update 21:15 — Slack private channels not supported

Dataleap reported: the shared Slack connection supports public channels only; private-channel reads, posts and triggers require a personal Slack connection or a custom Slack app. Decision 25: public `#targets-<firstname>` channels. Created so far: `#targets-leonie` C0CAUDMH80Y (bot U0C9X4ZUJF4 and Leonie U0C9LBXNZSS invited). `#targets-tara` and `#targets-mara` still to be created in the Slack UI (public, add @Dataleap and the DRI). Then re-import `ir-dri-routing.md` and `ir-debrief-extraction.md`, reload the prompt at the new commit, `go`.

Production upgrade path: a custom Slack app with `channels:history`, `groups:history`, `chat:write`, `reactions:read`, `files:read`, `users:read.email` restores private channels; the skill text does not change, only the channel IDs.

Phase 0 (3rd account, after demo-v2 import) also reported: existing agent DB tables differ from the new contract (reconcile, do not delete history); tiers in Attio carry no demo-v2 stamp; `slack_channel_id` / `attending_events` attributes absent (fallback active).

Channel IDs: #targets-mara C0C9YDQ3HML, #targets-leonie C0CAUDMH80Y, #targets-tara C0CA43FNPGC (all public, bot U0C9X4ZUJF4 member). Mara channel: Mara has no Slack user yet.
