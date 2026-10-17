---
name: IR DRI Routing
description: Rules for assigning a coverage DRI to an event attendee. Use in the DRI assignment step.
---

# IR DRI Routing

## Eligible DRIs
Read list `ir_dri_people` at the start of every run and mirror eligible rows into agent DB table `dri_config`. A row is eligible when `profile_status = Confirmed`, `product_focus` has at least one value and `vertical_expertise` has at least one value. Rows at Draft or Inactive are never routed. Only the people in this list can be DRIs; no other Attio member or select code is ever used. Current rows:

| dri_code | display_name | product_focus | vertical_expertise | capacity | slack_user_id | slack_channel | email |
|---|---|---|---|---|---|---|---|
| Testperson 1 | Mara | DI Angel Investment | Deep Tech, AI, Quantum, Defense | 10 | not yet mapped | #coverage-mara C0C9J6YJ2MD | mara.sofi.pasenau@gmail.com |
| Testperson 2 | Leonie | Fund | ESG, Sustainability, Energy, Climate | 10 | U0C9LBXNZSS | #coverage-leonie C0C9TB8LKR9 | m.pasenau@icloud.com |
| Testperson 3 | Tara | Gen Cap | Consumer | 10 | U0C9G3X7ZS7 | #coverage-tara C0CA1F1TV17 | mara.pasenau@b2venture.vc |

Each DRI has a private channel with only the DRI and the Dataleap bot. Briefings and debriefs happen there. #event-coverage (C0C9WQFS78A) is the team overview: event summary only, no individual briefings.

## Onboarding a new DRI
1. The user says `add dri <Name>, <email>, <products>, <verticals>` or a Person is added to `ir_dri_people` manually.
2. The agent creates or finds the Person, adds the list entry with `profile_status = Draft`, the next free `dri_code`, `product_focus`, `vertical_expertise`, `coverage_capacity = 10`, and `profile_evidence` = who requested it and when.
3. If any of product_focus, vertical_expertise or slack_user_id is missing, the agent posts once in #event-coverage: "New DRI profile for <Name> is incomplete. Missing: <fields>. Set them in Attio and change the status to Confirmed." and does not route to that DRI.
4. A human sets `profile_status = Confirmed`. From the next run the DRI is eligible.
5. `profile_status = Inactive` removes a DRI from routing without deleting history.

dri_code is the internal key used in Attio selects and routing. display_name is what appears in Slack and in Attio notes; never show a Testperson code to a human. Emails are test delivery addresses, not identity proof; the agent never sends email.

Vertical mapping for comparison with `preferred_verticals`: Deep Tech → Industrial Tech, Quantum → AI, Sustainability → ESG.

## Attendance
`dri_config` carries `attending_event` per event, set by the user command `attending <event>: Mara, Tara`. Default when not set: all eligible DRIs attend. Everyone at an event who reaches Tier A/B/C gets a DRI; R4 guarantees that as long as one DRI attends. A DRI not attending the event is skipped by R1–R3 for that event.

## Tie-break for "product with the highest tier"
If two products share the highest tier, take the one with more `supported` criteria; if still tied, apply the precedence Gen Cap > DI Angel Investment > Fund (configurable here).

## Rules (first rule that fires wins)
- R1 relationship: an eligible DRI whose `relationship_people` contains the person → that DRI
- R2 product: the eligible DRI whose `product_focus` contains the product with the highest tier
- R3 vertical: an eligible DRI with ≥ 1 overlap between mapped `vertical_expertise` and `preferred_verticals`; on a tie set `Escalated` with both in `candidate_dris`
- R4 attendance: no product or vertical match → the eligible DRI who is attending the event and has the fewest assignments for this event so far; on a tie, the one listed first. `dri_assignment_reason = R4 attendance`. Only if no eligible DRI is attending: `dri_assignment_state = Escalated`, `candidate_dris` = all eligible DRIs, `assigned_dri` empty, reason `R4 no attendee`.

Capacity check before any assignment: count the DRI's entries for this event at stages `DRI Assigned` and `Pre-event Brief Ready`. If the count equals `coverage_capacity`, fall through to the next rule.

## Scope
- Only entries with `proposed_overall_tier` in {Tier A, Tier B, Tier C} are routed.
- Needs Review and Irrelevant stay at `Ready for Review` with `dri_assignment_state = Unassigned`.
- Never overwrite `dri_assignment_state = Confirmed`. Detect a manual change by comparing the current `assigned_dri` in Attio with the value stored in agent DB table `dri_assignments` from the last run; if they differ and the Attio value is an eligible DRI, set `dri_assignment_state = Confirmed`, store the new value, and do not re-route.

## Approvers
A Slack reaction counts as an approval or rejection only when the reacting user's ID equals the `slack_user_id` of an eligible DRI in `dri_config`. Reactions from any other user are logged to `run_log` and ignored.
- Write the rule id (R1–R4) into `dri_assignment_reason`.
