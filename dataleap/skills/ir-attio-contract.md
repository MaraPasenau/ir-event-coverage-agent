---
name: IR Attio Contract
version: 2026-10-17.3
description: Attio workspace b2v schema, normalization functions, idempotency keys, agent DB tables and write protocol for the Event Coverage Agent. Use before any Attio read or write.
---

# IR Attio Contract (workspace b2v, schema read 2026-10-16)

## Allowed Attio operations
search-records, get-records-by-ids, create-record, update-record, add-record-to-list, update-list-entry-by-record-id, update-list-entry-by-id, list-records-in-list, create-note, search-notes-by-metadata, get-note-body, create-task, update-task (mark follow-up tasks complete only), list-tasks, list-attribute-definitions (read only, to resolve select option IDs and stage sets).
Not allowed: merge-records, any delete, writes to objects or lists not listed here.

## Normalization functions (used by every match and key)
- `normalize(text)`: Unicode NFKD, strip combining marks (Müller → Muller), casefold, collapse whitespace, trim. For organisation names additionally drop a trailing legal form from {GmbH, AG, SE, KG, KGaA, Ltd, LLC, Inc, Corp, SA, SAS, BV, AB, Oy}.
- `normalize_linkedin(url)`: lowercase; drop scheme; drop a leading `www.` or two-letter locale subdomain (`de.`, `fr.`); drop query string, fragment and trailing slash. Result shape `linkedin.com/in/<slug>`.
- `normalize_email(e)`: casefold, trim.
All comparisons below are on normalized values.

## Events — object `ir_coverage_events`
One record per event. Fields: `name` (text), `integration_key` (text, unique), `luma_event_id` (text, unique), `luma_url` (text), `event_start`, `event_end` (timestamp), `event_timezone` (IANA text), `location` (text), `source_mode` (select: Organizer API, Approved Export, Manual Authorized), `access_state` (status: Verified, Pending, Denied), `source_completeness` (select: Complete, Partial, Unknown), `event_status` (status: Planned, Cancelled, Completed), `import_status` (status: Pending, Imported, Partial, Failed), `imported_at` (timestamp), `source_attendee_count` (number), `import_evidence` (text).
Lookup order: `integration_key`, `luma_event_id`, `normalize(name)` + same `event_start` date.

## People (standard)
Strong match keys, in order: `normalize_linkedin(linkedin)`, then `normalize_email(email_addresses)`. Name is never a match key.
Identity resolution runs before any create:
1. linkedin match → reuse, `identity_review_state = Verified`.
2. Else email match → reuse, Verified.
3. Else `normalize(full_name)` equals an existing Person whose linkedin is different or empty → create a new record with `description = "UNVERIFIED — possible duplicate of <record_id>"`, `identity_review_state = Conflict`. Never merge. Conflict entries are not enriched, tiered or routed until a human resolves them.
4. Else create. `identity_review_state = Verified` if the row carried a linkedin or email; `Pending` if it carried neither. Pending proceeds like Verified and is marked "identity unverified" in the briefing.
A linkedin hit and an email hit on two different records is also a Conflict (case 3).
Create with `name` {first_name, last_name, full_name}, `job_title`, `linkedin`, `email_addresses`, `description`. `company` is set in 6.3 (below).

## Companies (standard)
6.3 resolves the attendee's organisation: match on `domains` (from the web search or LinkedIn result), else `normalize(name)`; create if absent with `name` and `domains`; set `people.company` on the Person. One company per Person; never overwrite an existing `company` reference.

## Event coverage list — slug `ir_event_coverage`, parent People
List ID 8ad90a24-81ed-41da-872b-e50241f13f2a. One shared list; one entry per person per event, linked via `coverage_event`.

| api_slug | type | values | written by |
|---|---|---|---|
| coverage_event | record-ref → ir_coverage_events | | 6.1 |
| luma_attendee_id | text | | 6.1 |
| coverage_stage | status | Imported → Enrichment Pending → Ready for Review → DRI Assigned → Pre-event Brief Ready → Conversation Logged → Routing Ready → Promoted → Closed | see Stage machine |
| identity_review_state | status | Pending, Verified, Conflict | 6.1 |
| enrichment_status | status | Pending, Complete, Partial, Failed | 6.3 |
| enriched_at | timestamp | | 6.3 |
| professional_summary | text | max 3 sentences | 6.3 |
| professional_interests | text | investment focus per 6.3 definition; shown in the briefing as Interests | 6.3 |
| investment_history_summary | text | | 6.3 |
| preferred_verticals | multi-select | AI, Biotech, Climate, Consumer, Defense, Energy, Enterprise Software, ESG, FinTech, Health, Industrial Tech, Space, Other, Unknown | 6.3 |
| evidence_urls | text | one URL per line | 6.3 |
| data_gaps | text | | 6.2, 6.3, 6.4 |
| fund_fit_proposal, di_fit_proposal, gencap_fit_proposal | select | Tier A, Tier B, Tier C, Needs Review, Irrelevant | 6.4 |
| product_fit_reasons | text | line 1 `rules_version`, then one line per product | 6.4 |
| relevant_products | multi-select | Fund, DI Angel Investment, Gen Cap | 6.4 |
| proposed_overall_tier | select | as fit proposals | 6.4 |
| conversation_talking_points | text | | 6.4 |
| assigned_dri | record-ref → People | parent record of an `ir_dri_people` entry | 6.5 |
| candidate_dris | multi record-ref → People | | 6.5 |
| dri_assignment_state | status | Unassigned, Suggested, Confirmed, Escalated | 6.5 (never writes Confirmed) |
| dri_assignment_reason | text | rule id + detail | 6.5 |
| slack_channel_id, slack_thread_ts | text | | 6.6 |
| briefing_delivery_state | status | Not Sent, Queued, Sent, Delivery Unknown, Failed | 6.6 |
| post_event_note | text | raw debrief or confirmed transcript | 6.7 |
| post_event_source_message_id | text | Slack message ts | 6.7 |
| conversation_logged_at | timestamp | | 6.7 |
| conversation_outcome | status | No Conversation, No Fit, Nurture, Potential Investor, Interest Confirmed | 6.7 |
| ticket_size_indication | number | only with currency | 6.8 |
| ticket_currency_code | text | ISO 4217 | 6.8 |
| selected_product | select | Fund, DI Angel Investment, Gen Cap | 6.8 |
| promoted_opportunity | record-ref → ir_opportunities | | 6.8 |
| promoted_at | timestamp | | 6.8 |
| promotion_approved_by | actor-ref | | 6.8 |

Profile photos: the agent never writes `profile_photo_url`, `profile_photo_source`, `profile_photo_use` or any image URL to Attio; a picture URL from LinkedIn enrichment is used only inside a Slack briefing and stored only in `evidence_records` (topic photo).
Read-only for the agent: `confirmed_overall_tier`, `suppressed`, `outreach_permission`, `processing_basis`, `identity_reviewed_by`, `identity_reviewed_at`, `dri_assignment_by`, `profile_photo_url`, `profile_photo_source`, `profile_photo_use`.
If `suppressed = true`, skip the entry in 6.6 and 6.8. If `dri_assignment_state = Confirmed`, skip the entry in 6.5.

## Stage machine
Each step has exactly one precondition stage and writes exactly one successor. Guards that are not stages are listed explicitly.

| step | precondition | guard | success → |
|---|---|---|---|
| 6.1 import | — | entry absent | Imported |
| 6.2 identity | Imported | `identity_review_state ≠ Conflict` | Enrichment Pending |
| 6.3 research | Enrichment Pending | | Ready for Review |
| 6.4 fit and tier | Ready for Review | `proposed_overall_tier` empty | Ready for Review (no stage change; the guard prevents re-runs) |
| 6.5 routing | Ready for Review | `proposed_overall_tier` set, state ≠ Confirmed | DRI Assigned (routed) / stays (Conflict, Irrelevant) |
| 6.6 briefing | DRI Assigned | `briefing_delivery_state ≠ Sent` | Pre-event Brief Ready |
| 6.7 debrief | Pre-event Brief Ready | confirmed text present | Conversation Logged |
| 6.8a proposal posted | Conversation Logged | proposals.status = draft | Routing Ready (cases A, B) / Closed (case C) |
| 6.8b approved | Routing Ready | 👍 by assigned DRI | Promoted |
| 6.8b rejected | Routing Ready | 👎 by assigned DRI | Routing Ready (proposals.status = rejected) |
| later debriefs | Routing Ready or Promoted | | stage unchanged; progress lives in `proposals.status` |

On failure the stage stays unchanged and the error goes to `run_log`.

## DRI profiles — list `ir_dri_people`, parent People
Fields: `dri_code` (text), `profile_status` (status: Draft, Confirmed, Inactive), `product_focus` (multi-select: Fund, DI Angel Investment, Gen Cap), `vertical_expertise` (multi-select: the 14 coverage verticals + Deep Tech, Quantum, Sustainability), `slack_team_id`, `slack_user_id` (text), `workspace_member` (actor-ref), `relationship_people` (multi record-ref → People), `backup_dri` (record-ref → People), `coverage_capacity` (number), `profile_evidence` (text), `last_confirmed_at` (timestamp), plus `languages`, `geography_expertise`, `stage_expertise`, `conflict_policy`, `minimum_ticket`, `maximum_ticket` (unused in v1).
`slack_channel_id` (text) and `attending_events` (multi record-ref → ir_coverage_events) exist since 2026-10-17 and are populated for Testperson 1–3; they are the source for channel and attendance. The `dri_config` fallback applies only if a row has them empty.
Agent writes (onboarding only): `add-record-to-list`, `update-list-entry-by-id` for `dri_code`, `profile_status = Draft`, `product_focus`, `vertical_expertise`, `coverage_capacity`, `profile_evidence`, `slack_user_id`, `slack_channel_id`. The agent never writes Confirmed, Inactive, `workspace_member` or `relationship_people`.
Eligibility is defined in IR DRI Routing only.

## Investor entities — object `ir_investor_entities`
Required: `name`, `investor_type` (select: Entity, Angel Investor). Mapping: debrief `investing_context = organisation` → Entity; `personal` → Angel Investor; `unknown` → Angel Investor when the person is the investing party, else Entity, and record the assumption in `source_detail`.
On create also: `company_type` (Family Office, Fund Angel, VC Fund, PE Fund, Corporation, Foundation / Endowment, Pension Fund, Asset Manager, CVC, Bank, Insurance Company, Public Investment Company), `relevant_investment_types` (multi: Fund, DI Angel Investment, Gen Cap), `relationship_source = Event`, `integration_key`.
Do not write `responsible_dri` on this object in v1: its select has no Testperson options. The DRI is carried on the opportunity.
Lookup order: `integration_key`, then `normalize(name)`.

## Opportunities — object `ir_opportunities`
Required: `name`, `route` (Fund, DI Angel Investment, Gen Cap), `investor_entity` (record-ref, must exist).
On create also: `responsible_dri` (select, value = dri_code; options Testperson 1–3 verified 2026-10-16), `responsible_workspace_member` (actor-ref = the DRI's `workspace_member`, when set), `conversation_contacts` (multi record-ref → People), `source_note`, `integration_key`; `expected_commitment_min`, `expected_commitment_max`, `currency_code` only when all three are stated.
Never write: `fund_stage`, `di_stage`, `gen_cap_stage`, `closing_probability`, `final_commitment_amount`.
"Open opportunity" = an opportunity whose route stage is not in that route's closed set. Read the stage options once per run via list-attribute-definitions; closed = any option whose title starts with "Closed", "Lost", "Declined" or "Won". The agent reads stages, never writes them.
Display lists, no direct writes: `ir_fund_opportunities`, `ir_di_opportunities`, `ir_gen_cap_opportunities`.

## Notes (standard)
`create-note` on the Person record, one per debrief. Title: `Event debrief — <event name> — <YYYY-MM-DD> — <source message ts>`; the ts makes two debriefs on one day distinct. Body: the fields in IR Debrief Extraction, section "Conversation note". Lookup before create: list the Person's notes with limit 50 (Attio rejects larger pages), paginate until exhausted, match the title locally; if present, skip.

## Tasks (standard)
`create-task` and `update-task` (completion only, for follow-up tasks) with `content`, `deadline_at`, `linked_records` = the opportunity when one exists, else the Person, `assignees` = DRI `workspace_member` if set, else unassigned. Lookup before create: `list-tasks` on the linked record with identical `content`; if present, skip.

## Approval attribution
`promotion_approved_by` is an actor reference. Resolve from the approving Slack user: `dri_config.slack_user_id` → that DRI's `workspace_member`. Testperson 1 and Testperson 3 currently map to the same workspace member (3eb34deb-14a7-4096-bd23-4ccc5e29a231); to keep attribution unambiguous, write `promotion_approved_by` only for Testperson 3, and for every approval record the Slack user ID in the note body and in `run_log`. Testperson 2 has no workspace member: leave empty.

## Multi-product promotion
`selected_product` and `promoted_opportunity` are single-valued. When one debrief creates more than one opportunity: `selected_product` = `rank_products(interested products)[0]`; `promoted_opportunity` = that product's opportunity; all opportunity record IDs are stored in the `proposals` row and listed in the Slack confirmation.

## Idempotency keys
- Event: `integration_key = "ir:event:" + (luma_event_id if present else sha1(normalize(name) + "|" + event_start date YYYY-MM-DD))`
- Coverage entry: `(event_record_id, person_record_id)`
- Investor entity, personal (`investor_type = Angel Investor`): `"ir:investor:person:" + person_record_id`
- Investor entity, organisation: `"ir:investor:org:" + (primary domain if known else sha1(normalize(name)))`
- Opportunity: `"ir:opp:" + investor_entity_record_id + ":" + route`
- Briefing: `(coverage_entry_id, "briefing")`; never resend when `briefing_delivery_state = Sent`
- Proposal: `proposal_id = sha1(coverage_entry_id + "|" + source_message_ts + "|" + canonical_json(changes))` where `canonical_json` = sorted keys, no whitespace, UTF-8
- Slack post: `(kind, coverage_entry_id or proposal_id)`; a post is made only if no `slack_messages` row with that key exists

## Agent DB tables
- `evidence_records(id, coverage_entry_id, claim, topic, source_url, source_tag, source_date, collected_at)`
- `proposals` (schema in IR Debrief Extraction)
- `slack_messages(ts, channel_id, kind ∈ {briefing, summary, transcript, proposal, confirmation, question, followup, test}, coverage_entry_id, proposal_id, dri_code, posted_at)` — every message the agent posts gets a row **before** anything else happens. The reaction trigger resolves `ts → kind` here; unknown ts → no-op.
- `run_log(run_id, step, entry_id, key, target, payload_hash, status ∈ {pending, verified, mismatch, failed, ignored}, detail, latency_ms, created_at)`
- `dri_config` (mirror of `ir_dri_people`, rebuilt every run) and one settings row `followup_send_mode` ∈ {draft, send_on_explicit}, default draft
- `runs(run_id, trigger, event_record_id, coverage_entry_id, step, status ∈ {in_progress, done, failed, skipped}, started_at, finished_at, entries_processed, writes_verified, failures, cost_usd)` — `step` and `status` are updated before every step (checkpoint); a new run on the same coverage entry first looks for a run with status in_progress and resumes at its `step` instead of starting over.
- `slack_events(ts, channel_id, kind, processed_at, run_id)` — every incoming Slack event (message or reaction) is inserted here before any work; a duplicate (same ts + channel) ends the run with `skipped: duplicate event`. Exactly-once per event.
- `locks(coverage_entry_id, run_id, acquired_at)` — acquired before the first write for an entry, TTL 10 minutes; if held by another live run → `skipped: locked`, the event stays in slack_events unprocessed and is retried by the next event or the `retry dead letters` command. Released at run end.
- `settings(key, value)` — `followup_send_mode` (draft), `budget_daily_usd` (25), `photo_in_digest` (true).
Budget guard: before any write, sum `runs.cost_usd` for today (Europe/Berlin); if ≥ `budget_daily_usd`, make no writes, post one line in the DRI channel ("Paused for today, Mara knows."), one line to the operator, and end the run with `skipped: budget`.

## Write protocol
1. Before a create or update: `run_log` row `{key, target, payload_hash}` status `pending`.
2. Execute.
3. Read-back. Steps 6.1–6.7: once per coverage entry at the end of the step, all fields written in that step (`get-records-by-ids` / list entry read). Step 6.8 and every write to `ir_investor_entities`, `ir_opportunities`, notes and tasks: read-back immediately after each write.
4. Set `verified` or `mismatch`. A mismatch on a timestamp caused by Attio's millisecond truncation, or a blank text read back as `[]`, is reconciled as `verified` with `detail`; no replay.
5. After a timeout or ambiguous response: look up by idempotency key first; create only if absent. Retries: max 2 with backoff 2 s then 8 s plus random jitter 0–1 s; on HTTP 429 honour Retry-After; never retry a create after an ambiguous response.
6. A failed item that still fails after retries goes to `run_log` with status `failed` and is listed in the run summary under "Dead letters"; the user command `retry dead letters` re-runs them through the same protocol.
Reads are not logged individually. One `runs` row per run.
