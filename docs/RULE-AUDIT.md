# Rule audit — 2026-10-16

Scope: `dataleap/prompts/agent-prompt.md` and the four skills, checked against each other and against the live Attio schema (`ir_opportunities.responsible_dri`, `ir_dri_people`, `ir_event_coverage.coverage_stage` read via MCP today). Severity: **B** blocks or corrupts the current run, **L** logic defect (wrong or nondeterministic result), **C** two texts contradict, **D** state that does not survive an account switch.

Confirmed correct against the live schema: `ir_opportunities.responsible_dri` has options Testperson 1–3 (the write in 6.8 will succeed); `coverage_stage` has the nine documented statuses; `ir_dri_people` has `profile_evidence`, `relationship_people`, `backup_dri`, `coverage_capacity`. Unused but present: `ir_opportunities.responsible_workspace_member` (actor-ref), `ir_dri_people.backup_dri`, `conflict_policy`, `minimum_ticket`, `maximum_ticket`.

## B — blockers

| # | Finding | Consequence | Fix |
|---|---|---|---|
| B1 | Every product has exactly two core signals, so Tier B ("all but one core supported, rest unknown") and Tier C ("≥ 1 core supported, none contradicted, rest unknown") are the same predicate. A `contradicted` core signal without an exclusion maps to no tier at all. | The model picks B or C arbitrarily; markers 🟡/🔵 differ between runs; one contradicted signal produces an undefined tier. | Redefine per product: **A** = both core `supported`, newest evidence ≤ 24 months, no exclusion. **B** = both core supported on evidence > 24 months; or one core supported + booster supported on evidence ≤ 24 months. **C** = exactly one core supported, no booster; or any supported core whose only source is `pre-enrichment` (CSV) with no external corroboration. **Irrelevant** = exclusion supported by a dated source, or a core signal `contradicted` by a dated source. **Needs Review** = a signal both supported and contradicted; or undated contradiction. Recency is measured from the run date. |
| B2 | Testperson 1 (Mara) has no `slack_user_id`. Onboarding step 3 says a missing `slack_user_id` blocks routing; the eligibility definition does not require it. | Every DI-routed attendee lands in `#coverage-mara`, where no one is mentioned and no reaction can ever be accepted as approval. Dead end for the whole DI path (Testperson 7, 11). | One eligibility definition, in the routing skill only: `profile_status = Confirmed` ∧ `product_focus ≠ ∅` ∧ `vertical_expertise ≠ ∅` ∧ `slack_user_id ≠ ∅`. Until Mara's ID is mapped, DI attendees go through R3/R4 to Leonie or Tara. Decision for Mara: create the third Slack user now or accept the fallback. |
| B3 | 6.4 does not advance the stage (Ready for Review → Ready for Review), so 6.4 and 6.5 share a precondition and violate "advance by exactly one stage". 6.7 advances two stages (Conversation Logged → Routing Ready) in one step. | Re-running `run 6.2–6.5` re-tiers every entry (cost, nondeterminism). A crash inside 6.7 leaves entries at Conversation Logged, a state no step resumes from. Rejection and case C have no defined end stage. | Guard 6.4 by `proposed_overall_tier` empty (not by stage). 6.7 ends at Conversation Logged. 6.8a (post proposal) Conversation Logged → Routing Ready. 6.8b: 👍 → Promoted; 👎 → stays Routing Ready, `proposals.status = rejected`. Case C (note only) → Closed. Second debrief on Promoted: stage unchanged, state lives in `proposals.status`. |
| B4 | Reaction trigger (b) must know whether the reacted ts is a transcript, a proposal or a briefing. The transcript ts is stored nowhere; `slack_messages` is not among the allowed agent DB tables. | Dispatch by emoji instead of by message identity; a 👍 on a transcript (what people do) is ignored or, worse, treated as approval of a proposal that does not exist. | Add table `slack_messages(ts, channel_id, kind ∈ {briefing, transcript, proposal, confirmation}, coverage_entry_id, proposal_id, dri_code, posted_at)`. Every post the agent makes writes a row before anything else. Trigger (b): look up ts → kind; transcript accepts ✅ or 👍; proposal accepts 👍/👎 only; everything else no-op. |

## L — logic defects

| # | Finding | Fix |
|---|---|---|
| L1 | R2 picks "the DRI whose `product_focus` contains the top product". `product_focus` is multi-select; after one `add dri` two DRIs can share a product. R2 also looks only at the top-tier product: if that DRI is absent or at capacity the entry falls to R3 instead of trying the second product (Testperson 4 is Gen Cap A, DI B; Tara absent → should go to the DI DRI, not to a vertical match). | R2 iterates `relevant_products` in tier order; for each product, candidates = eligible, attending, under capacity DRIs with that focus; tie-break: fewest assignments this event → most vertical overlaps → list order. |
| L2 | R3 tie → Escalated contradicts Section 4.5 and R4 (escalate only if no DRI attends). | R3 tie-break: most overlaps → fewest assignments → list order. Escalated exists only in R4-no-attendee. |
| L3 | Vertical overlap treats `Other` and `Unknown` as matches. | Exclude both from the overlap set. |
| L4 | Needs Review conflates identity conflict (must not be routed) with thin evidence (< 2 sourced claims). Thin-evidence attendees get no DRI at all, against the stated goal that every attendee is covered. | Identity Conflict → never routed. Thin evidence → `proposed_overall_tier = Needs Review` but routed by R4 and appended to the digest as a final block "Also attending, no evidence yet:" with one line per name, no marker, no background. |
| L5 | R4 "fewest assignments so far" and the capacity check depend on processing order, which is unspecified. | Process entries sorted by `proposed_overall_tier` desc, then `luma_attendee_id` asc. Two runs on the same input must give the same routing. |
| L6 | D3 "a ticket below 50k lowers the tier by one step" from C has no target. | Floor at C. |
| L7 | "Strongest product" is defined three times (routing tie-break, contract multi-product, debrief `selected_product`) and the debrief version ranks by pre-event evidence, so T7 (interested in DI, strongest evidence Gen Cap) sets the wrong `selected_product`. | One function `rank_products(products)` in the product rules: tier → number of supported signals → precedence Gen Cap > DI > Fund. Debrief applies it over the *interested* products only. |
| L8 | `conversation_outcome` is mapped per statement, but polarity is per product (T7: Fund declined, DI interested). | Aggregate precedence: any `interested` with a `next_step` → Interest Confirmed; any `interested` → Potential Investor; vague/"later" → Nurture; every mentioned product `declined`, none interested → No Fit; no conversation → No Conversation. |
| L9 | `responsible_dri` on an opportunity created from a cross-product debrief (T9: Tara logs DI interest, DI focus is Mara) is undefined. | Default = the debriefing DRI. If a different DRI owns the route, add a proposal item "Task: handover to <DRI>" instead of auto-reassigning. Also write `responsible_workspace_member` (exists, actor-ref) from `dri_config.workspace_member`. |
| L10 | Idempotency keys are weak. Investor: `sha1(lower(name))` makes "Müller Family Office", "Mueller Family Office" and "Müller FO" three entities. Event: `luma_url or name` — adding the URL later changes the key and duplicates the event. `proposal_id` hashes `serialized_changes` without a canonical form. | Event: `luma_event_id` if present, else `normalize(name) + "|" + event_start date`. Investor (personal): `ir:investor:person:<person_record_id>`. Investor (organisation): company domain if known, else `normalize(name)`. `normalize` = NFKD, strip diacritics, casefold, collapse whitespace, drop legal suffixes (GmbH, AG, Ltd, LLC, Inc, SE, KG). `proposal_id` over canonical JSON (sorted keys, no whitespace). |
| L11 | LinkedIn URL "exact match" fails on `www.`, locale subdomains (`de.linkedin.com`), trailing slash, case, query string. Applies to the Attio match key and to the enrichment check. | `normalize_linkedin(url)` = lowercase, drop scheme, drop `www.`/locale subdomain, drop query and trailing slash; compare normalized forms. |
| L12 | A person created with neither linkedin nor email is labelled Verified. The exact-name conflict check misses "Müller" vs "Mueller". | Created without a strong key → `identity_review_state = Pending` (proceeds, flagged in the digest as "identity unverified"). Conflict check on `normalize(full_name)`. |
| L13 | "If an open opportunity exists → update" — "open" is undefined; stages are human fields. | Open = route stage not in a closed set (read the stage options of `fund_stage`, `di_stage`, `gen_cap_stage`; agent reads, never writes). |
| L14 | CSV `company` is never persisted: the People create fields exclude it; the digest shows a company the CRM does not know. | 6.3 resolves the company (domain from search or LinkedIn), creates/matches the Company record per contract, sets `people.company`. |
| L15 | Quantum → AI, Deep Tech → Industrial Tech, Sustainability → ESG is a runtime mapping between two vocabularies. | Optional: keep one 14-value vocabulary on both sides and map at onboarding, not at routing time. |

## C — contradictions inside the prompt and skills

| # | A | B | Resolution |
|---|---|---|---|
| C1 | Section 4.3: `run_log` row per tool call | Cost mode: one summary row per step | One row per **write** (create/update), none per read, one summary row per run. |
| C2 | Section 2 / contract: read-back after every write | Cost mode: once per entry at step end | Batched read-back per entry is the protocol for 6.1–6.7. Per-write read-back only in 6.8 (business records). |
| C3 | 6.3: budget 5 calls | Cost mode: 4 calls | 4. Skip source 1 (existing notes) when the Person was created by this import. |
| C4 | Section 1: voice clips only from `#event-coverage` threads | 6.7: per-DRI channels | Per-DRI channels only. |
| C5 | 6.5: Slack summary as a table | Line 85: one line per attendee | Lines; Slack mrkdwn has no tables. |
| C6 | Contract: `ir_dri_people` read-only; eligibility "dri_code starts with Testperson" | Routing: `add dri` writes list entries; eligibility by `profile_status` and fields; new `dri_code` = "next free" = "Testperson 4" = an attendee's name | Allow `add-record-to-list` and `update-list-entry` on `ir_dri_people` for `dri_code`, `profile_status = Draft` only, `product_focus`, `vertical_expertise`, `coverage_capacity`, `profile_evidence`. Agent never writes Confirmed. New codes `DRI-004`, `DRI-005`, …; drop the "Testperson" filter. |
| C7 | Routing: any eligible DRI may approve | 6.8: "Approver: the assigned DRI" | The assigned DRI. Identical today only because channels are private; state it. |
| C8 | 6.7 (a): only thread replies under a stored `slack_thread_ts` | Observed: the voice clip was posted top-level | In a two-member private channel every DRI message is a debrief: accept top-level and thread. Event = the DRI's event with a Sent briefing and the nearest `event_start`; ask if more than one. Attendee = unique first/last-name hit anywhere in the first sentence (or anywhere in the text if exactly one attendee matches); otherwise ask once. |

## D — state that does not survive an account switch

| # | Finding | Fix |
|---|---|---|
| D1 | `attending_event`, `slack_channel`, `dri_assignments` live only in the agent DB. The agent DB was lost twice today. Manual-override detection (T8) diffs against that table. | Attio is the durable store. Add two attributes on `ir_dri_people` (UI, one minute): `slack_channel_id` (text), `attending_events` (multi record-ref → `ir_coverage_events`). Manual override: the human sets `dri_assignment_state = Confirmed` in Attio; the agent skips Confirmed entries. No DB diff. T8 changes to "set `assigned_dri` and state Confirmed". |
| D2 | Briefing trigger "event_start − 24 h in event_timezone" is not expressible as a per-record schedule. | Daily trigger 08:00 Europe/Berlin: select events with `event_start ∈ (now, now + 36 h]` and entries at DRI Assigned with `briefing_delivery_state ≠ Sent`. |
| D3 | Testperson 1 and Testperson 3 map to the same `workspace_member`, so `promotion_approved_by` cannot distinguish them. | Leave `promotion_approved_by` empty for Testperson 1 and record the Slack user ID in the note; or accept as a demo artefact and say so in the Loom. |

## Decisions required from Mara

1. B2: create the third Slack user (mara.sofi.pasenau@gmail.com) now, or let DI attendees fall back to Leonie/Tara for this run.
2. L4: route thin-evidence attendees to the attending DRI as an "Also attending" block, yes or no.
3. D1: add `slack_channel_id` and `attending_events` to `ir_dri_people` in the Attio UI, or keep that state in the agent DB and accept that it is lost on every account switch.
4. B3: case C (note only) ends at Closed, yes or no.

## Changes to apply after the decisions

- `ir-product-rules.md`: B1, L6, L7 (`rank_products`), run-date recency.
- `ir-dri-routing.md`: B2 eligibility, L1, L2, L3, L4, L5, C6 codes, C7, D1.
- `ir-debrief-extraction.md`: L7, L8, L9, C8.
- `ir-attio-contract.md`: B4 table, L10, L11, L12, L13, L14, C6 allowed writes on `ir_dri_people`, `responsible_workspace_member`, D1 fields.
- `agent-prompt.md`: B3 stage machine, B4 trigger dispatch, C1–C5, C8, D2, test updates (T3 end stage, T8, new T15 injection, T16 determinism: two runs of 6.5 on the same input produce identical `assigned_dri`).
