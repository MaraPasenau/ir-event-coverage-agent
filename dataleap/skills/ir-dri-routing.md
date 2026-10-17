---
name: IR DRI Routing
version: 2026-10-17.2
description: Eligibility, onboarding and deterministic rules R1–R4 for assigning a coverage DRI to an event attendee. Use in the DRI assignment step and for the approver check.
---

# IR DRI Routing

## Source of truth
Attio list `ir_dri_people` is authoritative. Read it at the start of every run and mirror eligible rows into agent DB table `dri_config` (`dri_code`, `display_name`, `person_record_id`, `product_focus`, `vertical_expertise`, `coverage_capacity`, `slack_user_id`, `slack_channel_id`, `workspace_member`, `relationship_people`, `attending_events`). The table below is a snapshot for the reader; never route from it.

| dri_code | display_name | product_focus | vertical_expertise | capacity | slack_user_id | slack_channel_id | eligible today |
|---|---|---|---|---|---|---|---|
| Testperson 1 | Mara | DI Angel Investment | Deep Tech, AI, Quantum, Defense | 10 | U0C9U823G8K | #targets-mara C0C9YDQ3HML | yes |
| Testperson 2 | Leonie | Fund | ESG, Sustainability, Energy, Climate | 10 | U0C9LBXNZSS | #targets-leonie C0CAUDMH80Y | yes |
| Testperson 3 | Tara | Gen Cap | Consumer | 10 | U0C9G3X7ZS7 | #targets-tara C0CA43FNPGC | yes |

`slack_channel_id`: read Attio attribute `slack_channel_id` on the list entry (populated for all three DRIs); only if empty, resolve the channel by name (`#targets-<firstname>`) and store the ID in `dri_config`. The DRI channels are **public** channels with two human-relevant members, the DRI and the Dataleap bot; the Dataleap Slack connection cannot read, post or trigger in private channels, so the former private `#coverage-*` channels (C0C9J6YJ2MD, C0C9TB8LKR9, C0CA1F1TV17) are retired and never used. Briefings, debriefs, transcripts and proposals go to `#targets-<firstname>`. `#event-coverage` (C0C9WQFS78A) carries the event summary only. Bot user: U0C9X4ZUJF4; messages authored by it are never treated as debriefs.

## Eligibility (one definition)
A row is eligible when all of: `profile_status = Confirmed`, `product_focus ≠ ∅`, `vertical_expertise ≠ ∅`, `slack_user_id ≠ ∅`. Draft and Inactive rows are never routed. A Confirmed row without `slack_user_id` is reported once per run in the summary ("<display_name>: no Slack ID, not routable") and skipped. No other Attio member or select code is ever used as a DRI.

## Onboarding a new DRI
1. Trigger: user command `add dri <Name>, <email>, <products>, <verticals>`, or a Person added to `ir_dri_people` by a human.
2. The agent resolves the Person by `email_addresses` (create if absent), adds the list entry with `profile_status = Draft`, `dri_code = DRI-<nnn>` (next free number ≥ 004; codes never reuse an attendee name), `product_focus`, `vertical_expertise`, `coverage_capacity = 10`, `profile_evidence = "added by <user> via agent, <date>"`. The agent never writes Confirmed or Inactive.
3. `slack_user_id`: look up the Slack user by email; write it if exactly one match. Channel: if the Slack tool can create a private channel, create the public channel `#targets-<firstname>`, invite the DRI, write the channel ID; otherwise post the missing items.
4. Missing fields after step 3 → one message in `#event-coverage`: "New DRI profile for <Name> is incomplete. Missing: <fields>. Set them in Attio and change the status to Confirmed."
5. A human sets `profile_status = Confirmed`. Eligible from the next run. `Inactive` removes a DRI from routing without deleting history.

`dri_code` is the internal key in Attio selects and routing. `display_name` (first name) is what appears in Slack and in notes; never show a code to a human. Emails are test delivery addresses, not identity proof; the agent never sends email.

## Verticals
Overlap is computed on the canonical set of `preferred_verticals`. Map `vertical_expertise` first: Deep Tech → Industrial Tech, Quantum → AI, Sustainability → ESG. `Other` and `Unknown` are removed from both sides before comparison and never count as a match.

## Attendance
Per event. Source: Attio attribute `attending_events` (multi record-ref on the `ir_dri_people` entry, populated); the user command `attending <event>: Mara, Tara` stored in `dri_config`. Default when neither is set: all eligible DRIs attend. A DRI not attending is skipped by every rule for that event.

## Capacity
Before each assignment: count the DRI's entries for this event at stages DRI Assigned or Pre-event Brief Ready, plus assignments made earlier in this run. If the count ≥ `coverage_capacity`, the DRI is not a candidate for this entry.

## Processing order
Entries are processed sorted by `proposed_overall_tier` (A, B, C, Needs Review) then `luma_attendee_id` ascending. Candidate lists are sorted by `dri_code`. Two runs on identical input must produce identical `assigned_dri` values.

## Candidates
For every rule, `candidates(entry)` = eligible DRIs that attend the event and have capacity. Tie-break inside a rule, in order: fewest assignments for this event so far → most vertical overlaps with the entry → `dri_code` ascending.

## Rules (first rule that yields a DRI wins)
- **R1 relationship**: candidates whose `relationship_people` contains the person.
- **R2 product**: for each product in `rank_products(relevant_products)` order: candidates whose `product_focus` contains that product. Stop at the first product with at least one candidate.
- **R3 vertical**: candidates with ≥ 1 overlap between mapped `vertical_expertise` and the entry's `preferred_verticals`.
- **R4 attendance**: all candidates (the attending DRI with the fewest assignments).
- **Escalated**: only if `candidates(entry)` is empty (no eligible DRI attends or all are at capacity): `dri_assignment_state = Escalated`, `candidate_dris` = all eligible DRIs, `assigned_dri` empty, `dri_assignment_reason = "R4 no attendee"`.

On assignment write `assigned_dri` (Person record of the DRI), `dri_assignment_state = Suggested`, `dri_assignment_reason` = `R1 relationship` | `R2 product <product>` | `R3 vertical <overlap list>` | `R4 attendance` | `R4 unrated`.

## Scope
- Entries with `proposed_overall_tier` ∈ {Tier A, Tier B, Tier C} run R1–R4.
- Entries with `proposed_overall_tier = Needs Review` and `identity_review_state ≠ Conflict` (insufficient evidence, not a conflict) run R4 only, reason `R4 unrated`. They appear in the briefing as the final block "Also attending, no evidence yet".
- `identity_review_state = Conflict` or `proposed_overall_tier = Irrelevant`: stage stays Ready for Review, `dri_assignment_state = Unassigned`.
- Never touch an entry whose `dri_assignment_state = Confirmed`. Humans set Confirmed in Attio when they override `assigned_dri`; that is the only override signal, no agent DB comparison.

## Approvers
A reaction counts as approval or rejection only when the reacting Slack user ID equals the `slack_user_id` of the entry's `assigned_dri`. Any other reaction is logged to `run_log` and ignored. In a two-member private channel this is equivalent to "any eligible DRI in the channel"; the rule is still stated per entry.
