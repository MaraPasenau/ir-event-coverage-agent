# Attio workspace `b2v` — schema snapshot, 2026-10-16

Read via the Attio MCP tools. Reference only; the authoritative contract is `dataleap/skills/ir-attio-contract.md`.

## Objects
- `people`, `companies` (standard)
- `ir_coverage_events` — events (see contract 2.1)
- `ir_investor_entities` — required: `name`, `investor_type` (Entity / Angel Investor)
- `ir_opportunities` — required: `name`, `route`, `investor_entity`; stages per route are manual
- `ir_investment_vehicles`, `ir_fund_briefs`, `ir_fund_matches`, `ir_events`, `ir_actions` — present, out of scope for v1

## Lists
| name | slug | parent | use |
|---|---|---|---|
| Event Coverage | `ir_event_coverage` (ID 8ad90a24-81ed-41da-872b-e50241f13f2a) | people | the working list, ~90 attributes |
| DRI Profiles | `ir_dri_people` | people | 3 eligible rows (Testperson 1–3) + 1 ignored (IR) |
| Events | `ir_event_directory` | ir_coverage_events | empty; views only |
| DI / Fund / Gen Cap Opportunities | `ir_di_opportunities`, `ir_fund_opportunities`, `ir_gen_cap_opportunities` | ir_opportunities | display |
| Berlin Capital Signals 2026 [Synthetic] · DRI Attendance | `ir_attendance_f0bc91082f96416e` | people | unused in v1 |
| Weekly IR Meeting, Opportunity Matching, Existing Investors, New Opportunities, Startup Fundraising | various | various | out of scope |

## DRI profile rows (ir_dri_people)
| dri_code | product_focus | vertical_expertise | slack_user_id | workspace_member | capacity |
|---|---|---|---|---|---|
| Testperson 1 | DI Angel Investment | Deep Tech, AI, Quantum, Defense | — | 3eb34deb-… | 10 |
| Testperson 2 | Fund | ESG, Sustainability, Energy, Climate | U0C9LBXNZSS | — | 10 |
| Testperson 3 | Gen Cap | Consumer | U0C9G3X7ZS7 | 3eb34deb-… | 10 |

## Select options that still contain real team codes (not used by the agent)
`ir_investor_entities.responsible_dri`, `supporting_contact_owners`, `known_by_strongest_connection`, and `ir_opportunities.responsible_dri` carry codes FS, FH, MO, AB, SLS, JHB, AG, FK, CS, GJ, PC, IR. Consider archiving before recording the Loom.

## Known limitation
Attio truncates timestamps to millisecond precision on write; submit ms-precision values.
