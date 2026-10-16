---
name: IR Attio Contract
description: Attio workspace b2v schema and write rules for the Event Coverage Agent. Use before any Attio read or write.
---

# IR Attio Contract (workspace b2v, read 2026-10-16)

## Allowed Attio operations
search-records, get-records-by-ids, create-record, update-record, add-record-to-list, update-list-entry-by-record-id, update-list-entry-by-id, list-records-in-list, create-note, search-notes-by-metadata, get-note-body, create-task, list-tasks.
Not allowed: merge-records, any delete, writes to objects or lists not listed here.

## Events — object `ir_coverage_events`
One record per event. Fields: `name` (text), `integration_key` (text, unique), `luma_event_id` (text, unique), `luma_url` (text), `event_start`, `event_end` (timestamp), `event_timezone` (IANA text), `location` (text), `source_mode` (select: Organizer API, Approved Export, Manual Authorized), `access_state` (status: Verified, Pending, Denied), `source_completeness` (select: Complete, Partial, Unknown), `event_status` (status: Planned, Cancelled, Completed), `import_status` (status: Pending, Imported, Partial, Failed), `imported_at` (timestamp), `source_attendee_count` (number), `import_evidence` (text).
Lookup order: `integration_key`, `luma_event_id`, exact `name`.

## People (standard)
Match keys, in order: `linkedin`, then `email_addresses`. Name is never a match key.
Identity resolution runs before any create:
1. `linkedin` match → reuse, `identity_review_state = Verified`.
2. Else `email_addresses` match → reuse, Verified.
3. Else exact-name match with a different or empty `linkedin` → create a new record with `description = "UNVERIFIED — possible duplicate of <record_id>"`, `identity_review_state = Conflict`. Never merge. Conflict entries are not enriched, tiered or routed until a human resolves them.
4. Else create, Verified.
A `linkedin` hit and an `email_addresses` hit on two different records is also a Conflict (case 3).
Create with `name` {first_name, last_name, full_name}, `job_title`, `linkedin`, `email_addresses`, `description`.

## Companies (standard)
Create only when a Person needs a company reference and no match on `domains` or exact `name` exists.

## Event coverage list — slug `ir_event_coverage`, parent People
List ID 8ad90a24-81ed-41da-872b-e50241f13f2a. One shared list; one entry per person per event, linked via `coverage_event`.

| api_slug | type | values | written by |
|---|---|---|---|
| coverage_event | record-ref → ir_coverage_events | | 6.1 |
| luma_attendee_id | text | | 6.1 |
| coverage_stage | status | Imported → Enrichment Pending → Ready for Review → DRI Assigned → Pre-event Brief Ready → Conversation Logged → Routing Ready → Promoted → Closed | all steps, one stage at a time |
| identity_review_state | status | Pending, Verified, Conflict | 6.2 |
| enrichment_status | status | Pending, Complete, Partial, Failed | 6.3 |
| enriched_at | timestamp | | 6.3 |
| professional_summary | text | max 3 sentences | 6.3 |
| professional_interests | text | | 6.3 |
| investment_history_summary | text | | 6.3 |
| preferred_verticals | multi-select | AI, Biotech, Climate, Consumer, Defense, Energy, Enterprise Software, ESG, FinTech, Health, Industrial Tech, Space, Other, Unknown | 6.3 |
| evidence_urls | text | one URL per line | 6.3 |
| data_gaps | text | | 6.3, 6.4 |
| fund_fit_proposal, di_fit_proposal, gencap_fit_proposal | select | Tier A, Tier B, Tier C, Needs Review, Irrelevant | 6.4 |
| product_fit_reasons | text | one line per product: `product: criterion=supported|contradicted|unknown [source]` | 6.4 |
| relevant_products | multi-select | Fund, DI Angel Investment, Gen Cap | 6.4 |
| proposed_overall_tier | select | as fit proposals | 6.4 |
| conversation_talking_points | text | | 6.4 |
| assigned_dri | record-ref → People | parent record of an `ir_dri_people` entry | 6.5 |
| candidate_dris | multi record-ref → People | | 6.5 |
| dri_assignment_state | status | Unassigned, Suggested, Confirmed, Escalated | 6.5 |
| dri_assignment_reason | text | rule id | 6.5 |
| slack_channel_id, slack_thread_ts | text | | 6.6 |
| briefing_delivery_state | status | Not Sent, Queued, Sent, Delivery Unknown, Failed | 6.6 |
| post_event_note | text | raw debrief or confirmed transcript | 6.7 |
| post_event_source_message_id | text | Slack message ts | 6.7 |
| conversation_logged_at | timestamp | | 6.7 |
| conversation_outcome | status | No Conversation, No Fit, Nurture, Potential Investor, Interest Confirmed | 6.7 |
| ticket_size_indication | number | only with currency | 6.7 |
| ticket_currency_code | text | ISO 4217 | 6.7 |
| selected_product | select | Fund, DI Angel Investment, Gen Cap | 6.8 |
| promoted_opportunity | record-ref → ir_opportunities | | 6.8 |
| promoted_at | timestamp | | 6.8 |
| promotion_approved_by | actor-ref | | 6.8 |

Read-only for the agent: `confirmed_overall_tier`, `suppressed`, `outreach_permission`, `processing_basis`, `identity_reviewed_by`, `identity_reviewed_at`, `dri_assignment_by`, `profile_photo_url`, `profile_photo_source`, `profile_photo_use`.
If `suppressed = true`, skip the entry in 6.6 and 6.8.

## DRI profiles — list `ir_dri_people`, parent People (read-only)
Fields: `dri_code` (text), `profile_status` (status: Draft, Confirmed, Inactive), `product_focus` (multi-select: Fund, DI Angel Investment, Gen Cap), `vertical_expertise` (multi-select: AI, Biotech, Climate, Consumer, Defense, Energy, Enterprise Software, ESG, FinTech, Health, Industrial Tech, Space, Other, Unknown, Deep Tech, Quantum, Sustainability), `slack_team_id`, `slack_user_id` (text), `workspace_member` (actor-ref), `relationship_people` (multi record-ref → People), `backup_dri` (record-ref → People), `coverage_capacity` (number).
Eligible rows: `profile_status = Confirmed` and `dri_code` starts with "Testperson". All other rows are ignored.

## Investor entities — object `ir_investor_entities`
Required: `name`, `investor_type` (select: Entity, Angel Investor). Mapping: debrief `investing_context = organisation` → Entity; `personal` → Angel Investor; `unknown` → Angel Investor when the person is the investing party, else Entity, and record the assumption in `source_detail`.
On create also: `company_type` (Family Office, Fund Angel, VC Fund, PE Fund, Corporation, Foundation / Endowment, Pension Fund, Asset Manager, CVC, Bank, Insurance Company, Public Investment Company), `relevant_investment_types` (multi: Fund, DI Angel Investment, Gen Cap), `relationship_source = Event`, `integration_key`.
Do not write `responsible_dri` on this object in v1: its select has no Testperson options. The DRI is carried on the opportunity.
Lookup order: `integration_key`, exact `name`.

## Opportunities — object `ir_opportunities`
Required: `name`, `route` (Fund, DI Angel Investment, Gen Cap), `investor_entity` (record-ref, must exist).
On create also: `responsible_dri` (select, value = dri_code), `conversation_contacts` (multi record-ref → People), `source_note`, `integration_key`; `expected_commitment_min`, `expected_commitment_max`, `currency_code` only when all three are stated.
Never write: `fund_stage`, `di_stage`, `gen_cap_stage`, `closing_probability`, `final_commitment_amount`.
Display lists, no direct writes: `ir_fund_opportunities`, `ir_di_opportunities`, `ir_gen_cap_opportunities`.

## Notes (standard)
`create-note` on the Person record, one per debrief. Title: `Event debrief — <event name> — <YYYY-MM-DD> — <source message ts>`; the ts makes two debriefs on one day distinct. Body: the fields in IR Debrief Extraction, section "Conversation note". Lookup before create: list the Person's notes (default page size, paginate until exhausted) and match the title locally; if present, skip. There is no dedicated title-search operation.

## Approval attribution
`promotion_approved_by` is an Attio actor reference. Resolve it from the approving Slack user: `dri_config.slack_user_id` → that DRI's `workspace_member`. If the DRI has no `workspace_member`, leave `promotion_approved_by` empty and record the Slack user ID in the note body and in `run_log`. Current mapping: Testperson 3 (U0C9G3X7ZS7) → workspace member 3eb34deb-14a7-4096-bd23-4ccc5e29a231; Testperson 1 → same member; Testperson 2 → none.

## Multi-product promotion
`selected_product` and `promoted_opportunity` are single-valued. When one debrief creates more than one opportunity: `selected_product` = the product with the strongest supported signals; `promoted_opportunity` = that product's opportunity; all opportunity record IDs are stored in the `proposals` row and listed in the Slack confirmation.

## Tasks (standard)
`create-task` with `content`, `deadline_at`, `linked_records` = the opportunity when one exists, else the Person, `assignees` = DRI `workspace_member` if set, else unassigned. Lookup before create: `list-tasks` on the linked record with identical `content`; if present, skip.

## Idempotency keys
- Event: `integration_key = "ir:event:" + sha1(lower(luma_url or name))`
- Coverage entry: `(event_record_id, person_record_id)`
- Investor entity: `integration_key = "ir:investor:" + sha1(lower(name))`
- Opportunity: `integration_key = "ir:opp:" + investor_entity_record_id + ":" + route`
- Briefing: `(coverage_entry_id, "briefing")`; never resend when `briefing_delivery_state = Sent`
- Proposal: `proposal_id = sha1(coverage_entry_id + post_event_source_message_id + serialized_changes)`

## Write protocol (every create or update)
1. Write intent `{key, target, payload}` to `run_log` with status `pending`.
2. Execute.
3. `get-records-by-ids`, compare written fields.
4. Set status `verified` or `mismatch`.
After a timeout or ambiguous response: search by idempotency key first; create only if absent. Retries: max 2, backoff 2 s then 8 s; never retry a create after an ambiguous response.
