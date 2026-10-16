---
name: IR DRI Routing
description: Rules for assigning a coverage DRI to an event attendee. Use in the DRI assignment step.
---

# IR DRI Routing

## Eligible DRIs
Read list `ir_dri_people` at the start of every run and mirror eligible rows into agent DB table `dri_config`. A row is eligible when `profile_status = Confirmed` and `dri_code` starts with "Testperson". Current rows:

| dri_code | product_focus | vertical_expertise | coverage_capacity | slack_user_id |
|---|---|---|---|---|
| Testperson 1 | DI Angel Investment | Deep Tech, AI, Quantum, Defense | 10 | — (workspace_member set) |
| Testperson 2 | Fund | ESG, Sustainability, Energy, Climate | 10 | U0C9LBXNZSS |
| Testperson 3 | Gen Cap | Consumer | 10 | U0C9G3X7ZS7 |

Vertical mapping for comparison with `preferred_verticals`: Deep Tech → Industrial Tech, Quantum → AI, Sustainability → ESG.

## Attendance
`dri_config` carries `attending_event` per event, set by the user command `attending <event>: Testperson 1, Testperson 3`. Default when not set: all eligible DRIs attend. A DRI not attending the event is skipped by R1–R3 for that event.

## Tie-break for "product with the highest tier"
If two products share the highest tier, take the one with more `supported` criteria; if still tied, apply the precedence Gen Cap > DI Angel Investment > Fund (configurable here).

## Rules (first rule that fires wins)
- R1 relationship: an eligible DRI whose `relationship_people` contains the person → that DRI
- R2 product: the eligible DRI whose `product_focus` contains the product with the highest tier
- R3 vertical: an eligible DRI with ≥ 1 overlap between mapped `vertical_expertise` and `preferred_verticals`; on a tie set `Escalated` with both in `candidate_dris`
- R4 none: `dri_assignment_state = Escalated`, `candidate_dris` = all eligible DRIs, `assigned_dri` empty

Capacity check before any assignment: count the DRI's entries for this event at stages `DRI Assigned` and `Pre-event Brief Ready`. If the count equals `coverage_capacity`, fall through to the next rule.

## Scope
- Only entries with `proposed_overall_tier` in {Tier A, Tier B, Tier C} are routed.
- Needs Review and Irrelevant stay at `Ready for Review` with `dri_assignment_state = Unassigned`.
- Never overwrite `dri_assignment_state = Confirmed`. Detect a manual change by comparing the current `assigned_dri` in Attio with the value stored in agent DB table `dri_assignments` from the last run; if they differ and the Attio value is an eligible DRI, set `dri_assignment_state = Confirmed`, store the new value, and do not re-route.

## Approvers
A Slack reaction counts as an approval or rejection only when the reacting user's ID equals the `slack_user_id` of an eligible DRI in `dri_config`. Reactions from any other user are logged to `run_log` and ignored.
- Write the rule id (R1–R4) into `dri_assignment_reason`.
